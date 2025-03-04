import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from supabase import create_client, Client
from Utils.open_ai import customize, customizable

main_page_url = "https://hotelesplanade.com.au/whats-on/"
# Function to scrape the main page and get article details
async def get_event_from_hotelesplanade():
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    
    div=soup.find('div',class_='c-event-carousel')
    
    raws = soup.find_all('div', class_='c-event-card')
    print(len(raws))
    print(raws[4])
    for item in raws:
        
        event_div=item.find('a', class_='c-event-card-title')
        
        event_url=event_div['href']
        event_title=event_div.get_text(strip=True)
        event_description,event_time=scrape_detail_page(event_url)

        image_divs = soup.find_all('div', class_='bg-cover')

        # Extract and print the image URLs
        event_imgurl = [div['data-bg'] for div in image_divs if 'data-bg' in div.attrs]
 
        articles={
                "target_id": "hotelesplanadeEvent",
                "target_url": "https://hotelesplanade.com.au/gershwin-room/",
                "event_title": event_title,
                "event_category": ['hotel'],
                'event_description':event_description,
                'add_to_cart_url':event_url,
                "event_imgurl": event_imgurl[0],
            
                "start_date": event_time,
                "end_date": '',
                "start_time":'',
                "end_time": "",
                "event_location": {
                    "title" : 'St Kilda',
                    "street" : "11 The Esplanade",
                    "region" : "St Kilda, VIC, 3182",
                    "country" : "Australia"
                },
                
            }
        await  save_to_supabase(articles)

    print("get_event_from_hotelesplanade")

def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    description_div = soup.find('div', class_='c-event-single__description')
    event_description=''
    event_time=soup.find('div', class_='c-event-single__subtitle').get_text(strip=True)+' '+'2024'
    
    # Extract text from all paragraphs within the div
    if description_div:
        paragraphs = description_div.find_all('p')
        event_description = ' '.join(p.get_text(strip=True) for p in paragraphs)
    return event_description,event_time

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time = article["start_time"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).execute()
    )

    if not existing_article.data:
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("Event1").insert(article).execute()
        print(f"Inserted: {response.data}")



