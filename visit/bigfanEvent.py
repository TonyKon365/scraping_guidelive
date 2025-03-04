import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customize, customizable


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_event_from_bigfan():
    main_page_url = "https://www.bigfan.co.nz/events"
    page = 0
    response = requests.get(f"{main_page_url}?b138d03a_page={page}")
    response.raise_for_status()  # Check for HTTP errors
    soup = BeautifulSoup(response.content, "html.parser")
            
    raws = soup.find_all("div", class_="events-item w-dyn-item")
    if not raws:
        print(f"No events found on page {page}. Ending loop.")


    articles = []
    for item in raws:
                # Extract the event title
        event_title = item.find('a', class_='event-title w-inline-block').find_all('div')[1].text.strip()

                # Extract the start date and format it as required
        start_date_raw = item.find('div', class_='event__date').text.strip()
        start_date = datetime.strptime(f"{start_date_raw} 2024", "%d %b %Y").strftime("%Y-%m-%d")

                # Extract the event link and join with the base URL
        relative_event_link = item.find('a', class_='event-link-block w-inline-block')['href']
        event_url = urljoin("https://www.bigfan.co.nz", relative_event_link)
                
        event_description, start_time = scrape_detail_page(event_url)
                
        event_imgurl = item.find('a', class_='event-link-block w-inline-block').find('img')['src']
        article = {
                    "target_id": "bigfanEvent",
                    "target_url": "https://www.bigfan.co.nz/events",
                    "event_title": event_title,
                    "event_category": ['music'],
                    "event_imgurl": event_imgurl,
                   
                    "start_date": start_date,
                    "end_date": "",
                    "start_time": start_time,
                    "end_time": "",
                    'add_to_cart_url': event_url,
                    "event_description": event_description,
                    "event_location": {
                        "title": "Eden Terrace Auckland",
                        "street": "33 Mount Eden Road",
                        "region": "Eden Terrace Auckland",
                        "country": "New Zealand"
                    }
                }
                
        await save_to_supabase(article)

    print("get_event_from_bigfan")

def scrape_detail_page(event_url):
    try:
        response = requests.get(event_url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, "html.parser")

        time_str = soup.find('div', class_='event-page-time').get_text(strip=True)
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        start_time = time_obj.strftime("%H:%M:%S.%f")

        div_container = soup.find("div", class_="event-rich-body w-richtext")
        event_description = ''
        if div_container:
            event_description = " ".join(p.get_text() for p in div_container.find_all('p'))
        else:
            div_container1 = soup.find("div", class_="short--summary w-richtext")
            if div_container1:
                event_description = " ".join(p.get_text() for p in div_container1.find_all('p'))
            else:
                print(f"The specified <div> was not found: {event_url}")
                event_description = "Not there"
        return event_description, start_time

    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
        return "Not there", "00:00:00.000000"
    except Exception as e:
        print(f"Error scraping detail page: {e}")
        return "Not there", "00:00:00.000000"

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



