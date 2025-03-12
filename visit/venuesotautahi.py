import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import json
from supabase import create_client, Client
from Utils.open_ai import customize, customizable

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Target website details
target_id = "venuesotautahi"
target_url = "https://www.venuesotautahi.co.nz"


# Function to fetch URL content asynchronously
async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            logging.error(f"Request timed out for URL: {url}")
            return None
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return None


# Function to fetch JSON data asynchronously
async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            logging.error(f"Request timed out for URL: {url}")
            return None
        except Exception as e:
            logging.error(f"Error fetching JSON from {url}: {e}")
            return None


# Function to scrape event details from the main API
async def get_events_from_venuesotautahi():
    try:
        # Fetch event categories
        category_url = "https://www.venuesotautahi.co.nz/events-types.json"
        category_res = await fetch_json(category_url)

        if not category_res:
            logging.error("Failed to fetch event categories.")
            return

        for category in category_res.get("data", []):
            id = category.get("id")
            event_category = category.get("title")
            if not id or not event_category:
                continue

            # Split category into multiple if it contains "&"
            event_category = [item.strip() for item in event_category.split(" & ")]

            # Fetch the number of pages for this category
            init_type_url = f"https://www.venuesotautahi.co.nz/events.json?type={id}&venue=&within="
            temp_res = await fetch_json(init_type_url)
            if not temp_res:
                logging.error(f"Failed to fetch initial page count for category {event_category}.")
                continue

            page_count_type = temp_res.get("meta", {}).get("pagination", {}).get("total_pages", 0)

            for index in range(page_count_type):
                events_url = f"https://www.venuesotautahi.co.nz/events.json?type={id}&venue&within&pg={index + 1}"
                events_res = await fetch_json(events_url)

                if not events_res:
                    logging.error(f"Failed to fetch events for page {index + 1}, category {event_category}.")
                    continue

                for data in events_res.get("data", []):
                    try:
                        event_title = data.get("title", "")
                        event_detail_url = data.get("url", "")
                        event_location = data.get("venue", "")
                        start_date = data.get("startDate", "")
                        event_imgurl = data.get("image", {}).get("url", "")

                        # Fetch event details from detail page
                        event_description = await fetch_event_detail(event_detail_url)

                        if 'Apollo' in event_location:
                            event_data = {
                                "target_id": target_id,
                                "target_url": target_url,
                                "event_title": event_title,
                                "event_description": event_description,
                                "event_category": event_category,
                                "start_date": start_date,
                                "end_date": "",
                                "add_to_cart_url": event_detail_url,
                                "start_time": "",
                                "end_time": "",
                                "event_location_title":event_location,
                                "event_street":"",
                                "event_region":"",
                                "event_country":"",
                                "event_imgurl": event_imgurl,
                                "event_location": {
                                    "title": "Apollo Projects Stadium",
                                    "street": "95 Jack Hinton Drive,",
                                    "region": "Christchurch",
                                    "country": "New Zealand",
                                },
                            }
                        else:
                            event_data = {
                                "target_id": target_id,
                                "target_url": target_url,
                                "event_title": event_title,
                                "event_description": event_description,
                                "event_category": event_category,
                                "start_date": start_date,
                                "end_date": "",
                                "add_to_cart_url": event_detail_url,
                                "start_time": "",
                                "end_time": "",
                                "event_location_title":event_location,
                                "event_street":"",
                                "event_region":"",
                                "event_country":"",
                                "event_imgurl": event_imgurl,
                                "event_location": {
                                    "title": "Christchurch Town Hall",
                                    "street": "86 Kilmore St",
                                    "region": "Christchurch Central",
                                    "country": "New Zealand",
                                },
                            }

                        await save_to_supabase(event_data)
                    except Exception as e:
                        logging.error(f"Error processing event data: {e}")
                        continue

        logging.info("get_events_from_venuesotautahi completed.")
    except Exception as e:
        logging.error(f"Error in get_events_from_venuesotautahi: {e}")


# Function to fetch event details from the detail page
async def fetch_event_detail(event_url):
    try:
        html_content = await fetch_url(event_url)
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "lxml")

        # Extract event description from JSON-LD
        script_tag = soup.find("script", {"type": "application/ld+json"})
        if script_tag:
            json_data = json.loads(script_tag.string)
            description = json_data.get("@graph", [{}])[0].get("description", "")
            return description

        return ""
    except Exception as e:
        logging.error(f"Error fetching event details from {event_url}: {e}")
        return ""

async def save_to_supabase(article):
    temp_obj = await customize(article)
    card = customizable(temp_obj)
    add_to_cart_url = card["add_to_cart_url"]
 
    card.pop('event_location_title', None)
    card.pop('event_street', None)
    card.pop('event_region', None)
    card.pop('event_country', None)

    existing_article = (
        supabase.table("Event3").select("*").eq("add_to_cart_url", add_to_cart_url).execute()
        )
    if not existing_article.data:

        response = supabase.table("Event3").insert(card).execute()
        print(article)