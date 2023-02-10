from datetime import datetime
import boto3
import os
from botocore import errorfactory
import time

class Tweet:
    def __init__(self, id=None, text=None, created=None,
                 impressions=None, retweet_count=None, reply_count=None,
                 like_count=None, quote_count=None, user_id=None):
        self.id = id
        self.url = f'https://twitter.com/{user_id}/status/{id}'
        # set self.created to datetime object
        self.created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.text = text.replace('\n', ' ')
        self.impressions = impressions
        self.retweet_count = retweet_count
        self.reply_count = reply_count
        self.like_count = like_count
        self.quote_count = quote_count
        self.user_id = user_id


    def keys(self):
        return ['id', 'url', 'created', 'text', 'impressions', 'retweet_count',
                'reply_count', 'like_count', 'quote_count', 'user_id']

    def values(self):
        return [self.id, self.url, self.created, self.text, self.impressions,
                self.retweet_count, self.reply_count, self.like_count, self.quote_count, self.user_id]

    def to_json(self):
        return {
            'user_id': self.user_id,
            'tweet_id': self.id,
            'url': self.url,
            'created': self.created.strftime('%Y-%m-%d'),
            'text': self.text,
            'impressions': self.impressions,
            'retweet_count': self.retweet_count,
            'reply_count': self.reply_count,
            'like_count': self.like_count,
            'quote_count': self.quote_count
        }

    def write_to_db(self, retries=5, delay=4):
        TABLE_NAME = 'TweetData'
        prod_session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        prod_dynamodb = prod_session.resource('dynamodb')
        project_data_table = prod_dynamodb.Table(TABLE_NAME)

        try:
            project_data_table.put_item(Item=self.to_json())
        except Exception as e:
            print(f'ProvisionedThroughputExceededException: Retrying in {delay} seconds... ({retries} retries left)')
            if retries > 0:
                time.sleep(delay)
                self.write_to_db(retries=retries-1, delay=delay*2)
            else:
                raise e
