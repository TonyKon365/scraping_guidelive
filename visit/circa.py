import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_circa():
    main_page_url = "https://www.circa.co.nz/shows/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('div',class_='gdl-package-widget')
    articles = []
    for item in raws:
        event_url =item.find('a')['href']
        event_imgurl = item.find('img')['src']  
        event_title = item.find('h2').text.strip()
        event_time = item.find('div',class_='package-date').text.strip()+' '+'2024'
        location=scrape_detail_page(event_url)
        
      
        event_description=item.find('div',class_='package-content').text.strip()
        articles={
                "target_id": "circa",
                "target_url": "https://www.circa.co.nz/shows/",
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
                    "street" : "1 Taranaki Street",
                    "region" : "Wellington",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_circa")
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)




def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    event_description=''
    description_div = soup.find_all('div',class_='package-info')
    location=description_div[1].text.strip()
  
    return location




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




