import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

Server_API_URL = "https://crownrangelounge.co.nz/live-music%2Fgig-guide"
target_id = 'crownrangelounge'
target_url = 'https://crownrangelounge.co.nz/home'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_crownrangelounge():

    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        div = soup.find('div', {'data-aid': 'MENU_ITEM_GRID_0'})
        if not div:
            print("Error: Couldn't find the events container.")
            return
        articles = div.find_all('div', {'data-ux': 'GridCell'})
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for article in articles:
        title_tag = article.find('h4')
        if not title_tag:
            continue

        title_text = title_tag.text.split(' - ')
        if len(title_text) < 2:
            continue

        event_title = title_text[1]
        event_time = title_text[0] + '2024'
            
        desc_div = article.find_all('span')
        event_description = desc_div[0].text if desc_div else ""
        img_tag = article.find('img')
        event_img_url = 'https:' + img_tag['data-srcsetlazy'] if img_tag and 'data-srcsetlazy' in img_tag.attrs else ""
        url_tag = article.find('a')
        event_url = url_tag['href'] if url_tag else ""

        result={
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['Show'],
                'add_to_cart_url': event_url,    
                'event_imgurl': event_img_url,
                "start_date": event_time,
                "end_date": '',
                "start_time": '',
                "end_time": "",
                "event_location": {
                    "title": 'Auckland',
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                }
            }
        await save_to_supabase(result)

    print("get_events_from_crownrangelounge")

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


