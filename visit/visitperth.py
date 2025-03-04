import requests
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import load_dotenv
from API.Httpclient import fetch_event_data  # Assuming this is your custom function
import os
from Utils.open_ai import customize, customizable


load_dotenv()


supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and Key must be set in the environment variables")

supabase = create_client(supabase_url, supabase_key)

Server_API_URL = "https://visitperth.com/events#eventenddate=20241002|&e=0"
target_url = 'https://visitperth.com'
target_id = "visitperth"

async def get_events_from_visitperth():
    page=0
    while True:
        main_page_url = f"https://visitperth.com/events#eventenddate=20241002|&e={page}"
        try:          
            response = requests.get(main_page_url)  
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []
        try:
            raws = soup.find_all("li")
            print(soup)
            print(len(raws))
            articles = []
            if articles==None:
                break 
            for item in raws:
                try:
                    event_title = item.find('h6').text
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)                 
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""
                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['business'],
                            "event_imgurl": event_imgurl,
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")


async def save_to_supabase(article):
    try:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        target_id = card["target_id"]
        title = card["event_title"]
        existing_article = (
            supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
        )
        
        if not existing_article.data:
            response = supabase.table("Event1").insert(card).execute()
     
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
