from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import requests
from urllib.parse import urljoin
import random



relative_path = r"chromedriver-win64\chromedriver.exe"
chrome_driver_path = os.path.abspath(relative_path)


chrome_options = Options()


driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)


CheeseImages = []
CheeseNames = []


image_directory = 'cheese_images'
os.makedirs(image_directory, exist_ok=True)


total_pages = 98
random_page = random.randint(1, total_pages)


base_url = 'https://www.cheese.com/'
page_url = f"{base_url}?page={random_page}"


driver.get(page_url)


try:
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'cheese-image'))
    )
except Exception as e:
    print("Failed to load the page or no cheese items found.")
    driver.quit()
    exit()


content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

# Find all cheese items
for element in soup.findAll('div', attrs={'class': 'cheese-item'}):
    image_div = element.find('div', attrs={'class': 'cheese-image'})
    name_h3 = element.find('h3')
    
    if image_div and name_h3:
        img_tag = image_div.find('img')
        if img_tag:
            img_url = img_tag['src']
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            img_name = img_url.split('/')[-1]
            img_path = os.path.join(image_directory, img_name)
            
            # Download and save the image
            try:
                img_data = requests.get(img_url).content
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                
                CheeseImages.append(img_path)  # Save the path to the downloaded image
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {img_url}: {e}")
        
        CheeseNames.append(name_h3.text)  # Extract the cheese name

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame({'Cheese Name': CheeseNames, 'Cheese Image': CheeseImages})
df.to_csv('cheese.csv', index=False, encoding='utf-8')


driver.quit()
