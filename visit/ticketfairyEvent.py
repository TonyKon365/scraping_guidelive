import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from Utils.open_ai import customize, customizable



def scrape_event_description(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the div with class description and extract its text content
    description_div = soup.find("div", class_="description")
    if description_div:
        # Extract text content from all child elements
        event_description = ' '.join(description_div.stripped_strings)
    else:
        event_description = ""
    
    return event_description



async def get_event_from_ticketfairy():
    main_page_url = "https://www.ticketfairy.com/search-results?type=upcoming"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all("div", class_="type_upcoming")
    print(soup)
    print(len(raws))
    for item in raws:
        event_url = 'https://www.ticketfairy.com'+item.find('a')['href']
        event_imgurl = 'https://www.ticketfairy.com'+item.find('img')['src']
        event_title = item.find('span',class_='event-listing-title').text.strip()
        date_str = item.select_one('.col-60 .orange').text.strip()
        time_str = item.select_one('.col-60 .light-color').text.strip().split('/')[1].strip()
        start_date = datetime.strptime(date_str, '%d %B %Y').date()
        start_time = datetime.strptime(time_str, '%I:%M %p').time()
        event_description = scrape_event_description(event_url)
        location_div=item.find('div',class_='event-location')
        span=location_div.find_all('span')
      
        if(len(span)>1):
            location=span[1].text
            region=span[1].text
            street = span[0].text
        else:
            location=''
            region=''
            street=''
        article={
                "target_id": "ticketfairyEvent",
                "target_url": "https://www.ticketfairy.com/search-results?type=upcoming",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date.isoformat(),  # Convert to string
                "start_time": start_time.isoformat(),  # Convert to string
                "end_date": "",
                "end_time": "",
                "event_description":event_description,     
                "event_category":["music"],
                "add_to_cart_url":event_url,
                "event_location": {
                    "title" : location,
                    "street" : street,
                    "region" : region,
                    "country" : ""
                },
            }
        await save_to_supabase(article)
        
    print("get_event_from_ticketfairy")


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]

    # existing_article = (
    #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
    #     )
    # if not existing_article.data:
    response = supabase.table("Event1").insert(article).execute()

