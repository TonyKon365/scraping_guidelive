import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("a", class_="e-gallery-item elementor-gallery-item elementor-animated-content")
    articles = []

    for item in raws:
        # Extract the event title
        event_url = item['href']

    
        articles.append(
            {
                "target_id": "ponsonbysocialclubEvent",
                "target_url": "https://ponsonbysocialclub.com/gigs/",
                "event_title": '',
                "event_category": ['music'],
                "event_imgurl": event_url,
                "event_url": event_url,
                "start_date": '',
                "end_date": "",
                "start_time":'',
                "end_time": "",
                'add_to_cart_url':'',
                "event_description":'',
                "event_location": {
                    "title" : "AUCKLAND",
                    "street" : "152, PONSONBY RD",
                    "region" : "AUCKLAND",
                    "country" : "New Zealand"
                }
            }
        )

    return articles


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






async def get_event_from_ponsonbysocialclub():
    main_page_url = "https://ponsonbysocialclub.com/gigs/"

    articles = scrape_main_page(main_page_url)
    for article in articles:
        await save_to_supabase(article)
    print("get_event_from_ponsonbysocialclub")
