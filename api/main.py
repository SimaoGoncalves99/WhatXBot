from utils.scraper import get_latest_tweet
from utils.sender import send_to_group
import os

USERNAME = "BallerOfTheDay_"  # change to your target
GROUP_ID = "ID54ed51eUMG6EJCiVaSaW"  # your group id (e.g. from pywhatkit docs)


def load_last_tweet_id():
    if os.path.exists("last_tweet.txt"):
        with open("last_tweet.txt") as f:
            return f.read().strip()
    return None


def save_last_tweet_id(tweet_id):
    with open("last_tweet.txt", "w") as f:
        f.write(tweet_id)


def main():
    last_id = load_last_tweet_id()
    latest = get_latest_tweet(USERNAME)

    if latest is None:
        print("No tweets found.")
        return

    tweet_id, tweet_text = latest

    if tweet_id != last_id:
        send_to_group(GROUP_ID, f"New tweet from @{USERNAME}:\n\n{tweet_text}")
        save_last_tweet_id(tweet_id)
    else:
        print("No new tweets.")


if __name__ == "__main__":
    main()
