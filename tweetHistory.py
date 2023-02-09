import csv
from datetime import datetime
from tweetUtil import get_user_id, get_tweets_for_user

class TweetHistory:
    def __init__(self, user, bearer, session):
        self.session = session
        self.bearer = bearer
        self.user = user
        self.user_id = get_user_id(self.user, self.bearer, self.session)
        self.tweet_list = self.get_tweet_list()
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

    def get_tweet_list(self):
        return get_tweets_for_user(self.user_id, self.bearer, self.session)

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

    def print_top_tweets(self):
        self.sort_by_impressions()
        print(f'TOP TWEETS FOR {self.user}')
        print('Date -- Impressions -- Retweets -- Replies -- Likes -- Quotes -- Text -- URL')
        for tweet in self.tweet_list[:10]:
            print(
                f'{tweet.created.date()} - {tweet.impressions} - {tweet.retweet_count} - {tweet.reply_count} - {tweet.like_count} - {tweet.quote_count} - {tweet.text} - {tweet.url}')

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
        metadata = {
            'user': self.user,
            'total_posts': self.total_posts,
            'first_post': self.first_post,
            'last_post': self.last_post,
            'posts_per_day': self.posts_per_day,
            'average_impressions': self.average_impressions,
            'average_retweets': self.average_retweets,
            'average_replies': self.average_replies,
            'average_likes': self.average_likes,
            'average_quotes': self.average_quotes
        }
        json = {
            'metadata': metadata,
            'tweets': [tweet.to_json() for tweet in self.tweet_list]
        }
        return json
