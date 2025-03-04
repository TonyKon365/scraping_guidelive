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

chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

async def get_event_ticketmasterNZ():
    await get_event_ticketmasterNZ_music()
    await get_event_ticketmasterNZ_arts()
    await get_event_ticketmasterNZ_sports()
    await get_event_ticketmasterNZ_family()


async def get_event_ticketmasterNZ_music():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.co.nz/section/music"
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    articles = []
    for item in raws:

        event_url =item.find('a')['href']
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
       
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description,event_time,event_imgurl=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterNZ",
                "target_url": "https://www.ticketmaster.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":"music",
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        await save_to_supabase(articles)
    print("get_event_ticketmasterAU_music")
    driver.quit()

async def get_event_ticketmasterNZ_arts():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.com.au/section/arts-theatre-comedy"
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    articles = []
    for item in raws:

        event_url =item.find('a')['href']
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
       
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description,event_time,event_imgurl=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterNZ",
                "target_url": "https://www.ticketmaster.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":"arts-theatre-comedy",
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)

    print("get_event_ticketmasternz_arts")
    driver.quit()

async def get_event_ticketmasterNZ_sports():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.co.nz/section/sports"
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    articles = []
    for item in raws:

        event_url =item.find('a')['href']
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
       
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description,event_time,event_imgurl=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterNZ",
                "target_url": "https://www.ticketmaster.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":"sports",
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_ticketmasternz_sports")
    driver.quit()    

async def get_event_ticketmasterNZ_family():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.co.nz/section/family-attractions"
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    articles = []
    for item in raws:

        event_url =item.find('a')['href']
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
       
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description,event_time,event_imgurl=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterNZ",
                "target_url": "https://www.ticketmaster.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":"family",
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_ticketmasternz_family")
    driver.quit()
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
    # time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    description_div = soup.find('div',class_='moduleseparator page fr-view')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    event_time=''
    div_event_time=soup.find('div',id='event-summary-date')
    if div_event_time:
        event_time=div_event_time.text.strip()
    div_event_imgurl=soup.find('img')
    event_imgurl=''
    if div_event_imgurl:
        event_imgurl="https:"+div_event_imgurl['src']
    driver.quit()
    return event_description,event_time,event_imgurl


