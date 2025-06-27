import base64
import random
import time
import traceback

from selenium import webdriver
from selenium.common import TimeoutException
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

        # Click the 'Next' button
        click_not_now_button(driver)

        # Wait for input box to appear
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-describedby='Message']"))
        )
        # Add any pictures that might be required
        for pic in pictures or []:
            print(f"🖼️ Uploading picture: {pic}")
            drag_and_drop_file(driver, pic, 'body')

            # pic_btn = wait_for_message_photo_button(driver)
            # pic_btn.click()

            # TODO: Remove below. this is for debugging
            input("⏸️ Check manually. Press Enter to continue...")

            time.sleep(1)

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


def click_not_now_button(driver, timeout=10):
    """
    Detects and clicks the 'Not Now' button if present and visible.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']"))
        )
        if button.is_displayed() and button.is_enabled():
            button.click()
            print("✅ 'Not Now' button clicked.")
            return True
        else:
            print("⚠️ 'Not Now' button found but not visible/enabled.")
            return False
    except TimeoutException:
        print("ℹ️ 'Not Now' button not found.")
        return False


def wait_for_message_photo_button(driver, timeout=10):
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//div[@role='button'][.//svg[contains(@aria-label, 'Photo') or contains(@aria-label, 'Video')]]"
        )))
        print("✅ Found story overlay element.")
        return element
    except Exception as e:
        print(f"❌ SVG element didn't appear in {timeout}s: {e}")
        return None


def drag_and_drop_file(driver, file_path, target_selector):
    with open(file_path, "rb") as f:
        file_content = f.read()
    file_name = file_path.split("/")[-1]
    file_b64 = base64.b64encode(file_content).decode("utf-8")

    js = """
    var target = document.querySelector(arguments[0]);
    var b64Data = arguments[1];
    var fileName = arguments[2];

    function b64toBlob(b64Data, contentType='application/octet-stream', sliceSize=512) {
        var byteCharacters = atob(b64Data);
        var byteArrays = [];
        for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            var slice = byteCharacters.slice(offset, offset + sliceSize);
            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            var byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
        return new Blob(byteArrays, {type: contentType});
    }

    var blob = b64toBlob(b64Data);
    var file = new File([blob], fileName);
    var dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);

    function triggerEvent(type) {
        var event = new DragEvent(type, {
            dataTransfer: dataTransfer,
            bubbles: true,
            cancelable: true
        });
        target.dispatchEvent(event);
    }

    triggerEvent('dragenter');
    triggerEvent('dragover');
    triggerEvent('drop');
    """
    driver.execute_script(js, target_selector, file_b64, file_name)


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
