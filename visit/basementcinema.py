import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable
from datetime import date

# Function to scrape the main page and get article details
async def get_event_basementcinema():
    main_page_url = "https://www.basementcinema.co.nz/now-showing.html"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('li',class_='cmsItemLI')
    articles = []
    for item in raws:
        event_url ='https://www.basementcinema.co.nz'+item.find('a')['href']
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('div',class_='cmsTitle').text.strip()
        today = date.today().isoformat()
  
        event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "basementcinema",
                "target_url": "https://www.basementcinema.co.nz/now-showing.html",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": today,
                "end_date": today,
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["movie"],
                "event_location": {
                    "title" : 'The Wall and Basement Cinemas',
                    "street" : "1140 Hinemoa Street",
                    "region" : "Rotorua",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_basementcinema")
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
    description_div = soup.find('div',class_='cmsBlogText')
    event_description=''
    if description_div:
      event_description = description_div.text.strip()


    return event_description

