# pip install playwright scrapfly-sdk
# playwright install
import os
from playwright.sync_api import sync_playwright
from pprint import pprint
import json
from email.utils import parsedate_to_datetime


X_PROFILE_URL = os.environ.get("X_PROFILE_URL", "https://x.com/MrBeast")


def scrape_twitter_info(url: str, boolean_user):

    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.on("response", intercept_response)

        page.goto(url)
        page.wait_for_load_state("networkidle")

        if boolean_user:
            selector = "[data-testid='primaryColumn']"
            xhr_condition = "UserBy"
            json_condition = "user"
        else:
            selector = "[data-testid='tweet']"
            xhr_condition = "TweetResultByRestId"
            json_condition = "tweetResult"

        # [data-testid='primaryColumn'] - userprofile data
        # [data-testid='tweet'] - tweets
        page.wait_for_selector(selector)
        # TweetResultByRestId
        usercalls = [f for f in _xhr_calls if xhr_condition in f.url]
        for uc in usercalls:
            data = uc.json()
            # tweetResult
            return data["data"][json_condition]["result"]


def scrape_most_recent_tweet(url: str):
    _xhr_calls = []

    def intercept_response(response):
        if (
            response.request.resource_type == "xhr"
            and "UserTweets" in response.url
        ):
            _xhr_calls.append(response)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.on("response", intercept_response)

        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("[data-testid='tweet']")

        # Try to find the UserTweets XHR
        user_tweets_call = None
        user_tweets_call = next(
            (r for r in _xhr_calls if "UserTweets" in r.url), None
        )
        if not user_tweets_call:
            print("No UserTweets XHR found.")
            return None

        data = user_tweets_call.json()
        instructions = data["data"]["user"]["result"]["timeline"]["timeline"][
            "instructions"
        ]

        entries = []
        for instr in instructions:
            if instr.get("entries"):
                entries.extend(instr["entries"])

        # Filter out tweet entries
        tweet_entries = [
            e["content"]["itemContent"]["tweet_results"]["result"]
            for e in entries
            if e["entryId"].startswith("tweet-")
            and "tweet_results" in e["content"]["itemContent"]
        ]

        if not tweet_entries:
            print("No tweet entries found.")
            return None

        tweets = []
        for t in tweet_entries:
            legacy = t.get("legacy", {})
            created_at = legacy.get("created_at")
            if created_at:
                dt = parsedate_to_datetime(created_at)
                text = legacy.get("full_text", "")
                media = legacy.get("entities", {}).get("media", [])
                image_urls = [
                    m["media_url_https"] for m in media if m["type"] == "photo"
                ]
                tweets.append(
                    {
                        "text": text,
                        "images": image_urls,
                        "created_at": created_at,
                        "created_at_parsed": dt,
                    }
                )
        # Sort by actual datetime, descending
        most_recent = sorted(
            tweets, key=lambda t: t["created_at_parsed"], reverse=True
        )[0]
        del most_recent["created_at_parsed"]  # remove internal key
        return most_recent


if __name__ == "__main__":

    # data = scrape_twitter_info(X_PROFILE_URL, True)
    # with open("./user_info.json", "w") as f:
    #     json.dump(data, f, indent=4, ensure_ascii=False)

    tweet = scrape_most_recent_tweet(X_PROFILE_URL)
    if tweet:
        with open("most_recent_tweet.json", "w") as f:
            json.dump(
                tweet,
                f,
                indent=4,
            )
