import requests
from bs4 import BeautifulSoup
import os
import json
from Utils.open_ai import customize, customizable
from supabase import create_client, Client


Server_API_URL = "https://www.frontiertouring.com/search/tours?fields.tourType=current&orderBy=fields.startDate&limit=100"
target_id = 'frontiertouring'
target_url = 'https://www.frontiertouring.com'

async def get_events_from_frontiertouring():
    result = []
    try:
        res = requests.get(Server_API_URL)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
        script = soup.find('script', {'type': 'application/ld+json'})
        json_data_list = json.loads(script.string)
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for json_data in json_data_list:
        try:
            event_category = json_data['@type']
            event_title = json_data['name']
            event_detail_url = json_data['url']
            event_imgurl = json_data['image']
            event_location = json_data['location']['name']
            country = json_data['location']['address']['addressCountry']
            region = json_data['location']['name']
            start_date = json_data['startDate']
            end_date = json_data['endDate']

            try:
                raw_detail = requests.get(event_detail_url)
                raw_detail.raise_for_status()
                soup1 = BeautifulSoup(raw_detail.text, 'lxml')
                description = soup1.find('div', class_='tour-intro')
                event_description = description.text.strip() if description else ""
            except requests.RequestException as e:
                print(f"Error fetching event detail page: {e}")
                event_description = ""

            obj = {
                "target_id": target_id,
                "target_url": target_url,
                "event_title": event_title,
                "event_description": event_description,
                "event_category": [event_category],
                "start_date": start_date,
                "start_time": "",
                "end_date": end_date,
                "end_time": "",
                "add_to_cart_url": event_detail_url,
                "event_imgurl": event_imgurl,
                "event_location": {
                    "title": event_location,
                    "street": "",
                    "region": region,
                    "country": country
                },
            }
   
            await save_to_supabase(obj)
        except Exception as e:
            print(f"Error processing event: {e}")
            continue

    print("get_events_from_frontiertouring")

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

