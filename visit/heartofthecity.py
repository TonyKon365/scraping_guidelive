import requests
import json
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import os


target_url = 'https://heartofthecity.co.nz'
target_id = 'heartofthecity'
Server_API_URL = "https://heartofthecity.co.nz/views/ajax"

async def get_events_from_heartofthecity():
    page = 21
    payload = { 'view_name': 'sector_sitewide_search','view_display_id': 'page_4', 'view_args': '85','page': 0}
    while True:
        result = []
        payload['page'] = page
        # async with aiohttp.ClientSession(headers=headers) as session:
        #     async with session.post(url, data=payload) as response:
        raw = requests.post(Server_API_URL, data=payload)
        if raw.status_code == 200:
            res = raw.json()
            temp = res[-1] if len(res) else None
            soup = BeautifulSoup(temp['data'], 'lxml')
            articles = soup.find_all('li', class_='grid__item')
            if not len(articles): break
            for article in articles:
                #title, description, img, time
                content_tag = article.find('div', class_='slat__content')
                event_title = content_tag.find('h4', class_='slat__title').text.strip() if content_tag else ""
                event_time = article.find('div', class_='slat__date').text.strip()
                
              
                temp1 = article.find('div', class_='field-name-field-summary')
                event_description = temp1.text.strip() if temp1 else ""
                img_tag = article.find('source')
                event_imgurl = target_url + img_tag.get('data-srcset') if img_tag else ""
                if event_imgurl == '': break
                    
                detailed_url = target_url + article.find('a', class_='field-group-link').get('href')
                raw1 = requests.get(detailed_url)
                if raw1.status_code == 200:
                    soup1 = BeautifulSoup(raw1.content, 'lxml')
                        #script
                    location_tag = soup1.find('div', class_='field-name-dynamic-token-fieldnode-custom-location-with-map-link')
                    event_location = location_tag.text.strip() if location_tag else ""
                    event_category = ['music']
                
                    result={
                            "target_id": target_id,
                            "target_url": target_url,
                            "event_title": event_title,
                            "event_description": event_description,
                            "event_category": [event_category],
                            "start_date": event_time,
                            "add_to_cart_url": detailed_url,
                            "event_imgurl": event_imgurl,
                            "end_date": '',
                            "end_time": "",
                            "start_time": "",
                             "event_location": {
                                "title": event_location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            },
                        }
                    await save_to_supabase(result)
                
                else: continue
        else: break
        page += 1
        
    print("get_events_from_heartofthecity")
        
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)



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



