import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

def scrape_event_description(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    event_description=soup.find('p',class_='sc-bdfBwQ sc-gsTCUz jAgast ewgwqq').text.strip()
    start_date=soup.find('div',class_='sc-bdfBwQ sc-hKgILt jAgast beOqPw').text.strip()
    return event_description,start_date
    
     


async def get_event_from_audiologytix():
    main_page_url = "https://audiologytouring.flicket.co.nz/"
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(main_page_url)
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-bdfBwQ gHwjME"))
            )
    time.sleep(1) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws=soup.find_all("div", class_="sc-bdfBwQ gHwjME")
    articles = []
    for items in raws:
        items=items.find_all("div", class_="sc-bdfBwQ gHwjME")
        for item in items:
            event_url = 'https://audiologytouring.flicket.co.nz'+item.find('a')['href']
            event_imgurl =item.find('img')['src']
            event_title=item.find('div',class_="sc-bdfBwQ sc-gsTCUz ghsCGa kNgGyf").text
            event_description ,start_date= scrape_event_description(event_url)
            location=item.find('div',class_='sc-bdfBwQ sc-gsTCUz stAZQ dmOHzK').text.strip()
            article={
                    "target_id": "audiologytouring",
                    "target_url": "https://audiologytouring.flicket.co.nz/",
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "event_title": event_title,
                    "start_date":start_date,  # Convert to string
                    "end_date": '',
                    "event_description":'',
                    "start_time": '',  # Convert to string
                    "end_time": "",
                    "event_category":["tour"],
                    "add_to_cart_url":event_url,
                    "event_location": {
                        "title" : location,
                        "street" : '',
                        "region" : '',
                        "country" : "New zealand"
                    },
                }
            await save_to_supabase(article)
        

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
    target_id = article["target_id"]
    existing_article = (
            supabase.table("Event1").select("*").eq("target_id", target_id).eq("event_title", title).execute()
        )

    if not existing_article.data:
        response = supabase.table("Event1").insert(article).execute()



