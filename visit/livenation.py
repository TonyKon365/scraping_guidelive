import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import json
from Utils.open_ai import customize, customizable

target_url="https://www.livenation.co.nz/event/allevents"
target_id = 'livenation'
async def get_events_from_livenation():
    url = "https://www.livenation.co.nz/event/allevents"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing main page: {e}")
        return []

    script_tags = soup.find_all('script', type='application/ld+json')
    
    articles = []
    print(len(script_tags))
    for item in script_tags:
        try:
            json_data = json.loads(item.string)
            event_title = json_data.get('name', 'N/A')


            event_imgurl = json_data.get('image', 'N/A')
            event_url = json_data.get('url', 'N/A')
            start_date = json_data.get('startDate', 'N/A')
            end_date = json_data.get('endDate', 'N/A')
            location = json_data.get('location', {})
            location_title = location.get('name', 'N/A')
            location_region = location.get('address', {}).get('addressLocality', 'N/A')
            description = json_data.get('offers', {}).get('name', 'N/A')

           
            if event_title!="":
                article = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": description,
                    "event_category": ["music"],
                    "add_to_cart_url": event_url,
                    "start_date": start_date,
                    "start_time": "",
                    "end_date": "",
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": location_title,
                            "street": "",
                            "region": location_region,
                            "country": "Australia"
                            },
                    }
                await save_to_supabase(article)
        except Exception as e:
            print(f"Error processing event data: {e}")

    print("get_event_from_livenationNZ")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]

    # existing_article = (
    #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
    #     )
    # if not existing_article.data:
        response = supabase.table("Event1").insert(article).execute()





