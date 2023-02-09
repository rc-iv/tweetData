import requests
import os
from tweet import Tweet


# Get bearer token
def get_bearer_token(session):
    key = os.environ['TWITTER_KEY']
    secret = os.environ['TWITTER_SECRET']

    response = session.post(
        "https://api.twitter.com/oauth2/token",
        auth=(key, secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"})

    if response.status_code != 200:
        raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

    body = response.json()
    return body["access_token"]


# Find twitter userid for a given username
def get_user_id(username, bearer_token, session):
    response = session.get(
        f"https://api.twitter.com/2/users/by/username/{username}",
        headers={"Authorization": f"Bearer {bearer_token}"})

    if response.status_code != 200:
        raise Exception(f"Cannot get user id for {username} (HTTP %d): %s" % (response.status_code, response.text))

    return response.json()["data"]["id"]


# Lookup all tweets + replies for a user (excludes retweets)
def get_tweets_for_user(user_id, bearer_token, session):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&tweet.fields=public_metrics,created_at"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    continue_request = True
    tweet_list = []
    while continue_request:
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Cannot get tweets for user {user_id} (HTTP %d): %s" % (response.status_code, response.text))

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
                    user_id
                )
                tweet_list.append(new_tweet)
        try:
            url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&tweet.fields=public_metrics,created_at&pagination_token={data['meta']['next_token']}"
        except KeyError:
            continue_request = False
    return tweet_list
