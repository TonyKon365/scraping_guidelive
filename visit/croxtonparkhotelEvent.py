import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from urllib.parse import urljoin

def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    
    time_element = soup.find('time', class_='ns-msp0op')
    datetime_str = time_element['datetime']
    start_date = datetime_str.split('T')[0]

    p_element = soup.find('p', {'data-testid': 'aedp-event-information-block-times'})
    time_element = p_element.find('time')
    if time_element:
        time_str = time_element.text.strip()
        formatted_time = time_str + ":00"
    else:
        formatted_time=''
   

    buy_tickets_tag = soup.find('a', {'data-testid': 'aedp-event-single-ticket-action-button-or-status'})
    if buy_tickets_tag:
        buy_tickets_link = buy_tickets_tag['href']
    else:
        buy_tickets_link=''
    
    return formatted_time, start_date,buy_tickets_link

def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="sqs-block-content")
    print(raws)
    articles = []
    
    for item in raws:
        event_urlDiv = item.find('a')
        event_url = ''
        if event_urlDiv and 'href' in event_urlDiv.attrs:
            event_url = 'https://www.croxtonparkhotel.com.au'+event_urlDiv['href']   
        img_element = soup.find('a').find('img')

# Check if the <img> element exists and has an src attribute
        event_imgurl = img_element['src'] if img_element and 'src' in img_element.attrs else ''
      #  text_element = item.find('div', class_='carousel-cell-footer').find('div')
   #     event_title = text_element.text.strip() if text_element else ''
    #    a_element = item.find('div', class_='carousel-cell-footer').find('a', class_='more')
     #   add_to_cart_url = a_element['href'] if a_element and 'href' in a_element.attrs else ''
      #  start_time, start_date,add_to_cart_url = scrape_detail_page(event_url)
        articles.append(
            {
                "target_id": "croxtonparkhotelEvent",
                "target_url": "https://www.croxtonparkhotel.com.au/entertainment",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": 'event_title',
                "start_date": 'start_date',
                'event_category': ['Show'],
                "end_date": 'start_date',
                "event_description": "",
                "start_time": 'start_time',
                "end_time": "",
                "add_to_cart_url": 'add_to_cart_url',
                "event_location": {
                    "title" : 'event_title',
                    "street" : "",
                    "region" : "",
                    "country" : "Australia",
                },
            }
        )

    return articles

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time = article["start_time"]
    existing_article = (
        supabase.table("guideEvent")
        .select("*")
        .eq("event_title", title)
        .eq("start_date", date)
        .eq("start_time", time)
        .execute()
    )

    if not existing_article.data:
        response = supabase.table("guideEvent").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")

def get_event_from_croxtonparkhotel():
    main_page_url = "https://www.croxtonparkhotel.com.au/entertainment"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        print(article)
        save_to_supabase(article)

