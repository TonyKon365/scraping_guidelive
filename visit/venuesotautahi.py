import requests
from bs4 import BeautifulSoup
import os
import json
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import asyncio

Server_API_URL = "https://www.venuesotautahi.co.nz/events.json?type=369&venue=&within="
target_id = 'venuesotautahi'
target_url = 'https://www.venuesotautahi.co.nz'

async def get_events_from_venuesotautahi():
    try:
        res1 = requests.get('https://www.venuesotautahi.co.nz/events-types.json')
        res1.raise_for_status()
        category_res = res1.json()
    except requests.RequestException as e:
        print(f"Error fetching event types: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return

    for category in category_res.get('data', []):
        id = category.get('id')
        event_category = category.get('title')
        event_category = [item.strip() for item in event_category.split(" & ")]

        if not id or not event_category:
            continue

        init_type_url = f'https://www.venuesotautahi.co.nz/events.json?type={id}&venue=&within='
        try:
            temp = requests.get(init_type_url).json()
            page_count_type = temp['meta']['pagination']['total_pages']
        except requests.RequestException as e:
            print(f"Error fetching initial type URL for category {event_category}: {e}")
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for category {event_category}: {e}")
            continue

        for index in range(page_count_type):
            url = f'https://www.venuesotautahi.co.nz/events.json?type={id}&venue&within&pg={index + 1}'
            try:
                res = requests.get(url).json()
                res_data = res.get('data', [])
            except requests.RequestException as e:
                print(f"Error fetching events page {index + 1} for category {event_category}: {e}")
                continue
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response for page {index + 1} of category {event_category}: {e}")
                continue

            result = []
            print(res_data)
            for data in res_data:
                try:
                    event_title = data.get('title', '')
                    event_detail_url = data.get('url', '')
                    event_location = data.get('venue', '')
                    start_date = data.get('startDate', '')

                    event_imgurl = data.get('image', {}).get('url', '')

                    detail = requests.get(event_detail_url)
                    detail.raise_for_status()
                    soup = BeautifulSoup(detail.content, 'lxml')

                    script_tag = soup.find('script', {'type': 'application/ld+json'})
                    json_data = json.loads(script_tag.text) if script_tag else {}
                    event_description = json_data.get('@graph', [{}])[0].get('description', '')

                    result={
                        "target_id": target_id,
                        "target_url": target_url,
                        "event_title": event_title,
                        "event_description": event_description,
                        "event_category": event_category,
                        "start_date": start_date,
                        "end_date": "",
                        'add_to_cart_url': event_detail_url,
                        "start_time": "",
                        "end_time": "",
                        "event_imgurl": event_imgurl,
                        "event_location": {
                            "title": event_location,
                            "street": "",
                            "region": "",
                            "country": "New Zealand"
                        },
                     
                    }
                    await save_to_supabase(result)
                except requests.RequestException as e:
                    print(f"Error fetching event details: {e}")
                    continue
  

    print("get_events_from_venuesotautahi")

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

