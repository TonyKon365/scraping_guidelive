import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

Server_API_URL = "https://galatos.co.nz/"
target_id = 'galatos'
target_url = 'https://galatos.co.nz/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_galatos():
    result = []
    try:
        raw = requests.get(Server_API_URL, headers=headers)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        links = soup.find_all('a', class_='woocommerce-loop-product__link')
    except Exception as e:
        print(f"Error parsing main page: {e}")
        return

    for link in links:
        try:
            event_url = link.get('href')
            raw = requests.get(event_url, headers=headers)
            raw.raise_for_status()  # Raise an HTTPError for bad responses

            soup = BeautifulSoup(raw.content, 'html.parser')
            
            # Extracting the event time
            event_time_element = soup.select_one('.custom_ticket_venue_header .venue .doors')
            event_time = event_time_element.text.strip() if event_time_element else 'No Time Available'

            # Extracting the event location
            event_location_element = soup.select_one('.custom_ticket_venue_header .venue .addr')
            event_location = event_location_element.text.strip() if event_location_element else 'No Location Available'

            # Extracting the event image URL
            event_img_url_element = soup.select_one('.woocommerce-product-gallery__image img')
            event_img_url = event_img_url_element['src'] if event_img_url_element and 'src' in event_img_url_element.attrs else ''

            # Extracting the event title
            event_title_element_h1 = soup.select_one('.custom_ticket_event_header .title h1')
            event_title_element_h2 = soup.select_one('.custom_ticket_event_header .title h2')
            event_title = (event_title_element_h1.text.strip() if event_title_element_h1 else 'No Title') + ", " + (event_title_element_h2.text.strip() if event_title_element_h2 else '')

            # Extracting the event description
            description_paragraphs = soup.select('.summary.entry-summary p')
            event_description = "\n\n".join(p.text.strip() for p in description_paragraphs)

            # Save data in database
            result.append({
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['Show'],
                'add_to_cart_url': event_url,
                "start_date": event_time,
                "end_date": "",
                "start_time": '',
                "end_time": "",
                'event_imgurl': event_img_url,
                "event_location": {
                    "title": event_location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                }
            })
        except requests.RequestException as e:
            print(f"Error fetching event page: {e}")
            continue
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    await save_to_supabase(result)
    return result

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


