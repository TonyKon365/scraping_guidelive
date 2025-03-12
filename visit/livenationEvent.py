import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import json
from supabase import create_client, Client
import os
import json
from Utils.open_ai import customize, customizable

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                return await response.text()
        except asyncio.TimeoutError:
            print(f"Request timed out for URL: {url}")
            return ""
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return ""

async def get_event_from_livenationNZ():

    url = "https://www.livenation.co.nz/event/allevents"

    try:
        html_content = await fetch_url(url)
        soup = BeautifulSoup(html_content, "lxml")

    except Exception as e:
        print(f"Error fetching/parsing main page: {e}")
        return []

    script_tags = soup.find_all('script', type='application/ld+json')
    print(f"Found {len(script_tags)} script tags")

    for idx, item in enumerate(script_tags):

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
            event_description = await scrape_detail_page(event_url)

            if event_title and event_title != "N/A":
                article = {
                    "target_id": "livenationEvent",
                    "target_url": url,
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "add_to_cart_url": event_url,
                    "event_category": ["music"],
                    "event_description": event_description,
                    "start_time": "",
                    "end_time": "",
                     "event_location_title":location_title,
                    "event_street":"",
                     "event_region":"",
                    "event_country":"",
                    "event_location": {
                        "title": location_title,
                        "street": "",
                        "region": location_region,
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(article)
        except Exception as e:
            print(f"Error processing event data: {e}")

    print("get_event_from_livenationNZ completed")

async def scrape_detail_page(event_url):
    try:
        html_content = await fetch_url(event_url)
        soup = BeautifulSoup(html_content, "lxml")

        description_div = soup.find('div', class_='eventdetails__list')
        event_description = ''
        if description_div:
            event_description = ' '.join(p.text.strip() for p in description_div.find_all('p'))
        return event_description
    except Exception as e:
        print(f"Error scraping detail page: {e}")
        return ""

async def save_to_supabase(article):
    temp_obj = await customize(article)
    card = customizable(temp_obj)
    add_to_cart_url = card["add_to_cart_url"]
 
    card['event_location']['title'] = card.get('event_location_title', "")
    card['event_location']['street'] = card.get('event_street', "")
    card['event_location']['region'] = card.get('event_region', "")
    card['event_location']['country'] = card.get('event_country', "")

        # Remove unnecessary keys
    card.pop('event_location_title', None)
    card.pop('event_street', None)
    card.pop('event_region', None)
    card.pop('event_country', None)


    existing_article = (
        supabase.table("Event3").select("*").eq("add_to_cart_url", add_to_cart_url).execute()
        )
    if not existing_article.data:

        response = supabase.table("Event3").insert(card).execute()
        print(card)