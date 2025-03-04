import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_lakehousearts():
    main_page_url = "https://lakehousearts.org.nz/calendar/8/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='event-lists')
    articles = []
    for item in raws:
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('h4').text.strip()
        date_p = item.find('p', text=lambda t: t and 'Date:' in t)
        time_p = item.find('p', text=lambda t: t and 'Time:' in t)
        venue_p = item.find('p', text=lambda t: t and 'Venue:' in t)

        # Extract the date, time, and venue from the paragraphs
        start_date = date_p.text.split('Date:')[1].strip() if date_p else None
        start_time = time_p.text.split('Time:')[1].strip() if time_p else None
        location = venue_p.text.split('Venue:')[1].strip() if venue_p else None


        articles={
                "target_id": "lakehousearts",
                "target_url": "https://lakehousearts.org.nz",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": 'event_description',
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":'https://lakehousearts.org.nz/calendar/8/',
                "event_category":["music"],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_lakehousearts")
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




