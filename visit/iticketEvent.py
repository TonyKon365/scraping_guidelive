import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

# Function to scrape the main page and get article details
async def get_event_from_iticket():
    main_page_url = "https://www.iticket.co.nz/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="w-52 max-sm:snap-center shrink-0")
    articles = []

    for item in raws:

        event_url = "https://www.iticket.co.nz"+item.find('a', {'data-testid': True})['href']

        # Extract event image URL
        event_img = item.find('img', {'alt': True})
        event_imgurl = "https://www.iticket.co.nz"+event_img['srcset'].split(',')[0].strip().split(' ')[0]

        # Extract event title
        event_title = item.find('p', {'class': 'text-lg font-semibold text-black'}).text.strip()


        div_tags = soup.find_all('div', class_='w-52 max-sm:snap-center shrink-0')

# Extract the href attributes from nested <a> tags
        
        a_tag = item.find('a', href=True)
        event_description = scrape_detail_page(event_url)
       

        # Extract event location
        event_location = item.find('span', {'class': 'flex gap-0.5 items-center p-1 rounded-lg w-fit text-sm bg-gray-100 text-gray-800 max-w-full'}).text.strip()
        date_span = item.find('div', {'class': 'hidden sm:flex items-center absolute bottom-2 right-2 ml-2 p-1 rounded-lg text-sm bg-indigo-100 text-indigo-800'})
        date = date_span.find('span').text.strip()

        articles={
                "target_id": "iticketEvent",
                "target_url": "https://www.iticket.co.nz/",
                "event_imgurl": event_imgurl,
              
                "event_title": event_title,
                "start_date": date,
                "end_date": '',
                "event_description": event_description,
                "start_time": "",
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : event_location,
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                },
            }
        await save_to_supabase(articles)

    print("get_event_from_iticket")

# Initialize Supabase client
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






def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")


    description_div = soup.find('div',id='event_details_container')
    print('event_url',event_url,description_div)
    event_description=''
# Extract text from all paragraphs within the div
    if description_div:
        paragraphs = description_div.find_all('p')
        event_description = ' '.join(p.get_text(strip=True) for p in paragraphs)
    else:
        print("Description div not found")

    return event_description

