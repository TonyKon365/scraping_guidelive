import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

async def get_event_from_destinationgoldcoast():
    main_page_url = "https://www.destinationgoldcoast.com/events/all"
    page = 1
    while True:
        response = requests.get(f"{main_page_url}?page={page}")
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, "lxml")
        if soup is None:
            break
        try:
            div_container = soup.find("div", class_="dgc-listing")
     
            raws = div_container.find_all("li")
            print(len(raws))
        except AttributeError as e:
            print(f"Error parsing the main page HTML: {e}")
            return []
        for item in raws:
            try:
                a_tag = item.find('a')

                # Extract the event URL
                event_url = 'https://www.destinationgoldcoast.com' + a_tag['href']

                # Locate the <img> tag within the <a> tag
                img_tag = a_tag.find('img')

                # Extract the image URL
                event_imgurl = img_tag['src']

                event_title = item.find('h3').text.strip() if item.find('h3') else ""

                event_description, start_date, start_time, end_time, street, region, country = scrape_detail_page(event_url)

                article={
                        "target_id": "destinationgoldcoastEvent",
                        "target_url": "https://www.destinationgoldcoast.com/events/all",
                        "event_imgurl": event_imgurl,
 
                        "event_title": event_title,
                        "start_date": start_date,
                        "end_date": start_date,
                        "start_time": start_time,
                        "end_time": end_time,
                        "event_description": event_description,
                        "event_category": ["music"],
                        "add_to_cart_url": event_url,
                        "event_location": {
                            "title": region,
                            "street": street,
                            "region": region,
                            "country": country
                        },
                    }
                await save_to_supabase(article)
            except Exception as e:
                print(f"Error processing item: {e}")
        page += 1

    print("get_event_from_destinationgoldcoast")
    

def scrape_detail_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return "", "", "", "", "", "", ""

    try:
        event_description_div = soup.find("div", id="event-description")
        result = ""
        if event_description_div:
            article_content = event_description_div.find_all("p")
            paragraph_content = [p.get_text(separator=" ") for p in article_content]
            result = "\n\n".join(paragraph_content)
    except AttributeError as e:
        print(f"Error parsing event description: {e}")

    try:
        date_div = soup.find('div', class_='dgc-summary-schedule-date')
        date = ""
        if date_div:
            time_paragraphs = date_div.find_all('p')
            date = time_paragraphs[0].get_text(strip=True) if time_paragraphs else ""
        
        start_time = ""
        end_time = ""
        if len(time_paragraphs) > 1:
            time_range = time_paragraphs[1].get_text(strip=True)
            if '-' in time_range:
                start_time, end_time = [t.strip() for t in time_range.split('-')]
    except AttributeError as e:
        print(f"Error parsing date and time: {e}")

    try:
        location_str = soup.find('div', class_='dgc-listing-header__details').find('p').get_text(strip=True)
        parts = location_str.split(', ')
        street = parts[0]
        region_country = parts[1].rsplit(' ', 1)
        region = region_country[0]
        country = 'Australia'
    except AttributeError as e:
        print(f"Error parsing location: {e}")
        street = ""
        region = ""
        country = "Australia"

    return result, date, start_time, end_time, street, region, country

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



