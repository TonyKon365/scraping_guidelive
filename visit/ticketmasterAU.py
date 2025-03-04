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
import random
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")

async def get_event_ticketmasterAU():
    await get_event_ticketmasterAU_music()
    # await get_event_ticketmasterAU_arts()
    # await get_event_ticketmasterAU_sports()
    # await get_event_ticketmasterAU_family()


async def get_event_ticketmasterAU_music():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.com.au/section/music"
    driver.get(url)
    
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'sc-1nyzlro-1'))  # Wait for card elements to be present
        )
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    print(len(raws))
    articles = []
    for item in raws:
        start_date=''
        end_date=''
        event_url =item.find('a')['href']
        start_time=''
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
        start_date=item.find('div',class_='sc-1evs0j0-0 jifFsK').text.strip()
        div_end_date=item.find('span',class_='VisuallyHidden-sc-8buqks-0 lmhoCy')

        div_time=item.find('span',class_='sc-1idcr5x-1 dieHWG')
        if div_time:
            start_time=div_time.find('span').text.strip()
        if div_end_date:
            end_date=div_end_date.find('span').text.strip()
            end_date=end_date
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description=''
        if(start_time==""):   
           event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterAU",
                "target_url": "https://www.ticketmaster.com.au/",
                "event_imgurl": '',
                "event_title": event_title,
                "start_date":start_date,
                "end_date": end_date,
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":"music",
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
        await save_to_supabase(articles)
    print("get_event_ticketmasterAU_music")
    driver.quit()

async def get_event_ticketmasterAU_arts():
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
                "target_id": "ticketmasterAU",
                "target_url": "https://www.ticketmaster.com.au/",
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
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)

    print("get_event_ticketmasterAU_arts")
    driver.quit()

async def get_event_ticketmasterAU_sports():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.com.au/section/sports"
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
                "target_id": "ticketmasterAU",
                "target_url": "https://www.ticketmaster.com.au/",
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
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_ticketmasterAU_sports")
    driver.quit()    

async def get_event_ticketmasterAU_family():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ticketmaster.com.au/section/family-attractions"
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    raws = soup.find_all('li',class_='sc-1nyzlro-1 jHDhvy')
    print(len(raws))
    articles = []
    for item in raws:

        event_url =item.find('a')['href']
        event_title = item.find('span',class_='sc-fyofxi-5 gJmuwa').text.strip()
       
        location=item.find('span',class_='sc-fyofxi-7 PpnvD').text.strip()
        event_description,event_time,event_imgurl=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketmasterAU",
                "target_url": "https://www.ticketmaster.com.au/",
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
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_ticketmasterAU_family")
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
    print('scrape_detail_page',event_url)
    event_description=''
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(event_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'moduleseparator'))  # Wait for card elements to be present
        )
        time.sleep(random.uniform(1, 5))
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        description_div = soup.find('div',class_='moduleseparator page fr-view')

        if description_div:
            event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 



        driver.quit()
    except Exception as e:
        print("Error occure in scraping detail page':", e)


    return event_description

def convert(input_date):
    date_object = datetime.strptime(input_date, "%d/%m/%y")
    # Format the date to the desired output format
    output_date = date_object.strftime("%Y-%m-%d")
    return output_date