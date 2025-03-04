import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all('div', class_='block widget', attrs={'data-loaded': 'true'})
    articles = []
    for item in raws:
        a_tag = item.find('a')
        img_tag = item.find('img')
        info_div = item.find('div', class_='info')

        if a_tag and img_tag and info_div:
            event_url = a_tag['href']
            event_imgurl = "https://www.bohmpresents.com"+img_tag['src']
            event_tile = info_div.get_text(strip=True)
            event_description,start_time,start_date,location=scrape_detail_page(event_url)
            add_to_cart_url=event_url
            articles.append(
                {
                    "target_id": "bohmpresentsEvent",
                    "target_url": "https://www.bohmpresents.com/current-events/",
                    "event_title": event_tile,
                    "start_date" : start_date,
                    "start_time" : start_time,
                    "end_date" : "",
                    "event_description": event_description,
                    "end_time" : "",
                    "event_category": ['Show'],
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "add_to_cart_url":event_url,
                    "event_location": location
                    
                }
            )

    return articles


def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    article_content = soup.find("div", class_="description").get_text(separator="\n").strip()
    first_aside = soup.find('aside', class_='event-venue-info')
    date_text = first_aside.find('li', class_='date').text
    cleaned_str = re.sub(r'^[A-Za-z]+,\s*', '', date_text).replace('@', '').strip()
    date_part, time_part = cleaned_str.rsplit(' ', 1)
    input_str = date_part.strip()
    date_obj = datetime.strptime(input_str, "%d %B %Y")
    start_date = date_obj.strftime("%Y-%m-%d")
    time_obj = datetime.strptime(time_part.strip(), "%I:%M%p")
    start_time = time_obj.strftime("%H:%M:%S.0000000")
    first_aside = soup.find('aside', class_='event-venue-info')
    title = first_aside.find('li', class_='title').text
    venue = first_aside.find('li', class_='venue').text
    location = {
        "title" : title,
        "street" : "",
        "region" : venue,
        "country" : "Australia"
    }

    return article_content,start_time,start_date,location


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
        supabase.table("guideEvent").select("*").eq("event_title", title).eq("start_date", date).eq("start_time", time).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("guideEvent").insert(card).execute()

async def get_event_from_bohmpresents():
    main_page_url = "https://www.bohmpresents.com/current-events/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        await save_to_supabase(article)
        
    print("get_event_from_bohmpresents")