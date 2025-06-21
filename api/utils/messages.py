import os
import tweepy
from duckduckgo_search import DDGS
import requests
import urllib.request


X_USER = os.environ.get("X_USER", "")
GROUP_ID = os.environ.get("GROUP_ID", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")

x_user_id = os.environ.get("X_USER_ID", "")
client = tweepy.Client(bearer_token=BEARER_TOKEN)


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    json_response = connect_to_endpoint(url)
    return json_response["data"]["id"]


def get_user_tweets(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    json_response = connect_to_endpoint(url)
    return json_response


def get_message():
    global x_user_id

    # Fetch user id
    if not x_user_id:
        x_user_id = get_user_id(X_USER)

    # Fetch user tweets
    tweets = get_user_tweets(x_user_id)

    # Fetch first tweet
    recent_tweet = tweets["data"][0]["text"]

    # Fetch text up until "https"
    index = recent_tweet.find("https")

    if index != -1:
        recent_tweet = recent_tweet[:index]
        print(recent_tweet)

    recent_tweet = recent_tweet.strip()

    # Search for image with DDGS
    results = DDGS().images(
        keywords=recent_tweet,
        size=None,
        type_image=None,
        layout=None,
        license_image=None,
        max_results=100,
    )
    image = urllib.request.urlretrieve(str(results[0]["image"]), "image.jpeg")

    return recent_tweet, os.path.abspath("image.jpg")
