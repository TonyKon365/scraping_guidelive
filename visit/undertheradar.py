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


supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))  # type: ignore

Server_API_URL = 'https://www.undertheradar.co.nz/utr/gig_guide/&limit=200'

async def get_events_from_undertheradar():
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(Server_API_URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
  
    card_tags = soup.find_all('div', class_='vevent')
    print(len(card_tags))

    for card_tag in card_tags:
        target_id = 'undertheradar'
        target_url = 'https://www.undertheradar'
        title_tag = card_tag.find('a', class_='summary url')
        event_title = title_tag.text if title_tag else ""
        detail_url = 'https://www.undertheradar.co.nz' + title_tag['href']
        res_detailed_data = requests.get(detail_url)
        soup_detailed = BeautifulSoup(res_detailed_data.content, 'html.parser')
                    
        description_tag = soup_detailed.find('p', class_='description')
        event_description = description_tag.text if description_tag else ""
        event_category = ["Gig"]
                    
        location_tag = card_tag.find('div', class_='venue-title location vcard')
        event_location = location_tag.text if location_tag else ""
      
        event_time = card_tag.find('span',class_='lite').text.strip()
        img_tag = soup_detailed.find('img', id='myImage')
        event_imgurl = img_tag.get('src') if img_tag else ""
        result = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": event_category,
                    "add_to_cart_url": detail_url,
                  
                    "start_date": event_time,
                    "start_time": "",  # Add proper time parsing if needed
                    "end_date": '',
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": "",
                        "country": "New Zealand"
                    },
                }
        await save_to_supabase(result)
    driver.quit()
    print("get_events_from_undertheradar")




async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]

    # existing_article = (
    #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
    #     )
    # if not existing_article.data:
        response = supabase.table("Event1").insert(article).execute()




url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

