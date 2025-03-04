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
async def get_event_wunderbar():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    main_page_url = "https://wunderbar.co.nz/whats-on/"
    response = requests.get(main_page_url)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(main_page_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('div',class_='fl-row-content-wrap')

    articles = []
    for item in raws:
        div_event_imgurl =item.find('img')
        if div_event_imgurl:
    
            event_url=item.find('a')['href']
            if event_url=="":
                event_url="https://wunderbar.co.nz/whats-on/"
            event_imgurl = div_event_imgurl['src']  
            event_title = item.find('h1').text.strip()
            start_date = item.find('h4').text.strip()+' '+'2024'
            start_time=''
            event_description=''
            div_start_time=item.find_all('div',class_='fl-rich-text')
            div_start_time_t=div_start_time[3].find('strong')
            if div_start_time_t:
                start_time=div_start_time_t.text.strip()
            description_div=item.find_all('div',class_='fl-module-rich-text')
            if description_div:
                event_description =description_div[2].text.strip()
            articles={
                    "target_id": "wunderbar",
                    "target_url": "https://wunderbar.co.nz/whats-on/",
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
            
            await save_to_supabase(articles)
        
    print("get_event_wunderbar")
    

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




