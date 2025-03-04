import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

Server_API_URL = "https://thistlehall.org.nz/activities"
target_id = 'thistlehall'
target_url = 'https://thistlehall.org.nz/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_thistlehall():
    result = []
    try:
        raw = requests.get(Server_API_URL, headers=headers)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'html.parser')
        links = soup.find_all('div', class_='view-mode-full ds-2col-stacked clearfix')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for link in links:
        try:
            # Get the event title
            event_title = link.find('div', class_='field--name-node-title').get_text(strip=True)
            
            # Extract the event time
            event_time = link.find('div', class_='field--name-field-time').find('div', class_='field__item').get_text(strip=True)
            
            # Extract the event location
            event_location = link.find('div', class_='field--name-field-where').find('div', class_='field__item').get_text(strip=True)
            
            # Extract the event description
            description_parts = []
            for field in link.find_all('div', class_='group-footer')[0].find_all('div', class_='field'):
                label = field.find('div', class_='field__label').get_text(strip=True).upper()
                item = field.find('div', class_='field__item').get_text(" ", strip=True)
                description_parts.append(f"{label}\n{item}")

            event_description = "\n\n".join(description_parts)
            
            # Extract the event URL
            add_to_cart_url = link.find('a')['href']
            if "https" not in add_to_cart_url:
                add_to_cart_url = target_url

            result.append({
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['Show'],
                'add_to_cart_url': add_to_cart_url,              
                "start_date": event_time,
                "end_date": "",
                "start_time": '',
                "end_time": "",
                'event_imgurl': '',
                "event_location": {
                    "title": event_location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                }
            })
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    await save_to_supabase(result)
    print("get_events_from_thistlehall")

async def save_to_supabase(articles):
    for article in articles:
        try:
            title = article["event_title"]
            existing_article = (
                supabase.table("Event1").select("*").eq("target_id",target_id).eq("event_title", title).execute()
            )
            if not existing_article.data:
                # temp_obj = await customize(article)
                # card = customizable(temp_obj)
                response = supabase.table("Event1").insert(articles).execute()
        except Exception as e:
            print(f"Error saving to Supabase: {e}")