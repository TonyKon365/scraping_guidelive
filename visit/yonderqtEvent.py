import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


async def get_event_from_yonderqt():
    url = "https://www.yonderqt.co.nz/category/live-music/"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    # raws = soup.find_all("ul",id='grid')
    rows=soup.find_all('div',class_='bloglistinner')
    for item in rows:
        start_date = item.find('span').text.strip()

        # Formatting the date
       

        # Extracting the event title and URL
        event_title_tag = item.find('h2').find('a')
        event_title = event_title_tag.text
        event_url = item.find('a')['href']
        event_description = item.find('p').text
        event_imgurl=''
        event_imgurl_div=item.find('img')
        if event_imgurl_div:
            event_imgurl=event_imgurl_div['src']

        article={
                "target_id": "yonderqtEvent",
                "target_url": "https://www.yonderqt.co.nz/blog/",
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": start_date,
                "end_time" : "",
                "event_imgurl": event_imgurl,
                "event_description": event_description,    
                "add_to_cart_url":event_url,
                "event_category": ['music'],
                "event_location": {
                    "title" : "Yonderqt",
                    "street" : "14 Church Street, Queenstown",
                    "region" : "Queenstown",
                    "country" : "New Zealand"
                },
            }
        await save_to_supabase(article)
    print("get_event_from_yonderqt")
 

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
    target_id=article["target_id"]
    existing_article = (
        supabase.table("guideEvent").select("*").eq("target_id", target_id).eq("event_title", title).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("guideEvent").insert(card).execute()
  

