import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_moshtix():
    main_page_url = "https://m.moshtix.co.nz/v2"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('div',class_='featured-events')
    articles = []
   
    for item in raws:

        event_url =item.find('a')['href']
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('h2').text.strip()
        event_time = item.find('div',class_='date truncate').text.strip()

        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "moshtix",
                "target_url": "https://m.moshtix.co.nz/v2",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_moshtix")


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
    description_div = soup.find('div',class_='landing-page-description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    else:
        description_div1 = soup.find('div',class_='moduleseparator')
        if description_div1:
          event_description=' '.join(p.text.strip() for p in description_div1.find_all('p')) 
    location=soup.find('div',class_='event-venue').text.strip()
    return event_description,location

