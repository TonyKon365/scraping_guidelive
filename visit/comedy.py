import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable
from datetime import date

# Function to scrape the main page and get article details
async def get_event_comedy():
    main_page_url = "http://www.comedy.co.nz/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='leftbanner panelbkgrd equal')
    articles = []
    for item in raws:
        event = item.find('a')

        start_date = date.today().isoformat()
        event_url ="http://www.comedy.co.nz"+item.find('a')['href']

        # Extract event image URL
  
        event_imgurl = "http://www.comedy.co.nz"+item.find('img')['src']  
        event_title = item.find('h4').text.strip()
       
      
        event_description=item.find('p').text.strip()
        articles={
                "target_id": "comedy",
                "target_url": "http://www.comedy.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["comedy"],
                "event_location": {
                    "title" : 'Auckland Central',
                    "street" : "321 Queen Street,",
                    "region" : "Auckland Central,",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_comedy")
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
    description_div = soup.find('div',class_='landing-page-description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    else:
        description_div1 = soup.find('div',class_='moduleseparator')
        if description_div1:
          event_description=' '.join(p.text.strip() for p in description_div1.find_all('p')) 

    return event_description

