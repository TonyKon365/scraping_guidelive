from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time

from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--ss")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Initialize the WebDriver (make sure to specify the path to your chromedriver if not in PATH)


async def get_event_bandsintown():
    driver = webdriver.Chrome(options=chrome_options)
# Open the target URL
    url = "https://www.bandsintown.com/c/sydney-australia/this-month/genre/all-genres"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "AtIvjk2YjzXSULT1cmVx")))
    try:
        time.sleep(1)
    except Exception as e:
        print("Error occurred while trying to click 'View All':", e)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Find all event items using Beautiful Soup
    event_items = soup.find_all('div', class_='AtIvjk2YjzXSULT1cmVx')
    for item in event_items:
        # Extract relevant information from each event item
        event_title = item.find('div',class_='_5CQoAbgUFZI3p33kRVk').text.strip()  # Example selector for the title
        event_imgurl=item.find('img')['src']
        start_date=item.find('div',class_='r593Wuo4miYix9siDdTP').text.strip()

        date_part, time_part = start_date.split('-')

        # Strip whitespace from both parts
        start_date = date_part.strip()+' '+'2024'
        start_time = time_part.strip()
        location=item.find('div',class_='bqB5zhZmpkzqQcKohzfB').text.strip()
        event_url=item.find('a')['href']
        event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "bandsintown",
                "target_url": "https://www.bandsintown.com/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["show"],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)

    print("get_event_bandsintown")
    driver.quit()

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(event_url, headers=headers)
  
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='y6bPrd1MQ2AGJWSu6ogJ')
    event_description=''
    if description_div:
      event_description = description_div.text.strip()
    else:
        description_div1=soup.find('div',class_='SJ33jtevZvYqdSqdsq4c')
        if description_div1:
            event_description=description_div1.text.strip()
    return event_description
