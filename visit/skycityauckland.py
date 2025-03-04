import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

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
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')

# Function to scrape the main page and get article details
async def get_event_skycityauckland():
    url='https://skycityauckland.co.nz/whats-on/?tag=CASINO'
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    time.sleep(2) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
  
    print(soup)
    raws = soup.find_all('a',class_='hover whats-on-flex item thisclass')
    print(len(raws))
    articles = []
   
    for item in raws:

        div_event_imgurl =item.find('img')
        if div_event_imgurl:
            event_url=item.find('a')['href']
            event_imgurl = div_event_imgurl['src']  
            event_title = item.find('h1').text.strip()
            start_date = item.find('h4').text.strip()+' '+'2024'
            start_time=''
            div_start_time=item.find_all('div',class_='fl-rich-text')
            div_start_time_t=div_start_time[3].find('strong')
            if div_start_time_t:
                start_time=div_start_time_t.text.strip()
            event_description=item.find('div',class_='fl-module-content fl-node-content').text.strip()
            
            articles={
                    "target_id": "skycityauckland",
                    "target_url": "https://skycityauckland.co.nz/whats-on/",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": '',
                    "event_description": event_description,
                    "start_time":start_time,
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["show"],
                    "event_location": {
                        "title" : 'Wunderbar',
                        "street" : "14 Canterbury Street",
                        "region" : "Lyttelton",
                        "country" : "New Zealand"
                    },
                }
            
            print(articles)
            await save_to_supabase(articles)
    print("get_event_wunderbar")


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
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='landing-page-description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    else:
        description_div1 = soup.find('div',class_='moduleseparator')
        if description_div1:
          event_description=' '.join(p.text.strip() for p in description_div1.find_all('p')) 
    location=soup.find('div',class_='event-venue').text.strip()
    return event_description,location

