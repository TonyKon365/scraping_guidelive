import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from Utils.open_ai import customize, customizable
import os

Server_API_URL = "https://www.theincubator.co.nz/whats-on"
target_id = 'theincubator'
target_url = 'https://www.theincubator.co.nz/whats-on'

async def get_events_from_theincubator():

    raw = requests.get(Server_API_URL)
    if raw.status_code == 200:
        soup = BeautifulSoup(raw.content, 'lxml')
        links = soup.find_all('li', class_='yIpRkq')
        print(len(links))
        for item in links:
                # Get the href attribute
            event_url = item.find('a')['href']
            event_title=item.find('a').text.strip()
            location_element = item.find('div', {'data-hook': 'short-location'}).text.strip()
            start_date = item.find('div', {'data-hook': 'short-date'}).text.strip()
            event_img_url=item.find('img')['src']
            raw = requests.get(event_url)
            if raw.status_code == 200:
                soup = BeautifulSoup(raw.content, 'lxml')
                event_description = ''
                about_section = soup.find('div', {'data-hook': 'about-section-text'})
                if about_section:
                    event_description = about_section.get_text(separator="\n").strip()
            result={
                        'target_id': target_id,
                        'target_url': event_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': ['Show'],
                        "start_date": start_date,
                        "end_date": '',
                        "start_time":'',
                        'add_to_cart_url':event_url,
                        "end_time": "",
                        'event_imgurl': event_img_url,
                         "event_location": {
                            "title" : location_element,
                            "street" : "",
                            "region" : "",
                            "country" : "New Zealand"
                        }

                    }
        
            await save_to_supabase(result)
    print("get_events_from_theincubator")
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








url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

