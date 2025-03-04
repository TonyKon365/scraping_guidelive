import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
from API.Httpclient import fetch_event_data
import os
from Utils.open_ai import customize, customizable
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')) # type: ignore

Server_API_URL = 'https://www.whatsontauranga.co.nz/'

async def get_events_from_mytauranga():
    try:
        response = requests.get(Server_API_URL)
        soup = BeautifulSoup(response.content, "lxml")


        card_tags = soup.find_all('div', class_='embla-slide')             
                # for loop in card_tags
        for item in card_tags:
            event_title=item.find('div',class_='event-search-results-box-title').text.strip()
            start_date=item.find('div',class_='event-search-results-box-details one-line').find('p').text.strip()
            event_imgurl='https://www.whatsontauranga.co.nz'+item.find('img')['src']        
            event_url=item.find('a')['href']     

            location=item.find('div',class_='event-search-results-box-details two-lines').find('p').text.strip()
            event_description,end_date,start_time,end_time=scrape_detail_page(event_url)
            result={
                "target_id": 'mytauranga',
                "target_url": 'https://www.whatsontauranga.co.nz',
                "event_title": event_title,
                "event_description": event_description,
                "event_category": ['show'],
                'add_to_cart_url':event_url,
                "start_date": start_date,
                "end_date": end_date,
                "start_time":start_time,
                "end_time": end_time,
                "event_imgurl": event_imgurl,
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                        "country" : "New Zealand"
                    }
                }
            await save_to_supabase(result)
        print("get_events_from_mytauranga")
    except Exception as e:
        print("error occurs", e)
          
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
    # Make the request to the event URL
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    
    # Get the description div
    description_div = soup.find('div', class_='col-sm-12 col-xs-12')
    event_description = ''
    
    # Find all the divs with class 'event-details-date-inline'
    div_time = soup.find_all('div', class_='event-details-date-inline')
  
    # Check the number of div_time elements
    if len(div_time) > 2:  # Use len() to check the number of elements
        div_end_date = div_time[-2].find_all(class_='event-details-date')  # Use class_ for class selection
    else:
        div_end_date = div_time[0].find_all(class_='event-details-date') if div_time else []  # Handle empty div_time
    try:
    # Initialize end_date and start_time
        end_date = ''
        start_time = ''
        end_time=''
        # Extract end date and start time if available
        if div_end_date:
            if len(div_end_date) > 0:  # Check if there is at least one element
                end_date = div_end_date[0].text.strip()
            if len(div_end_date) > 1:  # Check if there is a second element
                start_time = div_end_date[1].text.strip()
                if '-' in start_time:
                    start_time, end_time = start_time.split(" - ")
                
                start_time = start_time.strip().rstrip('.')
                end_time = end_time.strip().rstrip('.')
        # Extract text from all paragraphs within the description div
        if description_div:
            paragraphs = description_div.find_all('p')
            event_description = ' '.join(p.get_text(strip=True) for p in paragraphs)
    except ValueError as e:
 
        print("Error converting the string to dictionary:", e,event_url)
    return event_description, end_date, start_time,end_time