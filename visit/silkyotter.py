import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
import time
from Utils.open_ai import customize, customizable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Function to scrape the main page and get article details
async def get_event_silkyotter():
    driver = webdriver.Chrome(options=chrome_options)
    main_page_url = "https://www.silkyotter.co.nz/"
    driver.get(main_page_url)
    try:
        time.sleep(8)  # Adjust if necessary
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        rows=soup.find_all('li',class_='v-film-list-film')
       
        for item in rows:
            # Extract relevant information from each event item
            event_title = item.find('div',class_='v-film-title').text.strip()  # Example selector for the title
          
            event_imgurl=item.find('img')['src']
      
           
            event_url="https://www.silkyotter.co.nz"+item.find('a')['href']
            event_description,start_date=scrape_detail_page(event_url)
            articles={
                    "target_id": "silkyotter",
                    "target_url": "https://www.silkyotter.co.nz/",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": '',
                    "event_description":event_description,
                    "start_time": '',
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["movie"],
                    "event_location": {
                        "title" : 'SILKY OTTER CINEMAS',
                        "street" : "539 Main Street,",
                        "region" : "Palmerston North Central, Palmerston",
                        "country" : "New Zealand"
                    },
                }
            

            await save_to_supabase(articles)

    
    except Exception as e:
        print("An error occurred:", e)
        driver.quit()
        print("get_event_silkyotter")
    finally:
        driver.quit()
        print("get_event_silkyotter")

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
        # Optionally, wait for a specific element that indicates content is loaded
    time.sleep(5)  # Adjust if necessary
        # Get the page source and parse it with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    print(soup)
    div=soup.find('div',class_='v-description-list-item v-film-synopsis')
                
    event_description = div.find('dd').text.strip()
    event_description=''
    div_date=soup.find('div',class_='v-film-summary__primary')

    start_date=''
    div_start_date=div_date.find_all('span',class_='v-display-text-part')
    if div_start_date:
        start_date=div_start_date[1].text.strip()
    return event_description,start_date

