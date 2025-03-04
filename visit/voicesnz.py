import requests
from bs4 import BeautifulSoup
from Utils.open_ai import customizable, customize
import json
from supabase import create_client, Client
import os


Server_API_URL = "https://www.voicesnz.com/event/auckland/"
target_id = 'voicesnz'
target_url = 'https://www.voicesnz.com'

async def get_events_from_voicesnz():
    try:
        res = requests.get(Server_API_URL)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return
    except Exception as e:
        print(f"General error: {e}")
        return

    try:
        script = soup.find('script', {'type': 'application/ld+json'})
        json_data = json.loads(script.string)
        event_category = 'Voice'
        event_title = json_data['@graph'][0]['name']
        event_imgurl = json_data['@graph'][0]['thumbnailUrl']
        description = soup.find('div', id='event-info')
        event_description = description.text.strip() if description else ""
        rows=soup.find_all('div',class_='venue-box')

        for item in rows:
            region=item.find('h1').text.strip()
            start_date=item.find_all('p')[0].text.strip()
            location_title=item.find_all('p')[1].text.strip()
            article = {
                "target_id": target_id,
                "target_url": target_url,
                "event_title": event_title,
                "event_description": event_description,
                "event_category": [event_category],
                "start_date": start_date,
                "event_imgurl": event_imgurl,
                "add_to_cart_url": Server_API_URL,
                "event_location": {
                    "title": location_title,
                    "street": "",
                    "region": region,
                    "country": "New zealand"
                },
            }
            await save_to_supabase(article)
    except Exception as e:
        print(f"Error parsing event details: {e}")
        return

    print("get_events_from_voicesnz")

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
