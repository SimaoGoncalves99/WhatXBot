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
from selenium.webdriver.firefox.options import Options
import time
import pickle


X_USER = os.environ.get("X_USER", "MrBeast")
CACHE_FILE = "seen_tweets.json"


def save_cookies(driver, path="obj/cookies.pkl"):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, path="obj/cookies.pkl"):
    try:
        cookies = pickle.load(open(path, "rb"))
        for cookie in cookies:
            if "expiry" in cookie:
                cookie["expiry"] = int(cookie["expiry"])
            driver.add_cookie(cookie)
        return True
    except FileNotFoundError:
        return False


def getFirefoxDriver(headless=False):
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options=options)

    driver.get("https://x.com/")
    time.sleep(2)

    # Try to load cookies
    if load_cookies(driver):
        driver.refresh()
    else:
        print("Please log in manually within the browser window...")
        # Wait some time for manual login
        time.sleep(
            60
        )  # Or wait for user input, or implement smarter wait here
        save_cookies(driver)

    return driver


def twitter_login(driver):

    driver.get("https://twitter.com/login")

    # Fill username
    driver.find_element_by_xpath(
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'
    ).send_keys(USERNAME)

    # Fill password


def get_latest_tweet(driver, username="MrBeast"):
    try:
        driver.get(f"https://x.com/{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )

        articles = driver.find_elements(By.TAG_NAME, "article")

        # Iterate over articles and find first non-pinned tweet
        for article in articles:
            try:
                pinned_label = article.find_element(
                    By.XPATH, ".//div[@data-testid='pinnedTweet']"
                )
                # If pinned tweet found, skip it
                continue
            except:
                # No pinned label found, this is a normal tweet
                tweet_text_elem = article.find_element(
                    By.XPATH, ".//div[@data-testid='tweetText']"
                )
                tweet_text = tweet_text_elem.text

                link_elem = article.find_element(
                    By.XPATH, ".//a[contains(@href, '/status/')]"
                )
                tweet_link = link_elem.get_attribute("href")

                image_elems = article.find_elements(
                    By.XPATH, ".//img[contains(@src, 'twimg')]"
                )
                image_urls = list(
                    {img.get_attribute("src") for img in image_elems}
                )

                return {
                    "text": tweet_text,
                    "tweet_url": tweet_link,
                    "images": image_urls,
                }

    except TimeoutException:
        print("❌ Timeout: No tweets loaded.")
    except Exception as e:
        print("❌ Exception while fetching tweet:", e)


if __name__ == "__main__":
    driver = getFirefoxDriver()
    data = get_latest_tweet(driver, username=X_USER)
    driver.quit()

    if data:
        from pprint import pprint

        pprint(data)
