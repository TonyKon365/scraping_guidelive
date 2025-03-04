import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable


async def get_event_croxtonparkhotel():
    main_page_url = "https://www.croxtonparkhotel.com.au/whats-on"
    page = 0
    response = requests.get(f"{url}?b138d03a_page={main_page_url}")
    soup = BeautifulSoup(response.content, "html.parser")
    articles=[]
    items = soup.find_all("div", class_="carousel-cell is-selected")
    print("items",len(items))
    if(len(items)==0):
        print("get_event_croxtonparkhotel")
        
    for item in items:
        event_imgurl=''
        event_image_div=item.find('img')
    #  if event_image_div:   
    #      event_imgurl = 'https://www.croxtonparkhotel.com.au'+event_image_div['src']

        print("event_image_div",event_image_div)
        event_url = 'https://www.croxtonparkhotel.com.au'+item.find('a')['href']
    
        article={
                    "target_id": "croxtonparkhotelEvent",
                    "target_url": "https://www.croxtonparkhotel.com.au/",
                    "event_title": 'croxtonparkhotel',
                    "event_category": ['music'],
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "start_date": '',
                    "end_date": "",
                    "start_time":'',
                    "end_time": "",
                    'add_to_cart_url':event_url,
                    "event_description":'',
                    "event_location": {
                        "title" : "Thornbury, VIC, 3071",
                        "street" : "607 High St",
                        "region" : "Thornbury",
                        "country" : "New Zealand"
                    }
                }
        await save_to_supabase(article) 
        
    print("get_event_croxtonparkhotel")

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time= article["start_time"]
    target_id=article["target_id"]
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("guideEvent").insert(card).execute()



