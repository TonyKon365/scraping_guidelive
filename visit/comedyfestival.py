import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def scrape_main_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing main page: {e}")
        return []

    articles = []
    try:
        raws = soup.find_all("a", class_="grid-show")
    except Exception as e:
        print(f"Error finding event tags: {e}")
        return []

    for item in raws:
        try:
            event_url = "https://www.comedyfestival.co.nz" + item['href']
            location = item['data-locations']
            title_div = item.find('span', class_='title')
            event_title = title_div.get_text() if title_div else ""

            span = item.find('span', {'class': 'image'})
            style = span['style']
            event_imgurl = "https://www.comedyfestival.co.nz" + style.split("url('")[1].split("')")[0]

            event_description, start_date, start_time = scrape_detail_page(event_url)

            articles.append(
                {
                    "target_id": "comedyfestivalEvent",
                    "target_url": "https://www.comedyfestival.co.nz",
                    "event_title": event_title,
                    "event_category": ['music'],
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "start_date": start_date,
                    "end_date": "",
                    "start_time": start_time,
                    "end_time": "",
                    'add_to_cart_url': event_url,
                    "event_description": event_description,
                    "event_location": {
                        "title": location,
                        "street": "",
                        "region": "",
                        "country": "New Zealand"
                    }
                }
            )
        except Exception as e:
            print(f"Error processing an event: {e}")
            continue

    return articles

def scrape_detail_page(event_url):
    try:
        response = requests.get(event_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return "", "", ""
    except Exception as e:
        print(f"Error parsing detail page: {e}")
        return "", "", ""

    try:
        event_description = ''
        description_div = soup.find('div', class_='show-page-content well')
        if description_div:
            event_description = ' '.join([p.get_text(strip=True) for p in description_div.find_all('p')])
        else:
            print("Description not found", event_url)

        month_year = soup.find('div', class_='well-content-dates').find('p').text
        day = soup.find('div', class_='date-container').find('div', class_='date').text
        time = soup.find('div', class_='date-container').find('div', class_='time').text
        start_date = f"{month_year} {day}"
        start_time = time
    except Exception as e:
        print(f"Error extracting details from detail page: {e}")
        return "", "", ""

    return event_description, start_date, start_time

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to check for duplication and insert if not duplicated
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


async def get_events_from_comedyfestival():
    main_page_url = "https://www.comedyfestival.co.nz/find-a-show/"

    articles = await scrape_main_page(main_page_url)
    for article in articles:
        await save_to_supabase(article)
    print("get_events_from_comedyfestival")
