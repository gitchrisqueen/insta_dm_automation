import random
import time
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def launch_browser():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    return driver


def login(driver, username: str, password: str):
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, 15)

    # Wait for login fields to appear
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    user_input = driver.find_element(By.NAME, "username")
    pass_input = driver.find_element(By.NAME, "password")

    # Simulate human typing
    _slow_typing(user_input, username)
    _slow_typing(pass_input, password)
    pass_input.send_keys(Keys.RETURN)

    # Wait for home or error
    time.sleep(5)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Home']")))
        print("✅ Logged in successfully.")
        return True
    except:
        print("⚠️ Login may have failed or 2FA required.")
        return False


def _slow_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def navigate_to_profile(driver, profile_url: str):
    driver.get(profile_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "main"))
    )
    time.sleep(random.uniform(2, 4))


def has_story(driver) -> bool:
    try:
        # Profile picture with story ring
        driver.find_element(
            By.XPATH,
            "//header//canvas[following-sibling::span/img[contains(@alt, 'profile picture')]]"
        )
        print("📸 Story is available.")
        return True
    except:
        print("📭 No story found.")
        traceback.print_exc()
        return False


def view_story(driver):
    try:
        # Find the profile picture image and click it to view the story
        profile_img = driver.find_element(
            By.XPATH,
            "//header//span/img[contains(@alt, 'profile picture')]"
        )
        profile_img.click()
        print("▶️ Watching story...")
        time.sleep(random.uniform(5, 8))  # Watch time
    except Exception as e:
        print(f"⚠️ Failed to watch story: {e}")


def close_story(driver):
    try:
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("❎ Closed story.")
    except:
        print("❌ Could not close story manually.")


def can_message(driver) -> bool:
    try:
        msg_btn = driver.find_element(By.XPATH, "//div[text()='Message']")
        return True
    except:
        return False


def send_message(driver, message: str, pictures: list = None):
    try:
        msg_btn = driver.find_element(By.XPATH, "//div[text()='Message']")
        msg_btn.click()

        # Wait for input box to appear
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )
        # Add any pictures that might be required
        for pic in pictures or []:
            # For the first picture click the picture icon
            if pictures.index(pic) == 0:
                pic_btn = driver.find_element(
                    By.XPATH,
                    "//div[@role='button'][.//svg[contains(@aria-label, 'Photo') or contains(@aria-label, 'Video')]]"
                )
                pic_btn.click()                pic_btn.click()
                time.sleep(1)
            else:
                # Click the add more picture button
                add_more_btn = driver.find_element(By.XPATH, "//div[text()='Add more']")

            # Upload the picture
            upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
            upload_input.send_keys(pic)

            time.sleep(random.uniform(2, 4))

        time.sleep(1)
        _slow_typing(input_box, message)
        input_box.send_keys(Keys.RETURN)
        print(f"📨 Message sent: {message}")
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        traceback.print_exc()


def send_message_via_story(driver, message: str):
    try:
        # Look for the story message input box (typically <textarea> or <input>)
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Reply to')]"))
        )
        time.sleep(random.uniform(1, 2))
        _slow_typing(input_box, message)
        # Find the button sibling and click it
        button = input_box.find_element(By.XPATH, "following-sibling::div[@role='button']")
        button.click()
        print(f"📩 Sent story reply: {message}")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"❌ Failed to send message via story: {e}")
        traceback.print_exc()


# Test mode
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")

    if not username or not password:
        raise ValueError("Missing IG_USERNAME or IG_PASSWORD in .env")

    driver = launch_browser()
    success = login(driver, username, password)
    if not success:
        input("⏸️ Check manually. Press Enter to close browser...")
    else:
        input("⏸️ Logged in. Press Enter to close browser...")

    driver.quit()
