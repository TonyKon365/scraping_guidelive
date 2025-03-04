import requests
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import os

Server_API_URL = "http://www.cabana.net.nz"
target_id = 'cabana'
target_url = 'http://www.cabana.net.nz'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def get_events_from_cabana():
    result = []
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        links = soup.find_all('div', class_='ev2page-col')
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    for link in links:
        try:
            day = link.find('div', class_='ev2page-day')
            month = link.find('div', class_='ev2page-month')
            year = link.find('div', class_='ev2page-year')
            time = link.find('div', class_='ev2page-hour')
            weekday = link.find('div', class_='ev2page-week')

            day = day.text.strip() if day else "N/A"
            month = month.text.strip() if month else "N/A"
            year = year.text.strip() if year else "N/A"
            time = time.text.strip() if time else "N/A"
            weekday = weekday.text.strip() if weekday else "N/A"
            event_time = f"{time}, {day} {month.upper()} {year}, {weekday.upper()}"

            # Extracting the event title
            event_title_tag = link.find('h2', class_='ev2page-title')
            event_title = event_title_tag.a.text.strip() if event_title_tag and event_title_tag.a else "N/A"
            event_description = ""
            event_description_div = link.find('p')
            if event_description_div:
                event_description = event_description_div.get_text(strip=True)

            event_img_tag = link.find('div', class_='ev2page-cover')
            event_img_url = event_img_tag.img['src'] if event_img_tag and event_img_tag.img else "N/A"
            event_url = event_title_tag.a['href'] if event_title_tag and event_title_tag.a else ""

    
            if event_url:
                try:
                    raw1 = requests.get(event_url)
                    raw1.raise_for_status()  # Raise an HTTPError for bad responses
                    soup1 = BeautifulSoup(raw1.content, 'lxml')
                    time_info = soup1.find('div', class_='evsng-cell-info')
                    time = time_info.get_text() if time_info else "N/A"
                except requests.RequestException as e:
                    print(f"Error fetching event detail page: {e}")
                    continue
                except Exception as e:
                    print(f"Error parsing event detail page: {e}")
                    continue

                event_data = {
                    'target_id': target_id,
                    'target_url': event_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category':['Show'],
                    "start_date": event_time,
                    "end_date": '',
                    "end_time": "",
                    "start_time": "",
                    "add_to_cart_url": event_url,
                    'event_imgurl': event_img_url,
                    "event_location": {
                        "title": "The Cabana",
                        "street": "11 Shakespeare Rd",
                        "region": "Napier",
                        "country": "New Zealand"
                    },
                }
                result.append(event_data)

                continue
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    if result:
        await save_to_supabase(result)
    print("get_events_from_cabana")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

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



