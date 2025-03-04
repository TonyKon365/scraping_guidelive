
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
from datetime import datetime
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))  # type: ignore

Server_API_URL = "https://www.atc.co.nz/whats-on"
target_id = 'atc'
target_url = 'https://www.atc.co.nz'


async def get_events_from_atc():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    res = requests.get(Server_API_URL,headers=headers)
    soup = BeautifulSoup(res.content, 'lxml')
   
   
    events=soup.find_all('article')
    print(events)
    for item in events:
        try:
            event_title = item.find('h3').text.strip()
            event_description = item.find('p').text.strip()
            event_imgurl = item.find('img')['src']
            event_category = 'music'

            detailed_url = item.find('a')['href']
            start_date, event_location=scrape_detail_page(detailed_url)
            result = {
                "target_id": target_id,
                "target_url": target_url,
                "event_title": event_title,
                "event_description": event_description,
                "event_category": [event_category],
                "event_imgurl": event_imgurl,
                'start_date': start_date,
                "add_to_cart_url": detailed_url,
                "start_time": "",
                "end_date": '',
                "end_time": "",
                "event_location": {
                    "title": event_location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                },
            }

            await save_to_supabase(result)
        except Exception as e:
            print(f"Error processing event: {e}")
            continue

    print("get_events_from_atc")


async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]
    # start_time = card["start_time"]
    # existing_article = (
    #     supabase.table("Event1")
    #     .select("*")
    #     .eq("event_title", title)
    #     .eq("start_date", start_date)
    #     .eq("start_time", start_time)
    #     .execute()
    # )

    # if not existing_article.data:
    response = supabase.table("Event1").insert(article).execute()


def scrape_detail_page(event_url):
    try:
        response = requests.get(event_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        div=soup.find('div',class_='dates-location')
        start_date=div.find_all('p')[0].text.strip()
        location=div.find_all('p')[1].text.strip()
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return ""


    return start_date,location



