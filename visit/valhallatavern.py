import requests
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import os

Server_API_URL = "https://www.valhallatavern.com/events-1"
target_id = 'valhallatavern'
target_url = 'https://www.valhallatavern.com/'

async def get_events_from_valhallatavern():
    result = []
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        articles = soup.find_all('article', class_='eventlist-event eventlist-event--upcoming eventlist-event--hasimg eventlist-hasimg')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for article in articles:
        try:
            event_title = article.find('h1', class_='eventlist-title').get_text(strip=True)

            # Extract event description
            description_div = article.find('div', class_='image-subtitle-wrapper')
            description_paragraphs = description_div.find_all('p') if description_div else []
            event_description = "\n\n".join(p.get_text(strip=True) for p in description_paragraphs)

            img_tag = article.find('img')
            event_img_url = 'https://www.valhallatavern.com' + img_tag.get('src') if img_tag else ''

            # Extract event URL
            event_url_tag = article.find('a', class_='eventlist-title-link')
            event_url = target_url + event_url_tag['href'] if event_url_tag else ''
   
            start_date, start_time, end_time, location, street, region = await scrape_detail_page(event_url)


            event_data = {
                    'target_id': target_id,
                    'target_url': event_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category': ['Show'],
                    'event_imgurl': event_img_url,
                    "start_date": start_date,
                    "end_date": start_date,
                    "start_time": start_time,
                    'end_time': end_time,
                    'add_to_cart_url': event_url,
                    "event_location": {
                        "title": location,
                        "street": street,
                        "region": region,
                        "country": "New Zealand"
                    }
                }
            await save_to_supabase(event_data)


        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    print("get_events_from_valhallatavern")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    try:
        title = article["event_title"]
        target_id = article["target_id"]
        existing_article = (
            supabase.table("guideEvent").select("*").eq("target_id", target_id).eq("event_title", title).execute()
        )
        if not existing_article.data:
            temp_obj = await customize(article)
            card = customizable(temp_obj)
            response = supabase.table("Event1").insert(card).execute()
    except Exception as e:
        print(f"Error saving to Supabase: {e}")

async def scrape_detail_page(event_url):
    try:
        response = requests.get(event_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'lxml')

        # Find the event title
        title_tag = soup.find('h1', class_='eventitem-title')
        event_title = title_tag.get_text(strip=True) if title_tag else "Title not found"

        # Find the start date
        start_date_tag = soup.find('time', class_='event-date')
        start_date = start_date_tag['datetime'] if start_date_tag else "Date not found"

        # Find the start and end times
        start_time_tag = soup.find('time', class_='event-time-localized-start')
        end_time_tag = soup.find('time', class_='event-time-localized-end')
        start_time = start_time_tag.get_text(strip=True) if start_time_tag else "Start time not found"
        end_time = end_time_tag.get_text(strip=True) if end_time_tag else "End time not found"

        # Find the location details
        location_tag = soup.find('span', class_='eventitem-meta-address-line--title')
        street_tag = soup.find_all('span', class_='eventitem-meta-address-line')[1]
        region_tag = soup.find_all('span', class_='eventitem-meta-address-line')[2]
        location = location_tag.get_text(strip=True) if location_tag else "Location not found"
        street = street_tag.get_text(strip=True) if street_tag else "Street not found"
        region = region_tag.get_text(strip=True) if region_tag else "Region not found"

        return start_date, start_time, end_time, location, street, region
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return "", "", "", "", "", ""
    except Exception as e:
        print(f"Error parsing detail page: {e}")
        return "", "", "", "", "", ""

