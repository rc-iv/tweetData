import csv
from datetime import datetime, timedelta
from tweet import Tweet
import os
from pprint import pprint
import boto3
import decimal

TABLE_NAME = 'TweetData'

class TweetHistory:
    def __init__(self, user, session):
        self.session = session
        self.bearer = None
        self.get_bearer_token()

        self.user = user
        self.user_id = None
        self.get_user_id()

        self.average_impressions = None
        self.average_retweets = None
        self.average_replies = None
        self.average_likes = None
        self.average_quotes = None
        self.total_posts = None
        self.first_post = None
        self.last_post = None
        self.posts_per_day = None

        self.tweet_list = []

        if not self.get_from_db():
            print('no records found in db, getting tweets from twitter')
            self.get_tweets_for_user()
            self.calculate_stats()
            self.write_to_db()
        else:
            print('found the records')

    def calculate_stats(self):
        self.average_impressions = self.calculate_average_impressions()
        self.average_retweets = sum([tweet.retweet_count for tweet in self.tweet_list]) / len(self.tweet_list)
        self.average_replies = sum([tweet.reply_count for tweet in self.tweet_list]) / len(self.tweet_list)
        self.average_likes = sum([tweet.like_count for tweet in self.tweet_list]) / len(self.tweet_list)
        self.average_quotes = sum([tweet.quote_count for tweet in self.tweet_list]) / len(self.tweet_list)
        self.total_posts = len(self.tweet_list)
        self.first_post = None
        self.last_post = None
        self.find_oldest_tweet()
        self.find_newest_tweet()
        self.posts_per_day = self.total_posts / (self.last_post - self.first_post).days
    def write_to_csv(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.tweet_list[0].keys())
            for tweet in self.tweet_list:
                # remove newlines from tweet['text']
                writer.writerow(tweet.values())

    def sort_by_impressions(self):
        self.tweet_list.sort(key=lambda x: x.impressions, reverse=True)

    def sort_by_date(self):
        self.tweet_list.sort(key=lambda x: x.created, reverse=True)

    def calculate_average_impressions(self):
        # only count impressions for tweets with impressions > 0
        impressions = [tweet.impressions for tweet in self.tweet_list if tweet.impressions > 0]
        return sum(impressions) / len(impressions)

    def print_summary(self):
        print(f'TWEET DATA FOR {self.user}')
        print(f'Total Posts: {self.total_posts}')
        print(f'First Post: {self.first_post}')
        print(f'Last Post: {self.last_post}')
        print(f'Posts Per Day: {self.posts_per_day}')
        print(f'Average Impressions: {self.average_impressions} (since public impressions started)')
        print(f'Average Retweets: {self.average_retweets}')
        print(f'Average Replies: {self.average_replies}')
        print(f'Average Likes: {self.average_likes}')
        print(f'Average Quotes: {self.average_quotes}')


    def get_summary(self):
        return {
            'user': self.user,
            'total_posts': str(self.total_posts),
            'first_post': self.first_post.strftime('%Y-%m-%d'),
            'last_post': self.last_post.strftime('%Y-%m-%d'),
            'posts_per_day': str(self.posts_per_day),
            'average_impressions': str(self.average_impressions),
            'average_retweets': str(self.average_retweets),
            'average_replies': str(self.average_replies),
            'average_likes': str(self.average_likes),
            'average_quotes': str(self.average_quotes),
        }
    def print_top_tweets(self):
        self.sort_by_impressions()
        print(f'TOP TWEETS FOR {self.user}')
        print('Date -- Impressions -- Retweets -- Replies -- Likes -- Quotes -- Text -- URL')
        for tweet in self.tweet_list[:10]:
            print(
                f'{tweet.created.date()} - {tweet.impressions} - {tweet.retweet_count} - '
                f'{tweet.reply_count} - {tweet.like_count} - {tweet.quote_count} - {tweet.text} - {tweet.url}')

    def find_oldest_tweet(self):
        oldest_date = datetime.today()
        for tweet in self.tweet_list:
            if tweet.created < oldest_date:
                oldest_date = tweet.created
        self.first_post = oldest_date

    def find_newest_tweet(self):
        newest_date = datetime(1970, 1, 1)
        for tweet in self.tweet_list:
            if tweet.created > newest_date:
                newest_date = tweet.created
        self.last_post = newest_date

    def to_json(self):
        statistics = {
            'user': self.user,
            'total_posts': str(self.total_posts),
            'first_post': self.first_post.strftime('%Y-%m-%d'),
            'last_post': self.last_post.strftime('%Y-%m-%d'),
            'posts_per_day': str(self.posts_per_day),
            'average_impressions': str(self.average_impressions),
            'average_retweets': str(self.average_retweets),
            'average_replies': str(self.average_replies),
            'average_likes': str(self.average_likes),
            'average_quotes': str(self.average_quotes)
        }
        json = {
            'user_id': self.user_id,
            'tweet_id': 'metadata',
            'statistics': statistics,
            'tweets': [tweet.id for tweet in self.tweet_list]
        }
        return json

    def get_user_id(self):
        response = self.session.get(
            f"https://api.twitter.com/2/users/by/username/{self.user}",
            headers={"Authorization": f"Bearer {self.bearer}"})

        if response.status_code != 200:
            raise Exception(f"Cannot get user id for {self.user} (HTTP %d): %s" % (response.status_code, response.text))

        self.user_id = response.json()["data"]["id"]

    def get_tweets_for_user(self, start_time=None):

        url = f"https://api.twitter.com/2/users/{self.user_id}" \
              f"/tweets?max_results=100&tweet.fields=public_metrics,created_at"
        headers = {"Authorization": f"Bearer {self.bearer}"}

        continue_request = True
        while continue_request:
            response = self.session.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(
                    f"Cannot get tweets for user {self.user_id} (HTTP %d): %s" % (response.status_code, response.text))

            data = response.json()
            for tweet in data["data"]:
                if tweet['text'].startswith('RT'):
                    continue
                else:
                    new_tweet = Tweet(
                        tweet['id'],
                        tweet['text'],
                        tweet['created_at'],
                        tweet['public_metrics']['impression_count'],
                        tweet['public_metrics']['retweet_count'],
                        tweet['public_metrics']['reply_count'],
                        tweet['public_metrics']['like_count'],
                        tweet['public_metrics']['quote_count'],
                        self.user_id
                    )
                    self.tweet_list.append(new_tweet)
            try:
                url = f"https://api.twitter.com/2/users/{self.user_id}/" \
                      f"tweets?max_results=100&tweet.fields=public_metrics,created_at" \
                      f"&pagination_token={data['meta']['next_token']}"
            except KeyError:
                print('No more tweets')
                continue_request = False

    def get_bearer_token(self):
        key = os.environ['TWITTER_KEY']
        secret = os.environ['TWITTER_SECRET']

        response = self.session.post(
            "https://api.twitter.com/oauth2/token",
            auth=(key, secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"})

        if response.status_code != 200:
            raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

        body = response.json()
        self.bearer = body["access_token"]

    def write_to_db(self):
        prod_session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        prod_dynamodb = prod_session.resource('dynamodb')
        project_data_table = prod_dynamodb.Table(TABLE_NAME)

        project_data_table.put_item(Item=self.to_json())
        for tweet in self.tweet_list:
            tweet.write_to_db()

    def get_from_db(self):
        prod_session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        prod_dynamodb = prod_session.resource('dynamodb')
        project_data_table = prod_dynamodb.Table(TABLE_NAME)
        response = project_data_table.get_item(
            Key={
                'user_id': self.user_id,
                'tweet_id': 'metadata'
            }
        )
        try:
            item = response['Item']
            self.user = item['statistics']['user']
            self.total_posts = int(item['statistics']['total_posts'])
            self.first_post = datetime.strptime(item['statistics']['first_post'], '%Y-%m-%d')
            self.last_post = datetime.strptime(item['statistics']['last_post'], '%Y-%m-%d')
            self.posts_per_day = float(item['statistics']['posts_per_day'])
            self.average_impressions = float(item['statistics']['average_impressions'])
            self.average_retweets = float(item['statistics']['average_retweets'])
            self.average_replies = float(item['statistics']['average_replies'])
            self.average_likes = float(item['statistics']['average_likes'])
            self.average_quotes = float(item['statistics']['average_quotes'])
            self.tweet_list = item['tweets']
            return True
        except KeyError:
            print('No data in database')
            return False

    def add_new_tweets(self):
        now = datetime.now()
        if self.last_post < now - timedelta(days=1):
            self.get_tweets_for_user()
            self.calculate_statistics()
            self.write_to_db()