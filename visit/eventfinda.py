import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import requests
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))  # type: ignore

Server_API_URL = "https://www.eventfinda.co.nz/whatson/events/new-zealand/this-weekend/page/1"

async def get_events_from_eventfinda():
    page=1
  
    while True:
        page_url = f'https://www.eventfinda.co.nz/whatson/events/new-zealand/this-weekend/page/{page}'
        print(page)
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text, 'lxml')
        
        card_tags = soup.find_all('div', class_="card")
        if card_tags==None:
            break
        for card_tag in card_tags:
            try:
                target_id = 'eventfinda'
                target_url = 'https://www.eventfinda.co.nz'
                title_tag = card_tag.find('a', class_='url summary')
                event_title = title_tag.text if title_tag else ""
                
                detail_url = target_url + card_tag.find('a')['href']
                category_tag = card_tag.find('span', class_='category')
                event_category = category_tag.text.strip() if category_tag else ""
                location_tag = card_tag.find('span', class_='p-locality')
                event_location = location_tag.text.replace('&nbsp', '') if location_tag else ""
                img_tag = card_tag.find('img', class_='card-img-top')
                event_imgurl = img_tag.get('src') if img_tag else ""       


                try:
                    response = requests.get(detail_url)
                    soup_detailed = BeautifulSoup(response.text, 'lxml')
                    description_tag = soup_detailed.find('div', class_='module description', id='eventDescription')
                    event_description = description_tag.text if description_tag else ""
                    event_time_row = soup_detailed.find('div',id='jsSessions')
                    list_time=event_time_row.find_all('time')
           
                    for item in list_time:
                        start_date=item['datetime']
                        result = {
                                "target_id": target_id,
                                "target_url": target_url,
                                "event_title": event_title,
                                "event_description": event_description,
                                "event_category": [event_category],
                                'start_date': start_date,
                                "add_to_cart_url": detail_url,
                                "start_time": "",
                                "end_date": "",
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
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching details for {detail_url}: {e}")    
                
            except Exception as e:
                print(f"Error parsing events page: {e}")
        page=page+1
    print("get_events_from_eventfinda")

async def save_to_supabase(article):
   
    target_id = article["target_id"]

    temp_obj = await customize(article)
    card = customizable(temp_obj)
    title = card["event_title"]
    start_date=card["start_date"]
    existing_article = (
            supabase.table("Event1").select("*").eq("target_id", target_id).eq("start_date", start_date).eq("event_title", title).execute()
        )
    if not existing_article.data:
        response = supabase.table("Event1").insert(card).execute()
