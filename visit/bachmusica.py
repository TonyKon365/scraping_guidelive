import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_bachmusica():
    main_page_url = "https://bachmusica.com/whats-on/page/"
    page = 1
    while True:
        response = requests.get(f"{main_page_url}{page}")
        
        soup = BeautifulSoup(response.content, "lxml")
        if soup is None:
            break
        raws = soup.find_all('article',class_='hitmag-post')

        if not raws:
            print(f"No 'dgc-listing' div found on page {page}. Ending loop.")
            break
        articles = []
        for item in raws:

            event_url =item.find('a')['href']

            # Extract event image URL
            event_title = item.find('h3').text.strip()
            event_time=''
            div_event_time=item.find('time')
            if div_event_time:
                event_time=div_event_time.text.strip()
            div_event_description=item.find('div',class_='entry-summary').find('p')
            event_description=''
            if div_event_description:
                event_description=div_event_description.text.strip()
            articles={
                    "target_id": "bachmusica",
                    "target_url": "https://bachmusica.com/whats-on/",
                    "event_imgurl": '',
                    "event_title": event_title,
                    "start_date": event_time,
                    "end_date": '',
                    "event_description": event_description,
                    "start_time": '',
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["music"],
                    "event_location": {
                        "title" : 'Aotea Square',
                        "street" : "Queen Street",
                        "region" : "Auckland",
                        "country" : "New Zealand"
                    },
                }
            

            await save_to_supabase(articles)
        page += 1
    print("get_event_bachmusica")

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

