import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable

# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("a", class_="calendar__item clearfix")
    articles = []

    for item in raws:
        event_url = item['href']

        event_title = item.find('h1', class_='calendar__item-title').text.strip()

        # Extract image URL
        event_imgurl = item.find('div', class_='calendar__item-image').find('img')['src']

        # Extract date information
        date_text = item.find('div', class_='calendar__item-date').text.strip()
        # Extract date components
        day = date_text[3:5].strip()
        month = date_text[5:].strip()

        # Create a date object
        date_string = f"2024-{month}-{day}"
        date = datetime.strptime(date_string, "%Y-%b-%d").date()
        event_description,add_to_cart_url,start_time=scrape_detail_page(event_url)
        formatted_date = date.strftime('%Y-%m-%d')

        articles.append(
            {
                "target_id": "cornerhotelEvent",
                "target_url": "http://cornerhotel.com/events-and-specials/",
                "event_title": event_title,
                "event_category": ['Shows'],
                'event_description':event_description,
                'add_to_cart_url':event_url,
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "start_date": formatted_date,
                "end_date": formatted_date,
                "start_time":start_time,
                "end_time": "",
                "event_location": {
                    "title" : 'Richmond, VIC 3121',
                    "street" : "57 Swan St",
                    "region" : "Richmond, VIC 3121",
                    "country" : "Australia"
                },
                
            }
        )

    return articles



def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    event_description = soup.find("div", class_="page__copy copy clearfix").get_text(separator="\n").strip()
    start_time=soup.find('h3', class_='page__date-heading').text.strip()
    div = soup.find('div', class_='page__copy copy clearfix')
    add_to_cart_url=""
    # Extract the href attribute of the anchor tag inside the div
    if div:
        anchor = div.find('a')
        if anchor and 'href' in anchor.attrs:
            add_to_cart_url = anchor['href']
            
    else:
        print('No div with the specified class found')

    
    return event_description,add_to_cart_url,start_time

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time = article["start_time"]
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        if(card["end_date"]==''):
            card["end_date"]=card['start_date']
        response = supabase.table("guideEvent").insert(card).execute()
  

async def get_event_from_cornerhotel():
    main_page_url = "http://cornerhotel.com/events-and-specials/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
       
        await save_to_supabase(article)
    print("get_event_from_cornerhotel")