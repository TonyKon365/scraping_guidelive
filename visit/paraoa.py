import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_paraoa():
    main_page_url = "https://paraoa.co.nz/events/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='tribe-common-g-row tribe-events-calendar-list__event-row')
    articles = []

    for item in raws:
        event_url =item.find('a')['href']
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('h3').text.strip()
        start_date,start_time=scrape_detail_page(event_url)
        div_event_description=item.find('div',class_='tribe-events-calendar-list__event-description tribe-common-b2 tribe-common-a11y-hidden')
        event_description=div_event_description.find('p').text.strip()
        articles={
                "target_id": "paraoa",
                "target_url": "https://paraoa.co.nz/events",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date":start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : 'Whangaparaoa',
                    "street" : "719A Whangaparaoa Road",
                    "region" : "Stanmore Bay Whangaparaoa",
                    "country" : "New Zealand"
                },
            }
        
        # print(articles)
        await save_to_supabase(articles)
    print("get_event_paraoa")
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
    div_start_date = soup.find('abbr',class_='tribe-events-abbr tribe-events-start-date published dtstart')
    start_date=''
    if div_start_date:
      start_date = div_start_date['title']
    start_time=soup.find('div',class_='tribe-events-abbr tribe-events-start-time published dtstart').text.strip()
    return start_date,start_time

