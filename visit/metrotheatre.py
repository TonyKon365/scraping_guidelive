import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_metrotheatre():
    main_page_url = "https://www.metrotheatre.com.au/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(main_page_url,headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find('div',class_='le-card-container swiper-wrapper')
    # rows=raws.find_all('div',class_='evt-card evt-card-layout- medium-6 child swiper-slide cell post-40408 event type-event status-publish hentry swiper-slide-next')
    
    rows = soup.find_all('div', attrs={'data-custom-data-key': 'upcoming_events'})
    articles = []

    for item in rows:
        event_url=''
        a_tag = item.find('a', class_='bg2')

        # Check if the 'a' tag exists
        if a_tag:
            # Extract the URL from the 'href' attribute
            event_url = a_tag['href']
            print(event_url)
        else:
            print("No 'a' tag with the class 'button bg2' found")

        event_title = item.find('span',class_='h1 uppercase text2').text.strip()
        start_date = scrape_detail_page(event_url)
     
        event_description=item.find('span',class_='description text2').text.strip()
        span = soup.find('span', class_='image')
        style = span['style']
        start = style.find("(") + 1
        end = style.find(")")
        event_imgurl = style[start:end]
        articles={
                "target_id": "metrotheatre",
                "target_url": "https://www.metrotheatre.com.au/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : 'SYDNEY',
                    "street" : "624 George St SYDNEY",
                    "region" : "624 George St SYDNEY",
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_metrotheatre")
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

   
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(event_url,headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    print(soup)
    description_div = soup.find('li',class_='session-date')
    event_description=''
    if description_div:
      event_description = description_div.text.strip()
    else:
        print('not there',event_url)
    return event_description

