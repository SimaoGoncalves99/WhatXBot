import os
import tweepy
from duckduckgo_search import DDGS
import requests
from typing import Optional, Any
import httpx
import logging

X_USER = os.environ.get("X_USER", "")
GROUP_ID = os.environ.get("GROUP_ID", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")
X_USER_ID = os.environ.get("X_USER_ID", "")

X_USER = os.environ.get("X_USER", "")
GROUP_ID = os.environ.get("GROUP_ID", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")

x_user_id = os.environ.get("X_USER_ID", "")
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Logger
logger = logging.getLogger(__name__)


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


#
# Connect to endpoint
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


async def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    json_response = connect_to_endpoint(url)
    return json_response["data"]["id"]


async def get_user_tweets(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    json_response = connect_to_endpoint(url)
    return json_response


async def recent_tweet(x_user_id):

    # Fetch user tweets (wait for the response)
    tweets = await get_user_tweets(x_user_id)

    # Fetch first tweet
    recent_tweet = tweets["data"][0]["text"]

    # Fetch text up until "https"
    index = recent_tweet.find("https")

    if index != -1:
        recent_tweet = recent_tweet[:index]

    recent_tweet = recent_tweet.strip()

    return recent_tweet


async def fetch_baller_name():

    # Fetch the most recent tweet of user x_user_id
    if X_USER_ID:
        try:
            logger.info(
                "Fetching the most recent tweet of the specified user..."
            )
            tweet = await recent_tweet(X_USER_ID)
        except Exception as e:
            logger.error(e)
            logger.info("Fetching user id using the Twitter client API...")
            if X_USER:
                try:
                    x_user_id = await get_user_id(X_USER)
                except Exception as e:
                    raise RuntimeError(e)
                logger.info(
                    "Fetching the most recent tweet of the specified user..."
                )
                tweet = await recent_tweet(x_user_id)
            else:
                logger.error("Provide a valid X username!")

    return tweet


async def fetch_baller_image(baller_name: str) -> bytes:

    results = DDGS().images(keywords=baller_name, max_results=1)
    image_url = results[0]["image"]

    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        return response.content


# if __name__ == "__main__":
#     get_message()
