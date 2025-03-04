import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from Utils.open_ai import customize, customizable

retry_strategy = Retry(
    total=5,  
    backoff_factor=1, 
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"] 
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


def scrape_main_page(url):
    response = http.get(url, timeout=10)  
    soup = BeautifulSoup(response.content, "html.parser")
    div = soup.find('div', class_='attending-Bar sub')


    raws = div.find_all('li')
    articles = []

    for item in raws:
        try:
            event_title = item.find('h3').text.strip()

            a_element = item.find('a')
            event_imgurl = ''
            if a_element and 'href' in a_element.attrs:
                img_element = a_element.find('img')
                if img_element and 'src' in img_element.attrs:
                    event_imgurl = img_element['src']

            event_url = 'https://aaaticketing.co.nz/' + a_element['href']
            start_date=item.find_all('p')[0].text.strip()
            location=item.find_all('p')[1].text.strip()

            event_description = scrape_detail_page(event_url)
            articles.append(
                {
                    "target_id": "aaaticketing",
                    "target_url": "https://aaaticketing.co.nz/event",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": '',  
                    "event_description": event_description,  
                    "start_time": '',
                    "event_category":["tour"],
                    "add_to_cart_url": event_url,  
                    "end_time": "",
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
            )
        except Exception as e:
            print(f"Error processing item: {e}")

    return articles

def scrape_detail_page(news_url):
    response = http.get(news_url, timeout=10)  
    soup = BeautifulSoup(response.content, "html.parser")
    description = ""
    for p in soup.find_all('p'):
        description += p.get_text(separator=" ", strip=True) + " "


    description = ' '.join(description.split())
    return description


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







async def get_events_from_aaaticketing():
    main_page_url = "https://aaaticketing.co.nz/event"
    articles = scrape_main_page(main_page_url)
    for article in articles:
        await save_to_supabase(article)
    print("get_events_from_aaaticketing")