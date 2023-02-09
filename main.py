import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from tweetHistory import TweetHistory


# Setup retry strategy
session = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))


user = 'chilearmy123'

tweet_list = TweetHistory(user, session)

tweet_list.print_summary()
tweet_list.print_top_tweets()
