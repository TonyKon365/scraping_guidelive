import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_worldofwearableart():
    main_page_url = "https://www.worldofwearableart.com/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('div',id='w-node-_84806eed-70d7-6c54-3546-6d4ef6b148d0-8c75b3de')
    articles = []

    for item in raws:
        event_url ='https://www.worldofwearableart.com'+item.find('a')['href']
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('div',class_='text-style-cta text-size-small').text.strip()
        event_time = item.find('div',class_='news-card_date-wrap').text.strip()
     
        event_description=item.find('h3').text.strip()
        articles={
                "target_id": "worldofwearableart",
                "target_url": "https://www.worldofwearableart.com/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["WORLD OF WEARABLEART"],
                "event_location": {
                    "title" : 'Wellington',
                    "street" : "",
                    "region" : "Wellington",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_worldofwearableart")
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

