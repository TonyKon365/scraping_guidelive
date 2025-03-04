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
from selenium.webdriver.chrome.options import Options
import time
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Function to scrape the main page and get article details
async def get_event_southlandnz():
    driver = webdriver.Chrome(options=chrome_options)

    url = "https://southlandnz.com/events/"
    driver.get(url)
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "item")))
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    div=soup.find('div',class_='content grid')
    raws = div.find_all('div',class_='item')
    articles = []
    print(len(raws))
    for item in raws:
        event_url ='https://southlandnz.com'+item.find('a')['href']
        event_imgurl = item.find('img')['data-lazy-src']
        event_title = item.find('h4').text.strip()
        event_time=item.find('span',class_='mini-date-container').text.strip()+' '+'2024'
        location=item.find('li',class_='locations').text.strip()
        event_description,start_time,category=scrape_detail_page(event_url)
        articles={
                "target_id": "southlandnz",
                "target_url": "https://southlandnz.com/events/events-southland/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":[category],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    driver.quit()
    print('get_event_southlandnz')
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
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(event_url)
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "category")))
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    description_div = soup.find('p',class_='about')
    event_description=''
    if description_div:
      event_description = description_div.text
    div_start_time=soup.find('div',class_='times')
    if div_start_time:
        start_time=div_start_time.find('dd').text.strip()
    category=soup.find('div',class_='category two-line-wrap').text.strip()
    return event_description,start_time,category

