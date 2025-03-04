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

    div_container = soup.find("div", class_="hDJzl4")
    if div_container is None:
        print("Div container not found")
        return []

    # Extract all <li> tags within the found div
   
    raws = div_container.find_all("div",id='comp-lx2eq30u')
    articles = []
    print(len(raws))
    # for item in raws:
    #     a_tag = item.find('a')

    #     # Extract the event URL
    #     event_url = 'https://www.destinationgoldcoast.com'+a_tag['href']

    #     # Locate the <img> tag within the <a> tag
    #     img_tag = a_tag.find('img')

    #     # Extract the image URL
    #     event_imgurl = img_tag['src']

    #     event_title = item.find('h3').text.strip() if item.find('h3') else ""

      
    #     event_description,add_to_cart_url,start_date,start_time,end_time,street,region,country=scrape_detail_page(event_url)
        
    #     articles.append(
    #         {
    #             "target_id": "thefactoryhamiltonEvent",
    #             "target_url": "https://www.thefactoryhamilton.co.nz/",
    #             "event_imgurl": event_imgurl,
    #             "event_url": event_url,
    #             "event_title": event_title,
    #             "start_date": start_date,
    #             "end_date": start_date,
    #             "end_time":end_time,
    #             "event_description": event_description,
    #             "start_time": start_time,
    #             "event_category":"music",
    #             "add_to_cart_url":add_to_cart_url,
    #             "event_location": {
    #                 "title" : event_title,
    #                 "street" :street,
    #                 "region" : region,
    #                 "country" : country
    #             },
    #         }
    #         )

    return articles

def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    event_description_div = soup.find("div", id="event-description")

    if event_description_div:
        # Extract all <p> elements within the div
        article_content = event_description_div.find_all("p")

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

    if date_div:
        date = date_div.find_all('p')[0].get_text(strip=True)
        formatted_date = date.strip()  # Ensure no leading/trailing whitespace
        time_paragraphs = soup.find('div', class_='dgc-summary-schedule-date').find_all('p')
        date = time_paragraphs[0].get_text(strip=True)
        cleaned_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date)
        cleaned_str = re.sub(r'^[A-Za-z]+,\s*', '', cleaned_str).strip()
        try:
            date_obj = datetime.strptime(cleaned_str, "%d %B %Y")
            # Format the datetime object to the desired format
            formatted_date = date_obj.strftime("%Y-%m-%d")
            print(f"start_date: {formatted_date}")
        except ValueError as e:
            print(f"Error parsing date: {e}")
    else:
        formatted_date=""

    start_time_formatted = ""
    end_time_formatted = ""
    # Extract and format the time range, if present
    time_paragraphs = ""
    if len(time_paragraphs) > 1:
        time_range = time_paragraphs[1].get_text(strip=True)
        if '-' in time_range:
            start_time_str, end_time_str = [t.strip() for t in time_range.split('-')]
            
            # Convert the times to the desired format
            start_time_obj = datetime.strptime(start_time_str, "%I:%M %p")
            end_time_obj = datetime.strptime(end_time_str, "%I:%M %p")
            
            start_time_formatted = start_time_obj.strftime("%H:%M:%S.0000000")
            end_time_formatted = end_time_obj.strftime("%H:%M:%S.0000000")
            
            print(f"start_time: {start_time_formatted}")
            print(f"end_time: {end_time_formatted}")
        else:
            print("Time range format is incorrect.")
    else:
        print("Time range is not provided.")

    location_str = soup.find('div', class_='dgc-listing-header__details').find('p').get_text(strip=True)

# Split the location string
    parts = location_str.split(', ')
    street = parts[0]
    region_country = parts[1].rsplit(' ', 1)
    region = region_country[0]
    country = 'Australia'
    return result,add_to_cart_url,formatted_date,start_time_formatted,end_time_formatted,street,region,country


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
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")



async def get_event_from_thefactoryhamilton():
    main_page_url = "https://www.thefactoryhamilton.co.nz/"

    articles = scrape_main_page(main_page_url)
    for article in articles:
      await save_to_supabase(article)
    print("get_event_from_thefactoryhamilton")