import os
import requests
import logging
import tqdm
from typing import List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)

# =======================
# Browser Utility Functions
# =======================

def setup_browser() -> webdriver.Chrome:
    """Set up and return a Chrome browser instance."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    try:
        chrome_options.add_argument("--user-data-dir=./selenium_profile")
    except Exception as e:
        # in windows if terminal wasn't admin, it will throw exception
        log.error(e)
        log.info("Skipping adding profile, using default")
    return webdriver.Chrome(options=chrome_options)

def wait_for_element(browser: webdriver.Chrome, css_selector: str, timeout: int = 30) -> None:
    """Wait for an element to be present in the browser.

    Args:
        browser (webdriver.Chrome): The browser instance.
        css_selector (str): The CSS selector of the element to wait for.
        timeout (int, optional): The maximum time to wait in seconds. Defaults to 30.
    """
    WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )

# Automated login and redirection
def login_and_redirect(browser: webdriver.Chrome, email: str, password: str) -> None:
    """Log into the website using the provided credentials and redirect to course page."""
    login_url = "https://cgcookie.com/customers/sign_in"
    browser.get(login_url)
    try:
        email_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "customer_email")))
        password_field = browser.find_element(By.ID, "customer_password")
        login_button = browser.find_element(By.XPATH, "//input[@type='submit']")

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

        # Wait for login to complete and check for presence of
        # <span class="avatar-fallback avatar avatar-25 customer ">
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.nav-item.avatar-nav-item")))
    except TimeoutException:
        logging.error("Login failed. Please check credentials or internet connection.")
        browser.quit()

# =======================
# Course Details Extraction Functions
# =======================

def get_course_details(browser: webdriver.Chrome, course_url: str) -> Tuple[str, List[str]]:
    """Retrieve the course title and link from the provided URL.

    Args:
        browser (webdriver.Chrome): The browser instance.
        course_url (str): The URL of the course.

    Returns:
        Tuple[str, List[str]]: The course title and video links.
    """
    browser.get(course_url)
    wait_for_element(browser, "#course-list-accordion")  # Ensure the correct ID is being used

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    # Fetching the page title (might be different from course titles in the accordion)
    course_title = soup.find("title").text.strip()

    # Find all chapters
    chapters = soup.find_all("div", class_="chapter-heading")
    video_data = []

    # Iterating through each chapter to fetch all lesson details
    for chapter in chapters:
        lessons = chapter.find_next_sibling("div", class_="accordion-collapse").find_all("li", class_="lesson")
        for lesson in lessons:
            lesson_title = lesson.find("a", class_="lesson-link").get("title")
            lesson_link = lesson.find("a", class_="lesson-link").get("href")
            video_data.append({"title": lesson_title, "link": lesson_link})

    return course_title, video_data

# =======================
# Video Lessons Functions
# =======================

def extract_wistia_id(browser: webdriver.Chrome) -> Optional[str]:
    """Extract the Wistia video ID from the current page.

    Args:
        browser (webdriver.Chrome): The browser instance.

    Returns:
        Optional[str]: The Wistia video ID or None if not found.
    """
    wistia_div = browser.find_element(By.CSS_SELECTOR, ".wistia_embed")
    return wistia_div.get_attribute('data-video-id')

def get_wistia_video_url(wistia_id: str) -> str:
    """Retrieve the video URL using the Wistia API.

    Args:
        wistia_id (str): The Wistia video ID.

    Returns:
        str: The video URL.
    """
    api_url = f"https://fast.wistia.net/embed/medias/{wistia_id}.json"
    response = requests.get(api_url)
    video_url = max(response.json()['media']['assets'], key=lambda x: x['size'])['url']
    return video_url

# =======================
# Download Functions
# =======================

def download_video_from_url(video_url: str, filename: str) -> None:
    """Download a video from the given URL and save it with the specified filename.

    Args:
        video_url (str): The URL of the video.
        filename (str): The name to save the video as.
    """
    response = requests.get(video_url, stream=True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

def download_course_files(browser: webdriver.Chrome, save_path: str) -> None:
    """Download all course files.

    Args:
        browser (webdriver.Chrome): The browser instance.
        save_path (str): The directory to save the files in.
    """
    WebDriverWait(browser, 300).until(
        EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Course Files']"))
    )
    course_files_button = browser.find_element(By.XPATH, "//button[normalize-space()='Course Files']")
    course_files_button.click()

    links = browser.find_elements(By.CSS_SELECTOR, ".modal-body .text-truncate a")
    link_details = [(link.get_attribute('href'), link.get_attribute('textContent').strip()) for link in links]

    # download files by url
    # create folder for files
    files_path = os.path.join(save_path, "course_files/")
    os.makedirs(files_path, exist_ok=True)
    for url, filename in link_details:
        if not filename.strip():  # Check if filename is empty or just spaces
            logging.warning(f"Skipping a file due to empty filename. URL: {url}")
            continue
        logging.info(f"Downloading {filename}...")
        response = requests.get(url, stream=True)
        with open(os.path.join(files_path, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        logging.info(f"Downloaded {filename}")

# =======================
# Main Execution
# =======================

if __name__ == "__main__":
    email = "bedirtpkn@gmail.com"#input("Enter your email: ")
    password = "Bt@536353"#input("Enter your password: ")

    browser = setup_browser()
    login_and_redirect(browser, email, password)

    # course_urls = input("Enter course URLs separated by comma: ").split(',')
    course_urls = "https://cgcookie.com/courses/sessions-macro, https://cgcookie.mavenseed.com/courses/fundamentals-of-digital-lighting-in-blender".split(',')

    # prefix_option = input("Would you like to add a prefix to filenames? (yes/no): ").lower() == 'yes'
    # skip_if_exists = input("Would you like to skip videos that already exist? (yes/no): ").lower() == 'yes'
    # also opting for fixed options
    prefix_option = True
    skip_if_exists = True

    course_data = []
    for course_url in course_urls:
        course_url = course_url.strip()
        course_title, video_data = get_course_details(browser, course_url)
        logging.info(f"\nCourse Title: {course_title}")

        course_data.append({
            "course_title": course_title,
            "video_data": video_data
        })

    base_url = "https://cgcookie.com"

    for course in course_data:
        course_title = course['course_title']
        video_data = course['video_data']
        # currently we are opting for a fixed path
        save_path = os.path.join(os.getcwd(), "courses", course_title)
        os.makedirs(save_path, exist_ok=True)

        for idx, data in enumerate(video_data, 1):
            lesson_title = data['title']
            lesson_link = data['link']

            logging.info(f"\nDownloading {base_url + lesson_link}...")
            browser.get(base_url + lesson_link)
            try:
                wistia_id = extract_wistia_id(browser)
            except:
                logging.warning("No Wistia ID found, skipping...")
                continue
            if wistia_id:
                video_url = get_wistia_video_url(wistia_id)
                filename = f"{idx:02}-{lesson_title}.mp4" if prefix_option else f"{lesson_title}.mp4"
                full_path = os.path.join(save_path, filename)
                if skip_if_exists and os.path.exists(full_path):
                    logging.info(f"Skipping {filename} as it already exists...")
                    continue
                download_video_from_url(video_url, full_path)
                logging.info(f"Downloaded {filename}")

            if idx == 1: # first lesson
                download_course_files(browser, save_path)

    browser.quit()
