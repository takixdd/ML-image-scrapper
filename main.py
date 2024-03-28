import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time
from PIL import Image
from io import BytesIO


def is_large_enough(image_url, min_width, min_height):
    try:
        response = requests.get(image_url, stream=True)
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        return width >= min_width and height >= min_height
    except Exception as e:
        print(f"Error checking image size: {e}")
        return False


def resize_image(image, target_width, target_height):
    return image.resize((target_width, target_height))


def download_images(queries, num_images, min_width, min_height, target_width, target_height):
    for query in queries:
        url = f"https://www.google.com/search?q={query}&source=lnms&tbm=isch"
        driver = webdriver.Chrome()  # Chrome WebDriver is needed
        driver.get(url)

        # Accept cookies
        try:
            accept_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Odrzuć wszystko')]")))
            accept_button.click()
        except Exception as e:
            print(f"No accept cookies button found or couldn't be clicked for {query}: {e}")

        # Simulate scrolling and clicking "Pokaż więcej wyników"
        last_height = 0
        num_iterations = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.2)  # Adjust time between scrolls
            try:
                more_results_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Pokaż więcej wyników']")))
                more_results_button.click()
                num_iterations += 1
            except:
                pass
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or num_iterations >= 3:  # Adjust number of iterations as needed
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_links = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                if src.startswith('http') and is_large_enough(src, min_width, min_height):
                    image_links.append(src)

        driver.quit()

        # Create directory to store images
        os.makedirs(query, exist_ok=True)

        # Download and resize images
        downloaded_images = 0
        for i, link in enumerate(image_links):
            if downloaded_images >= num_images:
                break
            img_data = requests.get(link).content
            with Image.open(BytesIO(img_data)) as image:
                # Convert to RGB mode if not already in RGB
                if image.mode != "RGB":
                    image = image.convert("RGB")
                resized_image = resize_image(image, target_width, target_height)
                resized_image.save(f"{query}/{query}_{i+1}.jpg")
                downloaded_images += 1
                print(f"Downloaded and resized image {downloaded_images} for {query}")

        print(f"Total images downloaded for {query}: {downloaded_images}")


queries = ["cat", "car", "landscape"]  # Add more queries as needed
num_images = 4000  # You can adjust this number as needed
min_width = 99  # Adjust minimum width as needed
min_height = 99  # Adjust minimum height as needed
target_width = 350  # Adjust target width as needed
target_height = 200  # Adjust target height as needed
download_images(queries, num_images, min_width, min_height, target_width, target_height)
