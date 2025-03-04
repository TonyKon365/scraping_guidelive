import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
import time
from Utils.open_ai import customize, customizable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

def convert(input_value):
    date_object = datetime.strptime(input_value, "%a %d %b %Y")
    output_date = date_object.strftime("%Y-%m-%d")
    return output_date
# Print the output

# Function to scrape the main page and get article details
async def get_event_academycinemas():
    driver = webdriver.Chrome(options=chrome_options)
    main_page_url = "https://www.academycinemas.co.nz/coming-soon"
    driver.get(main_page_url)
    try:
        # Wait for the main content to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.coming-soon"))  # Waiting for <article class="coming-soon">
        )

        # Optionally, wait for a specific element that indicates content is loaded
        time.sleep(2)  # Adjust if necessary

        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        rows=soup.find_all('article',class_='coming-soon')

        for item in rows:
            # Extract relevant information from each event item
            event_title = item.find('h3').text.strip()  # Example selector for the title
          
            event_imgurl=item.find('img')['src']
            start_date=item.find('p',class_='coming-soon__date').text.strip()+' '+'2024'

           
            event_url='https://www.academycinemas.co.nz'+item.find('a')['href']
            event_description=scrape_detail_page(event_url)
            articles={
                    "target_id": "academycinemas",
                    "target_url": "https://www.academycinemas.co.nz/coming-soon",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": '',
                    "event_description": event_description,
                    "start_time": '',
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["movie"],
                    "event_location": {
                        "title" : 'Academy Cinemas',
                        "street" : "44 Lorne Street",
                        "region" : "Auckland 1010",
                        "country" : "New Zealand"
                    },
                }
            

            await save_to_supabase(articles)
        driver.quit()
        print("get_event_academycinemas")
    except Exception as e:
        print("An error occurred:", e)
        driver.quit()

    finally:
        driver.quit()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    temp_obj = await customize(article)
    card = customizable(temp_obj)
    title = card["event_title"]
    start_date = card["start_date"]

    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
        )
    if not existing_article.data:
        response = supabase.table("Event1").insert(card).execute()



       

def scrape_detail_page(event_url):
    event_description = ''
    try:
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(event_url)
        WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.single-movie__description"))  # Waiting for <article class="coming-soon">
            )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        description_div = soup.find('section',class_='single-movie__description')
        if description_div:
            event_description = description_div.text.strip()
        driver.quit()
    except Exception as e:
        print("An error occurred:", e)
    return event_description
