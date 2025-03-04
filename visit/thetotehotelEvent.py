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


# Function to scrape the main page and get article details
async def get_event_from_thetotehotel():
    
    page=0
   
    driver = webdriver.Chrome(options=chrome_options)
    while(1):
        try:
            main_page_url = f'https://thetotehotel.com/gig-guide/#q=&hPP=20&p={page}&is_v=1'
            driver.get(main_page_url)
            WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ais-hits--item"))
                )
            time.sleep(1) 
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            raws = soup.find_all('div',class_='ais-hits--item event-container')
            articles = []
            for item in raws:         
                event_url=item.find('a')['href']
                event_imgurl = item.find('img')['src']  
                event_title = item.find('h3').text.strip()
                event_description,start_date,location =scrape_detail_page(event_url)
                end_date=''
                start_time=''
             
                if '-' in start_date:
                     start_date=start_date                 
                else:
                    start_date=start_date.split(',')[1].strip()
                    if 'PM' in start_date:
                        start_date = start_date.replace('PM', 'pm')        
                    dt = datetime.strptime(start_date, "%d %B %Y %I:%M %p")
                    start_date = dt.strftime("%Y-%m-%d")
                    start_time = dt.strftime("%H:%M:%S")

                articles={
                    "target_id": "thetotehotel",
                    "target_url": "https://thetotehotel.com/",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "event_description": event_description,
                    "start_time":start_time,
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["gig-guide"],
                    "event_location": {
                        "title" : location,
                        "street" : "",
                        "region" : "",
                        "country" : "Australia"
                        },
                    }
                    
                await save_to_supabase(articles)
            
            page += 1
        except Exception as e:
            print(f"Error parsing main page: {e}")
            driver.quit()
            break
    print("get_event_thetotehotel")
    

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
      event_description = description_div.text.strip()
    div_event_detail_item=soup.find_all('div',class_='event-details-item')
    
    location=div_event_detail_item[0].find('span').text.strip()
    start_date=div_event_detail_item[1].find('span').text.strip()
    return event_description,start_date,location
