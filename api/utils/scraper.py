# pip install playwright scrapfly-sdk
# playwright install
import os
from playwright.sync_api import sync_playwright
from pprint import pprint
import json
from email.utils import parsedate_to_datetime
from datetime import datetime
from tqdm import tqdm


X_PROFILE_URL = os.environ.get("X_PROFILE_URL", "https://x.com/MrBeast")
CACHE_FILE = "seen_tweets.json"


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


def scrape_today_latest_tweet(url: str, max_scrolls=5):
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

        # Simulate scrolling
        for _ in range(max_scrolls):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)

        all_tweets = []

        for response in tqdm(_xhr_calls, desc="Scrolling X..."):
            try:
                data = response.json()
                instructions = data["data"]["user"]["result"]["timeline"][
                    "timeline"
                ]["instructions"]
                entries = []
                for instr in instructions:
                    entries.extend(instr.get("entries", []))

                for e in entries:
                    if (
                        e["entryId"].startswith("tweet-")
                        and "tweet_results" in e["content"]["itemContent"]
                    ):
                        tweet = e["content"]["itemContent"]["tweet_results"][
                            "result"
                        ]
                        legacy = tweet.get("legacy", {})
                        created_at = legacy.get("created_at")
                        if created_at:
                            dt = parsedate_to_datetime(created_at)
                            tweet["__parsed_date__"] = dt
                            all_tweets.append(tweet)
            except Exception:
                continue

        # Filter today's tweets
        today = datetime.utcnow().date()
        todays_tweets = [
            t
            for t in all_tweets
            if t.get("__parsed_date__")
            and t["__parsed_date__"].date() == today
        ]

        if not todays_tweets:
            print("No tweet found for today.")
            return None

        # Get most recent
        most_recent = sorted(
            todays_tweets, key=lambda t: t["__parsed_date__"], reverse=True
        )[0]
        legacy = most_recent.get("legacy", {})
        return {
            "text": legacy.get("full_text"),
            "images": [
                m["media_url_https"]
                for m in legacy.get("entities", {}).get("media", [])
                if m.get("type") == "photo"
            ],
            "created_at": legacy.get("created_at"),
            "tweet_id": most_recent.get("rest_id"),
            "tweet_url": f"https://x.com/{legacy.get('screen_name')}/status/{most_recent.get('rest_id')}",
        }


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

        # Simulate scrolling
        for _ in range(max_scrolls):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)

        all_tweets = []

        for response in _xhr_calls:
            try:
                data = response.json()
                instructions = data["data"]["user"]["result"]["timeline"][
                    "timeline"
                ]["instructions"]
                entries = []
                for instr in instructions:
                    entries.extend(instr.get("entries", []))

                for e in entries:
                    if (
                        e["entryId"].startswith("tweet-")
                        and "tweet_results" in e["content"]["itemContent"]
                    ):
                        tweet = e["content"]["itemContent"]["tweet_results"][
                            "result"
                        ]
                        legacy = tweet.get("legacy", {})
                        created_at = legacy.get("created_at")
                        if created_at:
                            dt = parsedate_to_datetime(created_at)
                            tweet["__parsed_date__"] = dt
                            all_tweets.append(tweet)
            except Exception:
                continue

        # Filter today's tweets
        today = datetime.utcnow().date()
        todays_tweets = [
            t
            for t in all_tweets
            if t.get("__parsed_date__")
            and t["__parsed_date__"].date() == today
        ]

        if not todays_tweets:
            print("No tweet found for today.")
            return None

        # Get most recent
        most_recent = sorted(
            todays_tweets, key=lambda t: t["__parsed_date__"], reverse=True
        )[0]
        legacy = most_recent.get("legacy", {})
        return {
            "text": legacy.get("full_text"),
            "images": [
                m["media_url_https"]
                for m in legacy.get("entities", {}).get("media", [])
                if m.get("type") == "photo"
            ],
            "created_at": legacy.get("created_at"),
            "tweet_id": most_recent.get("rest_id"),
            "tweet_url": f"https://x.com/{legacy.get('screen_name')}/status/{most_recent.get('rest_id')}",
        }


