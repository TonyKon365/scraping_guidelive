import requests
from bs4 import BeautifulSoup
import os
import json
from supabase import create_client, Client
from Utils.open_ai import customize, customizable

Server_API_URL = "https://www.northlandnz.com/api-listing/listing?&pageId=42&offset={}"
target_id = 'northlandnz'
target_url = 'https://www.northlandnz.com'

async def get_events_from_northlandnz():
    page = 0
    result = []
    
    try:
        while True:
            try:
                raw = requests.get(Server_API_URL.format(page)).json()
                if not raw['items']:
                    break
            except requests.RequestException as e:
                print(f"Error fetching events page {page}: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response on page {page}: {e}")
                break

            cards = raw['items']
            for card in cards:
                try:
                    event_title = card['name']
                    event_detail_url = target_url + '/' + card['url']
                    event_imgurl = target_url + card['image']
                    event_description = card['summary']
                    event_category = ",".join([cat_item['Title'] for cat_item in card['categories']])  # type: ignore
                    start_date = card['startDate']
                    end_date = card['endDate']
                    start_time, end_time = card['time'].split(" - ")
                    event_location = card['venue']

                    result={
                        "target_id": target_id,
                        "target_url": target_url,
                        "event_title": event_title,
                        "event_description": event_description,
                        "event_category": [event_category],
                        "add_to_cart_url": event_detail_url,
                        "start_time": start_time,
                        "end_date": end_date,
                        "end_time": end_time,
                        'start_date': start_date,
                        "event_imgurl": event_imgurl,
                        "event_location": {
                            "title": event_location,
                            "street": "",
                            "region": "",
                            "country": "New Zealand"
                        },
                    }
                    await save_to_supabase(result)
                except KeyError as e:
                    print(f"KeyError processing card: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing card: {e}")
                    continue

            page += 1
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("get_events_from_northlandnz")

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
