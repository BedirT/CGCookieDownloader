import os
import requests
import logging
import time
from typing import List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)

# =======================
# Browser Utility Functions
# =======================

def setup_browser() -> webdriver.Chrome:
    """Set up and return a Chrome browser instance."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=./selenium_profile")
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

# =======================
# Course Details Extraction Functions
# =======================

def get_course_details(browser: webdriver.Chrome, course_url: str) -> Tuple[str, str]:
    """Retrieve the course title and link from the provided URL.
    
    Args:
        browser (webdriver.Chrome): The browser instance.
        course_url (str): The URL of the course.
    
    Returns:
        Tuple[str, str]: The course title and link.
    """
    browser.get(course_url)
    wait_for_element(browser, "#js--course-list")
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    course_div = soup.find("div", class_="ms--lesson-course")
    course_title = course_div.find("p", class_="fw-bold").text.strip()
    course_link = course_div.find("a", class_="color-inherit")['href']
    
    return course_title, course_link

# =======================
# Video Lessons Functions
# =======================

def get_video_lessons(browser: webdriver.Chrome) -> List[str]:
    """Retrieve all video lesson links from the current page.
    
    Args:
        browser (webdriver.Chrome): The browser instance.
    
    Returns:
        List[str]: A list of video lesson links.
    """
    elements = browser.find_elements(By.CSS_SELECTOR, "#js--course-list a")
    print(elements)
    return [element.get_attribute('href') for element in elements]

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

def extract_lesson_name(browser: webdriver.Chrome) -> str:
    """Extract the lesson name from the current page.
    
    Args:
        browser (webdriver.Chrome): The browser instance.
    
    Returns:
        str: The lesson name.
    """
    lesson_name_element = browser.find_element(By.CSS_SELECTOR, ".lesson-content-inner .fw-bold")
    lesson_name = lesson_name_element.text.strip()
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        lesson_name = lesson_name.replace(char, '-')
    return lesson_name

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
    course_files_button = browser.find_element(By.CSS_SELECTOR, ".btn[data-bs-target='.js-courseFiles-modal']")
    browser.execute_script("arguments[0].click();", course_files_button)
    wait_for_element(browser, ".js-courseFiles-modal")
    
    download_links = browser.find_elements(By.CSS_SELECTOR, ".js-courseFiles-modal a")
    for link in download_links:
        url = link.get_attribute('href')
        filename = os.path.join(save_path, url.split('/')[-1])
        download_video_from_url(url, filename)
    
    close_button = browser.find_element(By.CSS_SELECTOR, ".js-courseFiles-modal .btn-close")
    close_button.click()

# =======================
# Main Execution
# =======================

def download_course(course_url: str, save_path: str, prefix_option: bool, skip_if_exists: bool) -> str:
    browser = setup_browser()
    browser.get(course_url)
    
    try:
        # Wait for the "signed-in" class in the header to appear
        WebDriverWait(browser, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > header.signed-in"))
        )
    except TimeoutException:
        browser.quit()
        return False, "Login not detected. Please try again."

    course_title, course_link = get_course_details(browser, course_url)
    logging.info(f"\nCourse Title: {course_title}")
    logging.info(f"Course Link: {course_link}")
    
    if not save_path:
        save_path = os.path.join(os.getcwd(), course_title)
    os.makedirs(save_path, exist_ok=True)
    
    video_lessons = get_video_lessons(browser)
    logging.info("\nVideo Lessons:")
    for idx, link in enumerate(video_lessons, 1):
        logging.info(link)
    
    for idx, link in enumerate(video_lessons, 1):
        logging.info(f"\nDownloading {link}...")
        browser.get(link)
        try:
            wistia_id = extract_wistia_id(browser)
        except:
            logging.warning("No Wistia ID found, skipping...")
            continue
        if wistia_id:
            video_url = get_wistia_video_url(wistia_id)
            lesson_name = extract_lesson_name(browser)
            filename = f"{idx:02}-{lesson_name}.mp4" if prefix_option else f"{lesson_name}.mp4"
            if skip_if_exists and os.path.exists(os.path.join(save_path, filename)):
                logging.info(f"File {filename} already exists, skipping...")
                continue
            full_path = os.path.join(save_path, filename)
            download_video_from_url(video_url, full_path)
            logging.info(f"Downloaded {filename}")
    
    download_course_files(browser, save_path)
    browser.quit()
    return "Download completed successfully!"