def load_seen_tweet_ids():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_tweet_ids(tweet_ids):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(tweet_ids), f)


def scrape_new_tweets(url: str, max_scrolls=10):
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

        for i in range(max_scrolls):
            prev_call_count = len(_xhr_calls)
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            new_calls = len(_xhr_calls) - prev_call_count
            print(f"🌀 Scroll {i + 1}: {new_calls} new XHR calls")
            if new_calls == 0:
                print("⛔ No new data loaded, stopping scrolls.")
                break

        all_tweets = []
        seen_ids = set()

        for response in _xhr_calls:
            try:
                data = response.json()
                instructions = data["data"]["user"]["result"]["timeline"][
                    "timeline"
                ]["instructions"]
                for instr in instructions:
                    entries = instr.get("entries", [])
                    for e in entries:
                        if (
                            e["entryId"].startswith("tweet-")
                            and "tweet_results" in e["content"]["itemContent"]
                        ):
                            tweet = e["content"]["itemContent"][
                                "tweet_results"
                            ]["result"]
                            legacy = tweet.get("legacy", {})
                            created_at = legacy.get("created_at")
                            if created_at:
                                dt = parsedate_to_datetime(created_at)
                                tweet["__parsed_date__"] = dt
                                all_tweets.append(tweet)
                                seen_ids.add(tweet.get("rest_id"))
            except Exception:
                continue

        print(f"🔍 Total fetched tweets: {len(all_tweets)}")
        return all_tweets


def find_today_tweet(tweets, seen_ids):
    today = datetime.utcnow().date()
    new_ids = seen_ids.copy()
    candidate_tweet = None

    for tweet in sorted(
        tweets, key=lambda t: t["__parsed_date__"], reverse=True
    ):
        tid = tweet.get("rest_id")
        if not tid or tid in new_ids:
            continue

        new_ids.add(tid)
        tweet_date = tweet["__parsed_date__"].date()

        if tweet_date == today and not candidate_tweet:
            legacy = tweet.get("legacy", {})
            candidate_tweet = {
                "text": legacy.get("full_text"),
                "images": [
                    m["media_url_https"]
                    for m in legacy.get("entities", {}).get("media", [])
                    if m.get("type") == "photo"
                ],
                "created_at": legacy.get("created_at"),
                "tweet_id": tid,
                "tweet_url": f"https://x.com/{legacy.get('screen_name')}/status/{tid}",
            }

    return candidate_tweet, new_ids


if __name__ == "__main__":
    attempts = 1
    result = None
    while not result:
        print(f"\n🔁 Scrolling attempt {attempts}...")
        seen = load_seen_tweet_ids()
        tweets = scrape_new_tweets(X_PROFILE_URL)
        result, updated_seen = find_today_tweet(tweets, seen)
        save_seen_tweet_ids(updated_seen)

        print(
            f"🧠 Seen tweet IDs: {len(seen)} ➡️ {len(updated_seen)} after update"
        )

        if result:
            print("✅ New tweet from today:")
            print(json.dumps(result, indent=4, ensure_ascii=False))
            break
        else:
            print("🕐 No new tweet from today yet.")
            attempts += 1

# if __name__ == "__main__":

#     # data = scrape_twitter_info(X_PROFILE_URL, True)
#     # with open("./user_info.json", "w") as f:
#     #     json.dump(data, f, indent=4, ensure_ascii=False)

#     tweet = scrape_today_latest_tweet(X_PROFILE_URL)
#     if tweet:
#         with open("most_recent_tweet.json", "w") as f:
#             json.dump(
#                 tweet,
#                 f,
#                 indent=4,
#             )
