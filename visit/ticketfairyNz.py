import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

# Function to scrape the main page and get article details
async def get_event_ticketfairyNz():
    main_page_url = "https://www.ticketfairy.com/search-results?type=upcoming&search=New%20Zealand%20"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div',class_='events-carousel')
    articles = []
    for item in raws:
        event_url ="https://www.ticketfairy.com"+item.find('a')['href']
        event_imgurl = "https://www.ticketfairy.com"+item.find('img')['src']  
        event_title = item.find('span',class_='event-listing-title').text.strip()

        start_date = item.find('div', class_='col-60 left').find_all('span')[0].text.strip()  # Date

        start_time_div = item.find('div', class_='col-60 left').find_all('span')[1].text.strip()  # Time
        input_time = start_time_div.split('/')[-1].strip()
        time_object = datetime.strptime(input_time, "%I:%M %p")

        start_time = time_object.strftime("%H:%M:%S")

        # Extracting event location
        event_location_parts = item.find('div', class_='event-location').find_all('span')
        event_location = ', '.join(part.text.strip() for part in event_location_parts)  # Combine location parts
        event_category=''
        event_category_div=item.find('span',class_='tf-event-tags')
        if event_category_div:
            event_category=event_category_div.text

        event_description=scrape_detail_page(event_url)
        articles={
                "target_id": "ticketfairyNZ",
                "target_url": "https://www.ticketfairy.com/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":[event_category],
                "event_location": {
                    "title" : event_location,
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)
    print('get_event_ticketfairyNz')
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
    description_div = soup.find('div',class_='description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) +' '.join(div.get_text(strip=True) for div in description_div.find_all('div'))

    return event_description

