import requests
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import os

Server_API_URL = "https://totarastreet.co.nz/events"
target_id = 'totarastreet'
target_url = 'https://totarastreet.co.nz/events'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_totarastreet():
    result = []

    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        rows = soup.find_all('a', class_='item-title-wrap')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for a_tag in rows:
        try:
            # Extract the detail URL from the <a> tag
            detail_url = a_tag.get('href')
            
            # Extract the event title from the <h3> tag
            title_tag = a_tag.find('h3', class_='item-title')
            event_title = title_tag.get_text(strip=True) if title_tag else ""

            if detail_url:
                try:
                    raw1 = requests.get(detail_url)
                    raw1.raise_for_status()  # Raise an HTTPError for bad responses
                except requests.RequestException as e:
                    print(f"Error fetching detail page: {e}")
                    continue

                try:
                    soup1 = BeautifulSoup(raw1.content, 'lxml')
                    div_start_date = soup1.find('span', class_='date')
                    start_date = div_start_date.get_text().strip() if div_start_date else ""
                    
                    description_div = soup1.find('div', class_='grid-text')
                    description_tags = description_div.find_all('p') if description_div else []
                    event_description = '\n'.join(tag.get_text(strip=True) for tag in description_tags)
                    
                    img_div = soup1.find_all('img')
                    event_imgurl = 'https://totarastreet.co.nz' + img_div[1]['src'] if img_div and len(img_div) > 1 else ""
                    
                    # Extract the location from all <a> tags within <div> elements with class "grid-btn"
                    grid_btn = soup1.find('a', class_='btn btn-secondary')
                    add_to_cart_url = grid_btn['href'] if grid_btn else ""

                    event_data = {
                        'target_id': target_id,
                        'target_url': detail_url,
                        'event_title': event_title,
                        'event_imgurl': event_imgurl,
                        'event_description': event_description,
                        'event_category': ['Show'],                         
                        'add_to_cart_url': detail_url,
                        "start_date": start_date,
                        "end_date": "",
                        "start_time": '',
                        "end_time": "",
                        "event_location": {
                            "title": "Totara",
                            "street": "Totara Street",
                            "region": "Mount Maunganui, Tauranga",
                            "country": "New Zealand"
                        }
                    }
                    result.append(event_data)
                except Exception as e:
                    print(f"Error parsing detail page: {e}")
                    continue
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    await save_to_supabase(result)

async def save_to_supabase(articles):
    for article in articles:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        title = card["event_title"]
        start_date = card["start_date"]

        existing_article = (
            supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
            )
        if not existing_article.data:
            response = supabase.table("Event1").insert(card).execute()
