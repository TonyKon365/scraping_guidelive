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

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

target_id = 'hawkesbaynz'
target_url = 'https://www.hawkesbaynz.com'
Server_API_URL = "https://www.hawkesbaynz.com/whats-on/events/the-whats-on-guide/?genre=0&eventlocation=0&eventdate=316"

async def get_events_from_hawkesbaynz():
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(Server_API_URL)
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.EventCard"))
    )
    time.sleep(2)
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-close[data-dismiss='modal']"))
    )
    close_button.click() 
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    print(soup)
    result = []

    card_tags = soup.find_all('div', class_='EventCard')


    for card_tag in card_tags:
        try:
            image = card_tag.find('div', class_='image')
            a_tag = image.find('a') if image else None
            detail_url = target_url + a_tag.get('href') if a_tag else ""
            event_imgurl = a_tag.get('data-src') if a_tag else ""

            date_tag = image.find('div', class_='dates') if image else None
            event_time = date_tag.text.strip() if date_tag else ""

            title = card_tag.find('div', class_='title')
            title_tag = title.find('div', class_='listingName') if title else None
            event_title = title_tag.text.strip() if title_tag else ""

            if not event_title:
                continue

            label = title.find('div', class_='cat-events') if title else None
            event_category = label.text.strip() if label else ""

            hidden = title.find('div', class_='hidden') if title else None
            location = hidden.find('div', {'itemprop': 'location'}) if hidden else None
            address = location.find('meta', {'itemprop': 'address'}) if location else None
            event_location = address.get('content') if address else ""

            description = hidden.find('span', {'itemprop': 'description'}) if hidden else None
            event_description = description.text.strip() if description else ""
   


            response1 = requests.get(detail_url)
            soup1 = BeautifulSoup(response1.content, "lxml")
            description_div = soup1.find('div',class_='free-text')

        
            div_date=description_div.find_all('p')
            for item in div_date:
                start_date=item.text.strip()
                obj = {
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': [event_category],
                'event_imgurl': event_imgurl,
                "start_date": start_date,
                "end_date": '',
                "start_time": "",
                "end_time": "",
                "add_to_cart_url": detail_url,
                "event_location": {
                    "title": event_location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                },
            }
                await save_to_supabase(obj)
        except Exception as e:
            print(f"Error processing an event: {e}")
            driver.quit()
            continue
    print("get_events_from_hawkesbaynz")
    driver.quit()




 

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




url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)