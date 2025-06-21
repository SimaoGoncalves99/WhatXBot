from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from utils.messages import get_message
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

GROUP_NAME = os.environ.get("GROUP_NAME", "")


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


# ─── SEND MESSAGE TO GROUP BY NAME ──────────────────────────────
def send_to_whatsapp(message, image_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-data-dir=/root/whatsapp_session"
    )  # Reuse login

    driver = webdriver.Firefox(options=options)
    driver.get("https://web.whatsapp.com")

    print("Waiting for WhatsApp Web to load...")
    time.sleep(10)

    try:
        # Search for the group
        search_box = driver.find_element(
            By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'
        )
        search_box.clear()
        search_box.send_keys(GROUP_NAME)
        time.sleep(3)

        group_title = driver.find_element(
            By.XPATH, f'//span[@title="{GROUP_NAME}"]'
        )
        group_title.click()
        time.sleep(2)

        # Send the text message
        input_box = driver.find_element(
            By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
        )
        input_box.send_keys(message + Keys.ENTER)
        print("Message sent.")

        # Send the image
        if image_path and os.path.exists(image_path):
            attach_btn = driver.find_element(
                By.XPATH, '//div[@title="Attach"]'
            )
            attach_btn.click()
            time.sleep(1)

            file_input = driver.find_element(
                By.XPATH,
                '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]',
            )
            file_input.send_keys(image_path)
            time.sleep(2)

            send_btn = driver.find_element(
                By.XPATH, '//span[@data-icon="send"]'
            )
            send_btn.click()
            print("Image sent.")

        time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()


# ─── MAIN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    # text, image_path = get_message()
    send_to_whatsapp("", "/home/scg/WhatXBot/image.jpeg")
