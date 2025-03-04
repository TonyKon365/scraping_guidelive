import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from Utils.open_ai import customize, customizable

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

async def get_event_from_sanfran():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.sanfran.co.nz/whats-on"
    page=1
    while(1):
        try:
            url = f'https://www.sanfran.co.nz/whats-on?Page={page}'
            driver.get(url)
            WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.event-ticket-link"))
                )
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            raws=soup.find_all('a',class_='event-ticket-link')
            if raws==None:
                break
            print(len(raws))
            for item in raws:
                event_url ='https://www.sanfran.co.nz'+item['href']
                div_event_imgurl=item.find('img')
                if div_event_imgurl:
                    event_imgurl=div_event_imgurl['src']
                start_date=''
                time_tag = item.find('time', class_='ns-rpxx7c')
                if time_tag:
                    day_span = time_tag.find('span', class_='ns-1x6z45a')
                    month_span = time_tag.find_all('span')[1]
                    
                    # Extract text and strip any extra whitespace
                    day = day_span.get_text(strip=True) if day_span else ''
                    month = month_span.get_text(strip=True) if month_span else ''
                    
                    # Format the date
                    start_date = f"{day} {month}"+" "+'2024'
                    event_title,start_time,event_description = scrape_detail_page(event_url)

                obj = {
                        "target_id": 'sanfran',
                        "target_url": 'https://www.sanfran.co.nz',
                        "event_title": event_title,
                        "event_description": event_description,
                        "event_category": ['show'],
                        "start_date": start_date,  # Convert to string
                        "start_time": '',  # Convert to string
                        "end_date": start_date,
                        "end_time": "",
                        "add_to_cart_url": event_url,
                        "event_imgurl": event_imgurl,
                        "event_location": {
                            "title" : "San Fran",
                            "street" : "171 Cuba Stree",
                            "region" : "Te Aro, Wellington 6011",
                            "country" : "New Zealand"
                        },
                        }
                await save_to_supabase(obj)
            page += 1
        except Exception as e:
            print(f"Error parsing main page: {e}")
            driver.quit()
            break
    print("get_event_from_sanfran")


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")

    event_title = soup.find('h1').text.strip()
    start_time=''
    description_div = soup.find('div', {'data-testid': 'aedp-event-information-block'})

    start_time=description_div.find('time')
    if description_div:
        start_time=description_div.get_text()
    event_description=''
    des=soup.find('section',class_='ns-ohmmtl')
    if des:
        event_description =des.text.strip()
    else:
        print("Description div not found")

    

    return event_title,start_time,event_description


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









