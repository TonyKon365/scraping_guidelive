import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from urllib.parse import urljoin
from supabase import create_client, Client
from Utils.open_ai import customize, customizable

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to fetch URL content asynchronously
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

# Function to extract image URL from the style attribute
def extract_image_url(style):
    try:
        url_match = re.search(r"url\('([^']+)'\)", style)
        if url_match:
            return url_match.group(1)
        else:
            print("Image URL not found in style attribute")
            return ""
    except Exception as e:
        print(f"Error extracting image URL: {e}")
        return ""

# Function to scrape the main page and extract event details
async def get_event_from_forummelbourne():

    main_page_url = "https://forummelbourne.com.au/shows?"

    try:
        html_content = await fetch_url(main_page_url)
        soup = BeautifulSoup(html_content, "lxml")

        # Find all event items
        event_items = soup.find_all("a", class_="show-item")
        print("count of events",len(event_items))

        for item in event_items:
            try:
                # Extract event URL
                event_url = item['href']
                event_url = event_url if event_url.startswith("http") else urljoin(url, event_url)

                # Extract event title
                event_title = item.find('span', class_='title').get_text(strip=True)

                # Extract event image URL
                div_element = item.find('div', class_='image')
                event_imgurl = extract_image_url(div_element['style'])

                try:
                    html_content1 = await fetch_url(event_url)
                    soup1 = BeautifulSoup(html_content1, "lxml")
                    description_div = soup1.find('div', class_='column left')
                    event_description = description_div.get_text(separator=' ', strip=True) if description_div else ""
                    list_item=soup1.find_all('div','show-item-details')
                    print("count of items",len(list_item,),event_url)
                    for item in list_item:
                        start_date, start_time = "", ""
                        calendar_div = item.find('div', class_='content')
                        if calendar_div:
                            start_date_div = calendar_div.find('span', class_='full-date')
                            if start_date_div:
                                start_date = start_date_div.get_text(strip=True)

                            time_div = calendar_div.find('span', class_='time')
                            if time_div:
                                start_time = time_div.get_text(strip=True)
                        article={
                                    "target_id": "forummelbourne",
                                    "target_url": url,
                                    "event_imgurl": event_imgurl,
                                    "event_title": event_title,
                                    "start_date": start_date,
                                    "end_date": "",  # End date not available
                                    "event_category": ['show'],
                                    "event_description": event_description,
                                    "start_time": start_time,
                                    "add_to_cart_url": event_url,
                                    "end_time": "",
                                    "event_location_title":"Forum Melbourne",
                                    "event_street":"",
                                    "event_region":"",
                                    "event_country":"",
                                    "event_location": {
                                        "title": "Forum Melbourne",
                                        "street": "154 Flinders St",
                                        "region": "Melbourne",
                                        "country": "Australia",
                                    },
                                }
                        await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing event item: {e}")
            except Exception as e:
                print(f"Error processing event item: {e}")

 
    except Exception as e:
        print(f"Error fetching/parsing main page: {e}")
        return []


# Function to check duplication and save data to Supabase
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
   