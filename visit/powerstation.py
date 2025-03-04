import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from Utils.open_ai import customize, customizable

Server_API_URL = "https://www.powerstation.net.nz/"
target_id = 'powerstation'
target_url = 'https://www.powerstation.net.nz/'

async def get_events_from_powerstation():
    result = []
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        articles = soup.find_all('article', class_='node node--announcement node--tour node--tour--announcement announcement')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for article in articles:
        try:
            title_tag = article.find('h2')
            event_title = title_tag.get_text(strip=True) if title_tag else ""
            
            time_tag = article.find('time')
            event_time = time_tag.get_text(strip=True) if time_tag else ""

            description_tags = article.find('div', class_='announcement-text').find_all('p')
            event_description = ' '.join(tag.get_text(strip=True) for tag in description_tags)

            img_tag = article.find('img')
            event_img_url = 'https://www.powerstation.net.nz' + img_tag.get('src') if img_tag else ""

            event_url = 'https://www.powerstation.net.nz' + article.find('a')['href']
                
            event_data = {
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['Show'],
             
                "start_date": event_time,
                'add_to_cart_url': event_url,
                "end_date": "",
                "start_time": '',
                "end_time": "",
                'event_imgurl': event_img_url,
                "event_location": {
                    "title": "Auckland",
                    "street": "33 Mount Eden Road",
                    "region": "Eden Terrace, Auckland",
                    "country": "New Zealand"
                }
            }

            await save_to_supabase(event_data)
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    print("get_events_from_powerstation")

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





# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

