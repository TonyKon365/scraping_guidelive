import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_get_tepapaevents():
    main_page_url = "https://www.tepapa.govt.nz/visit/events"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(main_page_url,headers=headers)
 
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='card_card__zENhz')
    articles = []
    for item in raws:
        event_url ='https://www.tepapa.govt.nz'+item.find('a')['href']

        # Extract event image URL
        event_imgurl='https://www.tepapa.govt.nz'+item.find('source')['srcset']
        location=scrape_detail_page(event_url)
        event_title = item.find('h4').text.strip()  
        event_time = item.find('strong').text.strip()+' '+'2024'
        event_description=item.find('p').text.strip()
        articles={
                "target_id": "tepapa",
                "target_url": "https://www.tepapa.govt.nz",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["special"],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_get_tepapaevents")
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






def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
 
    description_div = soup.find_all('div',class_='tourDetails_tourDetail___5nO6')
    location=''
    if description_div:
      location =description_div[1].find('p').text.strip()

    return location










