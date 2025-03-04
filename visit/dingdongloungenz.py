import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

Server_API_URL = "https://www.dingdongloungenz.com/events-1"
target_id = 'dingdongloungenz'
target_url = 'https://www.dingdongloungenz.com/'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_dingdongloungenz():
    result = []
    raw = requests.get(Server_API_URL)
    soup = BeautifulSoup(raw.content, 'lxml')

    articles = soup.find_all('li', class_='LFRKo9 Lgwamt')
    print(len(articles))
    for article in articles:
        event_title = article.select_one('[data-hook="ev-list-item-title"]').text.strip()
        event_time = article.select_one('[data-hook="date"]').text.strip()
        event_location = article.select_one('[data-hook="location"]').text.strip()
        event_img_url = article.select_one('wow-image img')['src']
        event_url = article.select_one('[data-hook="ev-rsvp-button"]')['href']
        

        response1 = requests.get(event_url)
    
        soup1 = BeautifulSoup(response1.content, 'html.parser')
        event_description=''
        div_event_description = soup1.find('div',class_='WpX5rV')
        if div_event_description:
            item_div=div_event_description.find_all('p')
            for div in item_div:
                event_description=''+div.text.strip()
        result={    
                    'target_id': target_id,
                    'target_url': event_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category': ['DING DONG'],
                    "start_date": event_time,
                    "end_date": "",
                    "start_time": '',
                    "end_time": "",
                    'add_to_cart_url': event_url,              
                    'event_imgurl': event_img_url,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": "",
                        "country": "New Zealand"
                    }
                }

        await save_to_supabase(result)
    print('get_events_from_dingdongloungenz')

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





