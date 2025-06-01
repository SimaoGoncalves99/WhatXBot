import snscrape.modules.twitter as sntwitter

def get_latest_tweet(username: str) -> tuple[str, str] | None:
    for tweet in sntwitter.TwitterUserScraper(username).get_items():
        return str(tweet.id), tweet.content