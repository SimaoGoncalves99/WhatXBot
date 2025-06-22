from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from utils.messages import get_message
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pickle
from tqdm import tqdm
import pywhatkit

GROUP_NAME = os.environ.get("GROUP_NAME", "")


def save_cookies(driver, path="./cookies.pkl"):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, path="./cookies.pkl"):
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
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.get("https://web.whatsapp.com")
    time.sleep(5)

    # Load cookies if they exist
    if load_cookies(driver):
        driver.refresh()
        time.sleep(10)  # Give time after refresh
    else:
        print("Please log in manually...")
        # Wait until WhatsApp is logged in (wait for chat sidebar)
        while True:
            try:
                driver.find_element(By.ID, "pane-side")  # Sidebar = logged in
                break
            except:
                time.sleep(2)

        save_cookies(driver)
        print("✅ Cookies saved after successful login.")

    return driver


def send_message_and_image(group_name, message=None, image_path=None):
    driver = getFirefoxDriver()

    try:
        # Locate the search box and enter group name
        print(f"🔍 Searching for group: {group_name}")
        search_box = driver.find_element(
            By.XPATH, '//div[@title="Search input textbox"]'
        )
        search_box.click()
        search_box.clear()
        search_box.send_keys(group_name)
        time.sleep(3)

        group = driver.find_element(By.XPATH, f'//span[@title="{group_name}"]')
        group.click()
        time.sleep(2)

        # Send text message
        if message:
            print("💬 Sending message...")
            input_box = driver.find_element(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
            )
            input_box.send_keys(message + Keys.ENTER)
            print("✅ Message sent.")

        # Send image
        if image_path and os.path.exists(image_path):
            print("📎 Attaching image...")
            attach_button = driver.find_element(
                By.XPATH, '//div[@title="Attach"]'
            )
            attach_button.click()
            time.sleep(1)

            file_input = driver.find_element(
                By.XPATH,
                '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]',
            )
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(3)

            print("📤 Sending image...")
            send_button = driver.find_element(
                By.XPATH, '//span[@data-icon="send"]'
            )
            send_button.click()
            print("✅ Image sent.")

        time.sleep(5)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    send_message_and_image(
        group_name=GROUP_NAME,
        message="Hello from Ubuntu bot! 🤖",
        image_path="your_image.jpg",  # Set this or leave as None
    )
