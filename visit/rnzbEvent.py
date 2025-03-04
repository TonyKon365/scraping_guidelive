import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from Utils.open_ai import customize, customizable

async def get_event_from_rnzb():
    main_page_url = "https://rnzb.org.nz/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    row=soup.find_all('div',class_='ShowReel_ShowContent__cxSwb')
    for item in row:

        event_title=item.find('h1').text.strip()
        start_time=item.find('h6').text.strip()
        event_url='https://rnzb.org.nz'+item.find('a')['href']
        event_description=scrape_detail_page(event_url)

        article={
            'target_id': 'rnzbEvent',
            'target_url': 'https://rnzb.org.nz/',
            'event_title': event_title,
            'event_description': event_description,
            'event_category': ['music'],
            "start_date": start_time,  # Convert to string
            "start_time": "",  # Convert to string
            "end_date": '',
            "end_time": "",
            'event_imgurl': '',
            "add_to_cart_url":event_url,
            "event_location": {
                "title" : "St James Theatre",
                "street" : "77–83 Courtenay Place",
                "region" : "Wellington",
                "country" : "New zealand"
                    },
        }
        await save_to_supabase(article)

# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    event_description=soup.find('div',class_='ShowPageHeader_RightSection__UgXU4').text.strip()
    return event_description 


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







