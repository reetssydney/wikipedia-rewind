import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2
import glob

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
ARTICLE_TITLE = "Python_(programming_language)"  # Change this to the article you want
SCREENSHOTS_DIR = "screenshots"
VIDEO_OUTPUT = "timelapse.mp4"

# Step 1: Fetch Revision History
def get_revisions(title, limit=10):
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": title,
        "rvprop": "ids|timestamp",
        "rvlimit": limit,
        "rvdir": "newer"
    }
    response = requests.get(WIKI_API_URL, params=params).json()
    pages = response.get("query", {}).get("pages", {})
    for page in pages.values():
        return page.get("revisions", [])
    return []

# Step 2: Capture Screenshots of Diffs
def capture_diff_screenshots(revisions):
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    for i in range(len(revisions) - 1):
        oldid = revisions[i]["revid"]
        newid = revisions[i + 1]["revid"]
        url = f"https://en.wikipedia.org/w/index.php?title={ARTICLE_TITLE}&type=revision&diff={newid}&oldid={oldid}"
        driver.get(url)
        time.sleep(2)  # Allow page to load
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"diff_{i}.png")
        driver.save_screenshot(screenshot_path)
    
    driver.quit()

# Step 3: Convert Screenshots to Video
def create_video():
    img_files = sorted(glob.glob(f"{SCREENSHOTS_DIR}/*.png"))
    frame = cv2.imread(img_files[0])
    h, w, _ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(VIDEO_OUTPUT, fourcc, 1, (w, h))
    
    for img in img_files:
        frame = cv2.imread(img)
        video.write(frame)
    
    video.release()

# Run the full pipeline
revisions = get_revisions(ARTICLE_TITLE, limit=5)  # Fetch 5 revisions for testing
capture_diff_screenshots(revisions)
create_video()
print("Timelapse video created: timelapse.mp4")
