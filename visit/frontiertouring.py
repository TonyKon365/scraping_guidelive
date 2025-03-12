import aiohttp
from bs4 import BeautifulSoup
import os
import json
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import asyncio

# Configuration
Server_API_URL = "https://www.frontiertouring.com/search/tours?fields.tourType=current&orderBy=fields.startDate&limit=100"
target_id = "frontiertouring"
target_url = "https://www.frontiertouring.com"

# Supabase configuration
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


async def fetch_url(session, url):
    """Fetch URL asynchronously with aiohttp."""
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching URL: {url}, Error: {e}")
        return None


async def get_events_from_frontiertouring():
    """Scrape events from Frontier Touring and save them to Supabase."""
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch the main events page
            res_text = await fetch_url(session, Server_API_URL)
            if not res_text:
                return

            # Parse the HTML
            soup = BeautifulSoup(res_text, "lxml")
            script = soup.find("script", {"type": "application/ld+json"})
            if not script:
                print(f"No JSON-LD script found on {Server_API_URL}")
                return

            try:
                json_data_list = json.loads(script.string)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON data: {e}")
                return
            
            print(f"count of {len(json_data_list)}")

            for json_data in json_data_list:
                try:
                    # Extract event details
                    event_category = json_data.get("@type", "N/A")
                    event_title = json_data.get("name", "N/A")
                    event_detail_url = json_data.get("url", "")
                    event_imgurl = json_data.get("image", "")
                    country = json_data.get("location", {}).get("address", {}).get("addressCountry", "")
                    # Fetch event details page for description
                    event_description = ""
                    if event_detail_url:
                        raw_detail = await fetch_url(session, event_detail_url)
                        soup1 = BeautifulSoup(raw_detail, "lxml")
                        description = soup1.find("div", class_="tour-intro")
                        event_description = description.text.strip() if description else ""
                        list_items=soup1.find_all('div',class_='venue__header-accordion')
                        print(len(list_items),event_detail_url)
                        for item in list_items:
                            start_date=item.find('div',class_='venue__date').text.strip()
                            end_date=item.find('div',class_='venue__date').text.strip()
                            event_location=item.find('div',class_='venue__name').text.strip()
                            region=item.find('div',class_='venue__city').text.strip()

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
                                "event_location_title":event_location,
                                "event_street":"",
                                "event_region":region,
                                "event_country":"",
                                "event_location": {
                                    "title": event_location,
                                    "street": "",
                                    "region": region,
                                    "country": country,
                                },
                            }

                    # Save to Supabase
                            await save_to_supabase(obj)
                except Exception as e:
                    print(f"Error processing event: {e}")
                    continue

    except Exception as e:
        print(f"Error fetching events page: {e}")

    print("get_events_from_frontiertouring completed")

async def save_to_supabase(article):
    temp_obj = await customize(article)
    card = customizable(temp_obj)
    add_to_cart_url = card["add_to_cart_url"]
    start_date = card["start_date"]
    
    card.pop('event_location_title', None)
    card.pop('event_street', None)
    card.pop('event_region', None)
    card.pop('event_country', None)


    existing_article = (
        supabase.table("Event3").select("*").eq("add_to_cart_url", add_to_cart_url).eq("start_date", start_date).execute()
        )
    if not existing_article.data:
        response = supabase.table("Event3").insert(card).execute()
   