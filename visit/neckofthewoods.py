
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re

from Utils.open_ai import customize, customizable
Server_API_URL = "https://www.neckofthewoods.co.nz/events"
target_id = 'neckofthewoods'
target_url = 'https://www.neckofthewoods.co.nz/'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_neckofthewoods():
   
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        articles = soup.find_all('article', class_='eventlist-event eventlist-event--upcoming eventlist-event--multiday')
        print(len(articles))
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for article in articles:
        try:
            event_title = article.find('h1', class_='eventlist-title').get_text(strip=True).upper()
            img_tag = article.find('img', {'data-image': True})
            event_img_url = img_tag['srcset'] if img_tag else ""
            description_blocks = article.find_all('div', class_='sqs-block-content')
            event_description = "\n".join(block.get_text(strip=True) for block in description_blocks).strip()
            event_url = article.find('div', class_='sqs-block-button-container').find('a')['href']
            date_div=article.find('div',class_='eventlist-datetag')
            start_date=date_div.find('div',class_='eventlist-datetag-startdate--month').text.strip()+' '+date_div.find('div',class_='eventlist-datetag-startdate--day').text.strip()+' '+'2024'
            end_date=date_div.find('div',class_='eventlist-datetag-enddate').text.strip()+' '+'2024'

            event_location=article.find('li',class_='eventlist-meta-address').text.strip()
            result={
                'target_id': target_id,
                'target_url': event_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['Show'],
                "start_date": start_date,
                "end_date": end_date,  # Add end_date if available
                "start_time": "",  # Add start_time if available
                "end_time": "",  # Add end_time if available
                'add_to_cart_url': event_url,
                'event_imgurl': event_img_url,
                "event_location": {
                    "title":event_location,
                    "street": '',
                    "region": '',
                    "country": "New Zealand"
                }
            }
            await save_to_supabase(result)
        except Exception as e:
            print(f"Error processing an article: {e}")
            continue


  
    print("get_events_from_neckofthewoods")

def scrape_detail_page(event_url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    start_date=soup.find('time',class_='f-label-3').text.strip()
   
    location = soup.find('span', class_='eventitem-meta-address-line')
    title=location[0].text.strip()
    street=location[2].text.strip()
    region=location[1].text.strip()
    # return start_date,title,street,region


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



