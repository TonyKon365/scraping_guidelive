import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from datetime import datetime
from Utils.open_ai import customize, customizable
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Function to scrape the main page and get article details
async def get_event_govettbrewster():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://govettbrewster.com/whats-on"
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='schedule-calendar')
    articles = []
    today = date.today().isoformat()
    for item in raws:

        event_url ="https://govettbrewster.com"+item.find('a')['href']

        # Extract event image URL
  
        event_imgurl = item.find('img')['src']  
        event_title = item.find('div',class_='schedule-title').text.strip()
        event_time = item.find('span',class_='metaData').text.strip()
      
        event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "govettbrewster",
                "target_url": "https://govettbrewster.com/events",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": today,
                "end_date": '',
                "event_description": event_description,
                "start_time": event_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["movie"],
                "event_location": {
                    "title" : 'govettbrewster',
                    "street" : "42 Queen Street",
                    "region" : "New Plymouth, 4310",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_govettbrewster")
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
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='col-second')
    event_description=''
    if description_div:
      event_description =description_div.text.strip()

    return event_description

