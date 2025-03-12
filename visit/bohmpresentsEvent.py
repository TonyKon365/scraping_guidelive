import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
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
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            print(f"Request timed out for URL: {url}")
            return ""
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return ""


# Main function to scrape events and save them to Supabase
async def get_event_from_bohmpresents():
    main_page_url = "https://www.bohmpresents.com/current-events/"
    try:
        html_content = await fetch_url(main_page_url)
        soup = BeautifulSoup(html_content, "lxml")
        print(soup)
        raws = soup.find_all('div', class_='block widget', attrs={'data-loaded': 'true'})
        print(len(raws))
        articles = []

        for item in raws:
            try:
                a_tag = item.find('a')
                img_tag = item.find('img')
                info_div = item.find('div', class_='info')

                if a_tag and img_tag and info_div:
                    event_url = a_tag['href']
                    event_imgurl = "https://www.bohmpresents.com" + img_tag['src']
                    event_title = info_div.get_text(strip=True)
                    event_description, start_time, start_date, location = await scrape_detail_page(event_url)

                    articles=(
                        {
                            "target_id": "bohmpresentsEvent",
                            "target_url": "https://www.bohmpresents.com/current-events/",
                            "event_title": event_title,
                            "start_date": start_date,
                            "start_time": start_time,
                            "end_date": "",
                            "event_description": event_description,
                            "end_time": "",
                            "event_category": ['Show'],
                            "event_imgurl": event_imgurl,
                            "add_to_cart_url": event_url,
                            "event_location": location
                        }
                    )
                    await save_to_supabase(articles)
            except Exception as e:
                print(f"Error processing event item: {e}")

    except Exception as e:
        print(f"Error fetching/parsing main page: {e}")
        return []


# Function to scrape the event detail page for descriptions and dates
async def scrape_detail_page(event_url):
    try:
        html_content = await fetch_url(event_url)
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract event description
        description_div = soup.find("div", class_="description")
        event_description = description_div.get_text(separator="\n").strip() if description_div else ""

        # Extract date and time
        first_aside = soup.find('aside', class_='event-venue-info')
        date_text = first_aside.find('li', class_='date').text
        cleaned_str = re.sub(r'^[A-Za-z]+,\s*', '', date_text).replace('@', '').strip()
        date_part, time_part = cleaned_str.rsplit(' ', 1)

        # Convert date and time to desired formats
        input_str = date_part.strip()
        date_obj = datetime.strptime(input_str, "%d %B %Y")
        start_date = date_obj.strftime("%Y-%m-%d")
        time_obj = datetime.strptime(time_part.strip(), "%I:%M%p")
        start_time = time_obj.strftime("%H:%M:%S.0000000")

        # Extract location details
        title = first_aside.find('li', class_='title').text
        venue = first_aside.find('li', class_='venue').text
        location = {
            "title": title,
            "street": "",
            "region": venue,
            "country": "Australia"
        }

        return event_description, start_time, start_date, location
    except Exception as e:
        print(f"Error scraping detail page ({event_url}): {e}")
        return "", "", "", {}
    

async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # add_to_cart_url = card["add_to_cart_url"]
    # existing_article = (
    #     supabase.table("Event3").select("*").eq("add_to_cart_url", add_to_cart_url).execute()
    #     )
    # if not existing_article.data:
        response = supabase.table("Event3").insert(article).execute()