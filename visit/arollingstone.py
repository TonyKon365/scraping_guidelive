import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


Server_API_URL = "https://www.arollingstone.co.nz/gig-guide"
target_id = 'arollingstone'
target_url = 'https://www.arollingstone.co.nz/'

async def get_events_from_arollingstone():
    result = []
    
    raw = requests.get(Server_API_URL)
    if raw.status_code == 200:
        soup = BeautifulSoup(raw.content, 'lxml')
        p_elements = soup.find_all('p', style='white-space:pre-wrap;')
        
        if not p_elements:
            print("No <p> elements found with the specified style.")
            return result
        
        for p_element in p_elements:
            strong_text = ""
            rest_of_text = ""
            
            strong_tag = p_element.find('strong')
            if strong_tag:
                strong_text = strong_tag.get_text()
                rest_of_text = p_element.get_text().replace(strong_text, '').strip()
            else:
                rest_of_text = p_element.get_text().strip()
            
            
            event_data = {
                    'target_id': target_id,
                    'target_url': target_url,
                    'event_title': target_id,
                    'event_description': rest_of_text,
                    'event_category': ['GIG'],
                    'event_imgurl': '',
                     'add_to_cart_url':target_url,
                    "start_date": strong_text,
                    "end_date": "",
                    "start_time":'',
                    "end_time": "",
                     "event_location": {
                        "title" : "Christchurch 8011",
                        "street" : "579 Colombo Street",
                        "region" : "Christchurch Central City",
                        "country" : "New Zealand"
                    }
                }
            await save_to_supabase(event_data)
    print("get_events_from_arollingstone")

async def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time = article["start_time"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", date).eq("start_time", time).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("Event1").insert(card).execute()
   

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

