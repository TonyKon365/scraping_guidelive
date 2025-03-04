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
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode


# Function to scrape the main page and get article details
async def get_event_dunedinnz():
    url='https://www.dunedinnz.com/visit/dunedin-events'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='carousel-cell')

    for item in raws:
        event_title=item.find('h4').text.strip( )
        event_url=item.find('a')['href']
        event_imgurl = item.find('img')['src'] 
        start_date = item.find_all('p',class_='deal-business')[1].text.strip()+' '+'2024'

        event_description=item.find('div',class_='deal-card-content').find_all('p')[2].text.strip()
            
        articles={
                    "target_id": "dunedinnz",
                    "target_url": "https://www.dunedinnz.com",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": '',
                    "event_description": event_description,
                    "start_time":'',
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["festival"],
                    "event_location": {
                        "title" : 'Dunedin',
                        "street" : "",
                        "region" : "Dunedin",
                        "country" : "New Zealand"
                    },
                }
            
        await save_to_supabase(articles)
    print("get_event_dunedinnz")


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




