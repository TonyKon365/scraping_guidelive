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

Server_API_URL = "https://jazz.org.nz/2024-events/"
target_id = 'jazz'
target_url = 'https://jazz.org.nz/'
async def get_events_from_jazz():
    response = requests.get(target_url)
    soup = BeautifulSoup(response.content, "lxml")
    nav_tags = soup.find_all('nav', class_='elementor-nav-menu--dropdown elementor-nav-menu__container')

    for nav_tag in nav_tags:
        events = nav_tag.find_all('a', class_='elementor-item')
        for event in events:
            try:
                detailed_url = event.get('href')
                event_title = event.text.strip()
                try:
                    res_detailed_data = await session.get(detailed_url)
                    res_detailed_data.raise_for_status()
                    soup_detailed = BeautifulSoup(await res_detailed_data.text(), 'lxml')
                except aiohttp.ClientError as e:
                    print(f"Error fetching event detail page: {e}")
                    continue
                try:
                    ele_wrap_tag = soup_detailed.find('div', class_=lambda value: value and 'jet-sticky-column elementor-column' in value)
                    list_tags = ele_wrap_tag.find_all('div', {'data-widget_type': 'text-editor.default'})
                    date_tag = list_tags[0]
                    event_time = date_tag.get_text().strip() + ' 2024'

                    location_tag = list_tags[1]
                    event_location = location_tag.text.strip()
                    start_time = list_tags[2].get_text().strip()

                        # description
                    div_temp = soup_detailed.find('div', class_=lambda value: value and 'ob-has-background-overlay elementor-widget elementor-widget-spacer' in value)
                    description_tag = div_temp.find_next('div', {'data-widget_type': 'text-editor.default'})
                    event_description = description_tag.text.strip()
                    img_tag = soup_detailed.find('img', class_=lambda value: value and 'attachment-large' in value)
                    event_imgurl = img_tag.get('src') if img_tag else ""

                    event_category = 'Jazz'

                    result = {
                            "target_id": target_id,
                            "target_url": target_url,
                            "event_title": event_title,
                            "event_description": event_description if event_description else event_title,
                            "event_category": [event_category],
                            'start_date': event_time,
                            "add_to_cart_url": detailed_url,
                            "start_time": start_time,
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
                except Exception as e:
                    print(f"Error processing event details: {e}")
                    continue
            except Exception as e:
                print(f"Error processing event: {e}")
                continue

        print("get_events_from_jazz")

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

