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
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode


# Function to scrape the main page and get article details
async def get_event_abstract():
    url = "https://abstract.net.au/"
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(4) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
  
    raws = soup.find_all('div',class_='project')
    articles = []

    for item in raws:
        event_url=''
        a_tag = item.find_all('a')
        event_url = a_tag[0]['href']

        event_title = a_tag[0]['title']
        start_date=a_tag[2].text.strip()
        event_description = scrape_detail_page(event_url)
     
    
        event_imgurl = item.find('img')['src']
        articles={
                "target_id": "abstract",
                "target_url": "https://abstract.net.au/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["tour"],
                "event_location": {
                    "title" : 'Australia',
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    driver.quit()
    print("get_event_abstract")
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id=article["target_id"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("Event1").insert(card).execute()


def scrape_detail_page(event_url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(event_url, headers=headers)
        
    soup = BeautifulSoup(response.content, "lxml")
    print(soup)
    description_div = soup.find('div',class_='et_pb_post_content')
    event_description=''
    if description_div:
      event_description = description_div.text.strip()
    else:
        print('not there',event_url)
    return event_description

