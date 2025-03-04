import requests
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from urllib.parse import urljoin
from supabase import create_client, Client
import os


Server_API_URL = "https://nzopera.com/whats-on/calendar/"
target_id = 'nzopera'

target_url = 'https://nzopera.com'

async def get_events_from_nzopera():
    try:
        res = requests.get(Server_API_URL)
        res.raise_for_status()
        raw = BeautifulSoup(res.text, 'lxml')
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return
    except Exception as e:
        print(f"General error: {e}")
        return

    resultTemp = []
    try:
        card_tags = raw.find_all('div', class_='gb-query-loop-item')
        print(len(card_tags))
        for card in card_tags:
            try:
                contents = card.find_all('div', class_='gb-grid-column')
        
                content2 = contents[1]
                content3 = contents[2]
                event_imgurl_div = card.find('img')
                event_imgurl = event_imgurl_div['src']

                if "https://nzopera.com/wp-content/uploads" in event_imgurl:
                    continue
                else:
                    event_imgurl = event_imgurl_div['data-src']

                title = content2.find('h2')
                event_title = title.text if title else ""

                desc_ps = content2.find_all('p')
                event_description = desc_ps[1].text.strip() if len(desc_ps) > 1 else desc_ps[0].text.strip()

                cont_list = content3.find_all('div', class_='gb-container')
                event_time = cont_list[1].text.strip()
                event_location = cont_list[2].text.strip()
                detail_url = cont_list[3].find('a').get('href')

                obj = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['Opera'],
                    "start_date": event_time,  # Convert to string
                    "start_time": '',  # Convert to string
                    "end_date": "",
                    "end_time": "",
                    "add_to_cart_url": detail_url,
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(obj)
                print(obj)
            except Exception as e:
                print(f"Error processing a card: {e}")
                continue
    except Exception as e:
        print(f"Error extracting cards: {e}")

    
    print("get_events_from_nzopera")

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



try:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Error creating Supabase client: {e}")

