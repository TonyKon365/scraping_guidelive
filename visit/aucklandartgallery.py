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
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('prefs', {
    'profile.default_content_setting_values.cookies': 2  # Block third-party cookies
})

def convert(timestamp_ms):
    timestamp_s = timestamp_ms / 1000
    date_time = datetime.fromtimestamp(timestamp_s)
# Format the date to a readable string
    formatted_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date

async def get_event_aucklandartgallery():
    main_page_url = "https://www.aucklandartgallery.com/search/events?date-range=future"
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(main_page_url)
    # WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
    time.sleep(8)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('article')
    # print(soup)
    for item in raws:
        event_title=item.find('h5').text.strip()
        start_date=item.find('time',class_='date start').text.strip()
        div_end_date=item.find('time',class_='date end')
        end_date=''
        if div_end_date:
             end_date=div_end_date.text.strip()
        event_url='https://www.aucklandartgallery.com'+item.find('a')['href']    
        event_imgurl=item.find('img')['src']
        event_description=scrape_detail_page(event_url)
        dec=item.find_all('p')
        start_time=dec[1].text.strip()
        if 'Every' in start_time:
            continue
        else:
            
            articles={
                "target_id": "aucklandartgallery",
                "target_url": "https://www.aucklandartgallery.com",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": end_date,
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["show"],
                "event_location": {
                    "title" : 'Sydney',
                    "street" : "",
                    "region" : "Sydney City",
                    "country" : "Australia"
                },
            }
            await save_to_supabase(articles)
 
    driver.quit()
    print("get_event_moget_event_aucklandartgalleryshtixAu")

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
    description_div = soup.find('div',class_='event-description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 

    return event_description

