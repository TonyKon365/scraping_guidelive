import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

Server_API_URL = "https://ticketing.oz.veezi.com/sessions/?siteToken=fpnccxy3ma159g7z8a3e95asy8"
target_id = 'hollywoodavondale'
target_url = 'https://www.hollywoodavondale.nz/'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_hollywoodavondale():
    result = []
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        links = soup.find_all('div', class_='film')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for link in links:
        try:
            # Extract event title
            title_tag = link.find('h3', class_='title')
            event_title = title_tag.get_text(strip=True) if title_tag else 'No Title'

            # Extract event time and date
            date_tag = link.find('h4', class_='date')
            time_tag = link.find('time')
            date_element = date_tag.text.strip() if date_tag else ''
            time_element = time_tag.text.strip() if time_tag else ''
            formatted_datetime = f"{date_element} 2024 {time_element}"

            # Extract event URL
            event_url = link.find('a')['href']
            if "https" not in event_url:
                event_url = 'https://ticketing.oz.veezi.com' + event_url

            # Extract event description
            event_description = scrape_detail_page(event_url)

            # Extract event image URL
            img_tag = link.find('img', class_='poster')
            if img_tag and 'src' in img_tag.attrs:
                base_url = "https://ticketing.oz.veezi.com"
                relative_img_url = img_tag['src']
                event_img_url = base_url + relative_img_url.replace('&amp;', '&')
            else:
                event_img_url = ''

            result.append({
                'target_id': target_id,
                'target_url': target_url,
                'event_title': event_title,
                'event_description': event_description,
                'event_category': ['movie'],
                "start_date": formatted_datetime,
                "end_date": "",
                "start_time": '',
                "end_time": "",
                'add_to_cart_url': event_url,    
                'event_imgurl': event_img_url,
                "event_location": {
                    "title": 'Avondale, Auckland, New Zealand',
                    "street": "18-20 Saint Georges Road",
                    "region": "Auckland",
                    "country": "New Zealand"
                }
            })
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    await save_to_supabase(result)
    print('get_events_from_hollywoodavondale')

def scrape_detail_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        synopsis_div = soup.find('div', class_='synopsis')

        # Extract text from all <p> tags within the synopsis div
        paragraphs = synopsis_div.find_all('p')
        description = ' '.join(p.text.strip() for p in paragraphs if p.text.strip())
        return description
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return ""
    except Exception as e:
        print(f"Error parsing detail page: {e}")
        return ""

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


