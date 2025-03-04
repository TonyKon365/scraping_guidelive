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
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode


# Function to scrape the main page and get article details
async def get_event_byronbay():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://byronbay.com/whats-on/"
    driver.get(url)
    time.sleep(4) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('article',class_='mec-event-article')
    articles = []

    for item in raws:
        event_url =item.find('a')['href']
        event_imgurl = item.find('img')['src']  
        event_title = item.find('h4').text.strip()
        start_date,start_time,location,categories,event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "byronbay",
                "target_url": "https://byronbay.com/whats-on/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":[categories],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    driver.quit()
    print("get_event_byronbay")
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
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("Event1").insert(article).execute()


def scrape_detail_page(event_url):
    
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(event_url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    start_date=''
    start_time=''
    div_date=soup.find('div',class_='mec-single-event-date')
    if div_date:
        start_date = div_date.find('span',class_='mec-start-date-label').text.strip()

    div_time = soup.find('abbr',class_='mec-single-event-time')
    if div_time:
        start_time=div_time.find('abbr',class_='mec-events-abbr').text.strip()
    # if div_time:
    #   start_time =div_time)
    
    div_location = soup.find('dd',class_='author fn org')
    location=''
    if div_location:
      location =div_location.text.strip()

    categories=''
    div_categories = soup.find('dd',class_='mec-events-event-categories')
    if div_categories:
      categories =div_categories.text.strip()
    if categories=="":
       categories="show"
    
    description=''
    div_description = soup.find('div',class_='mec-single-event-description mec-events-content')
    if div_description:
      description =div_description.text.strip()
    driver.quit()

    return start_date,start_time,location,categories,description

