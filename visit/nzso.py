import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv
from API.Httpclient import fetch_event_data
import os
import json
from datetime import datetime
from Utils.open_ai import customize, customizable


Server_API_URL = "https://srf7s95mal-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia for JavaScript (4.16.0); Browser (lite); instantsearch.js (4.53.0); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.12.0)&x-algolia-api-key=d9317c556e68922642127a88488854c9&x-algolia-application-id=SRF7S95MAL"

load_dotenv()
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')) # type: ignore

payload_params = "analytics=false&facets=%5B%22event_season.title%22%2C%22venue_locations.title%22%5D&filters=collection_handle%3Aevents%20AND%20published%3Atrue%20AND%20private%3Afalse&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=12&maxValuesPerFacet=100&page={}&sortFacetValuesBy=alpha&tagFilters="


async def get_events_from_nzso():
    for index in range(0, 2):
        params = payload_params.format(index)
        payload = json.dumps({
            "requests": [
                {
                    "indexName": "entries_date_asc",
                    "params": params
                }
            ]
        })
        response = requests.post(Server_API_URL, data=payload)
        res_data = response.json()
        events = res_data['results'][0]['hits']
        
        target_url = "https://www.nzso.co.nz"
        target_id = 'nzso'
        
        for event in events:
            print(event)
            event_title = event["title"]
        
  

            start_date=convert(event['concert_date_first'])
            end_date=convert(event['concert_date_last'])
            event_category = 'music'
            event_imgurl = target_url + "_next/image?url=https://nzso.sgp1.digitaloceanspaces.com/" +event['hero_image'] + '&w=1920&q=75'
            event_location = event['venue_locations'][0]['title']
            detailed_url = target_url + event['url']
            event_description=scrape_detail_page(detailed_url)
            result={
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": [event_category],
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_time":"",
                    'add_to_cart_url':detailed_url,
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title" : event_location,
                        "street" : "",
                        "region" : "",
                        "country" : "New Zealand"
                }
            }
            await save_to_supabase(result)
    print('get_events_from_nzso')

def scrape_detail_page(event_url):
    print(event_url)
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    
    div_description=soup.find('div',class_='prose')
    description=div_description.text.strip()
    return description

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


def convert(original_date_str):
    date_object = datetime.fromisoformat(original_date_str[:-1])  # Remove 'Z' for fromisoformat
    formatted_date_str = date_object.strftime('%Y-%m-%d')
    return formatted_date_str
