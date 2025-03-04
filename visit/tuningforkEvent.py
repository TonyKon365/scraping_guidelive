from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable
import requests


# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


def scrape_detail_page(event_url):
 
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    time_element = soup.find('time', class_='ns-msp0op')
    datetime_str = time_element['datetime']
    start_date = datetime_str.split('T')[0]

    p_element = soup.find('p', {'data-testid': 'aedp-event-information-block-times'})
    time_element = p_element.find('time')
    if time_element:
        time_str = time_element.text.strip()
        formatted_time = time_str + ":00"
    else:
        formatted_time=''
    event_description=''
    content_div = soup.find('div', {'data-component': 'ContentRichTextModule'})
    if content_div:
        event_description = ' '.join([p.get_text() for p in content_div.find_all('p')])
    else:
        event_description=''
    event_imgurl=soup.find_all('img')[1]['src']
    
    event_imgurl=soup.find('img')['src']
    return event_imgurl,start_date,formatted_time,event_description

async def get_event_from_tuningfork():
    
    url='https://www.tuningfork.co.nz/whats-on'
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)

    # time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    raws = soup.find_all("a", class_="ns-1i3v6r1")
    print(len(raws))
    print(soup)
    print(raws[0])
    for item in raws:
        event_url = 'https://www.tuningfork.co.nz/'+item['href']
        event_title = item.find('p', class_='ns-1od8y9y').text.strip()

        event_imgurl,start_date, start_time, event_description = scrape_detail_page(event_url)
        article={
                "target_id": "tuningforkEvent",
                "target_url": "https://www.tuningfork.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,   
                'event_category': ['Music'],
                "end_date": start_date,
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url": event_url,
                "event_location": {
                    "title" : "Auckland",
                    "street" : "42 Mahuhu Crescent",
                    "region" : "Parnell",
                    "country" : "New Zealand",
                },
            }
        await save_to_supabase(article)

    print("get_event_from_tuningfork")
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to check for duplication and insert if not duplicated
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




