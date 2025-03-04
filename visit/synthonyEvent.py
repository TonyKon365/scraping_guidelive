import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(f"{url}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find("div", class_="elementor-element elementor-element-1a0056b e-con-full e-flex e-con e-child animated fadeIn")
    if raws is None:
        print("Div container not found")
        return []


    articles = []

    for item in raws:
        a_tag = item.find('a')

        # Extract the event URL
        event_url = 'https://www.destinationgoldcoast.com'+a_tag['href']

        # Locate the <img> tag within the <a> tag
        img_tag = a_tag.find('img')

        # Extract the image URL
        event_imgurl = img_tag['src']

        event_title = item.find('h2').text.strip() if item.find('h3') else ""

      
        event_description,add_to_cart_url,start_date,start_time,end_time,street,region,country=scrape_detail_page(event_url)
        
        articles.append(
            {
                "target_id": "synthonyEvent",
                "target_url": "https://synthony.com",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": start_date,
                "end_time":end_time,
                "event_description": event_description,
                "start_time": start_time,
                "event_category":["music"],
                "add_to_cart_url":add_to_cart_url,
                "event_location": {
                    "title" : event_title,
                    "street" :street,
                    "region" : region,
                    "country" : country
                },
            }
            )

    return articles

def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find(
        "div", id="event-description"
    ).find_all("p")
    paragraph_content = [p.get_text(separator=" ") for p in article_content]
    result = "\n\n".join(paragraph_content)
    booking_link_tag = soup.find('a', class_='make-booking')

    if booking_link_tag:
        add_to_cart_url = booking_link_tag['href']
        print(f"Booking Link: {add_to_cart_url}")
    else:
        add_to_cart_url=""
        print("Booking link not found.")
    date_div = soup.find('div', class_='dgc-summary-schedule-date')

# Extract the date
    date = date_div.find_all('p')[0].get_text(strip=True)

   
    formatted_date = date.strip()  # Ensure no leading/trailing whitespace
    time_range = soup.find('div', class_='dgc-summary-schedule-date').find_all('p')[1].get_text(strip=True)
    start_time_str, end_time_str = [t.strip() for t in time_range.split('-')]

    # Convert the times to the desired format
    start_time_obj = datetime.strptime(start_time_str, "%I:%M %p")
    end_time_obj = datetime.strptime(end_time_str, "%I:%M %p")

    start_time_formatted = start_time_obj.strftime("%H:%M:%S.0000000")
    end_time_formatted = end_time_obj.strftime("%H:%M:%S.0000000")
    location_str = soup.find('div', class_='dgc-listing-header__details').find('p').get_text(strip=True)

# Split the location string
    parts = location_str.split(', ')
    street = parts[0]
    region_country = parts[1].rsplit(' ', 1)
    region = region_country[0]
    country = parts[2]
    return result,add_to_cart_url,formatted_date,start_time_formatted,end_time_formatted,street,region,country


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






def get_event_from_synthony():
    main_page_url = "https://synthony.com"
    articles = scrape_main_page(main_page_url)
    for article in articles:
        save_to_supabase(article)
