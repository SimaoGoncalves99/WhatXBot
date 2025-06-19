from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pickle
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
from playwright.sync_api import sync_playwright
import pickle
import tweepy
from duckduckgo_search import DDGS

# from duckduckgo_search import ddg_images
import requests
from bs4 import BeautifulSoup as bs
import urllib.request
from PIL import Image


X_USER = os.environ.get("X_USER", "")
X_USER_ID = os.environ.get("X_USER_ID", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")


client = tweepy.Client(bearer_token=BEARER_TOKEN)

import requests
import os

bearer_token = os.environ.get("BEARER_TOKEN")


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
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


if __name__ == "__main__":

    # Fetch user id
    if not X_USER_ID:
        X_USER_ID = get_user_id(X_USER)

    # Fetch user tweets
    tweets = get_user_tweets(X_USER_ID)

    # Fetch first tweet
    recent_tweet = tweets[0]["text"]

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
    urllib.request.urlretrieve(str(results[0]["image"]), "image.jpeg")
