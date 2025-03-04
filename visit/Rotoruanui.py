import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

target_url = 'https://www.rotoruanui.nz'
target_id = 'rotoruanui'
Server_API_URL = "https://www.rotoruanui.nz/all-events/page/{}"

async def get_events_from_rotoruanui():
    page = 0

    while True:

        result = []
        try:
            raw = requests.get(Server_API_URL.format(page))
            raw.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.RequestException as e:
            print(f"Error fetching events page {page}: {e}")
            break

        try:
            soup = BeautifulSoup(raw.content, 'lxml')
            if soup==None:
                break
            articles = soup.find_all('a', class_=lambda value: value and 'featuredCard card' in value)
            if articles==None:
                break 
        except Exception as e:
            print(f"Error parsing events page {page}: {e}")
            break

        if not articles:
            break

        for article in articles:
            try:
                # title, img, time
                img_tag = article.find('img', class_='card-img')
                event_imgurl = img_tag.get('src').strip() if img_tag else ""
                event_title = img_tag.get('alt').strip() if img_tag else ""
                event_time = article.find('span', class_='mainTitle').find_next().get_text(strip=True)
                detail_url = article.get('href')

                
                raw1 = requests.get(detail_url)
                raw1.raise_for_status()  # Raise an HTTPError for bad responses
                soup1 = BeautifulSoup(raw1.content, 'lxml')

                        # category
                cate_tag = soup1.find('div', class_='tagContainer')
                tags = cate_tag.find_all('a', class_='tag') if cate_tag else []
                event_category = ', '.join(tag.get_text(strip=True) for tag in tags)

                        # location
                location_tag = soup1.find('a', class_='mapText')
                event_location = location_tag.text.strip() if location_tag else ""

                        # description
                event_description = soup1.find('div', class_='fullSingleInfo').text.strip() if soup1.find('div', class_='fullSingleInfo') else ""

                result={
                            "target_id": target_id,
                            "target_url": target_url,
                            "event_title": event_title,
                            "event_description": event_description,
                            "event_category": [event_category],
                            "start_date": event_time,
                            "end_date": '',
                            'add_to_cart_url': detail_url,
                            "end_time": "",
                            "start_time": "",
                            "event_imgurl": event_imgurl,
                            "event_location": {
                                "title": event_location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            },
                        }
                await save_to_supabase(result)
            except Exception as e:
                print(f"Error processing an event: {e}")
                continue
        page += 1

    print('get_events_from_rotoruanui')

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

