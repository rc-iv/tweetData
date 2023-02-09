from datetime import datetime


# define Tweet class
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
        return dict(zip(self.keys(), self.values()))

