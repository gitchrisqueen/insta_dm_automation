import os
import random

from dotenv import load_dotenv

from utilities import instagram

load_dotenv()
username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

driver = instagram.launch_browser()
instagram.login(driver, username, password)

# Test variables
message = "Hello. I like your content. Would you like to collaborate?"
profile_url = "https://www.instagram.com/chrisqueenusa"

# Example profile
instagram.navigate_to_profile(driver, profile_url)

if False:
    # if instagram.has_story(driver):
    instagram.view_story(driver)
    instagram.send_message_via_story(driver, message)
    instagram.close_story(driver)
elif instagram.can_message(driver):
    # Randomly choose 2 images from the ./test_imgs folder and include them with the message
    base_folder = "./test_imgs"
    test_imgs = os.listdir(base_folder)
    random_imgs = random.sample(test_imgs, 2)
    random_imgs_abs = [os.path.abspath(os.path.join(base_folder, img)) for img in random_imgs]
    instagram.send_message(driver, message, random_imgs_abs)


input("Main Finisehd. Press Enter to close browser...")
driver.quit()
