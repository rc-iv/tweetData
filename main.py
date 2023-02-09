import requests
from pprint import pprint
import csv
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from tweetUtil import get_bearer_token, get_user_id, get_tweets_for_user
from tweet import Tweet
from tweetHistory import TweetHistory


twitter_key = "ly00p5JK6Moh4SEr093HPQ1T5"
twitter_secret = "sqJbmi1RKkNjMKuA8X1nnKmAyVAsBzJAXrbCPOWDdw9cOhoNrm"

# Setup retry strategy
session = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# Get bearer token
bearer = get_bearer_token(session)

user = 'wgmiio'
user_id = get_user_id(user, bearer, session)
tweet_list = TweetHistory(get_tweets_for_user(user_id, bearer, session))

tweet_list.print_summary()
tweet_list.print_top_tweets()

pprint(tweet_list.to_json())