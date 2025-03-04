import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_libertystage():
    main_page_url = "https://www.libertystage.com/current-tours"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('div',class_='index-section no-main-image page')
    articles = []

    for item in raws:
        div_element = item.find('div', class_='ytp-cued-thumbnail-overlay-image')
        event_imgurl=item.find('img')['src']
        event_title = item.find('h1').text.strip()
     
        event_description=item.find('div',class_='sqs-html-content').text.strip()
        articles={
                "target_id": "libertystage",
                "target_url": "https://www.libertystage.com/current-tours",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": '',
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":"https://www.libertystage.com/current-tours",
                "event_category":["tour"],
                "event_location": {
                    "title" : event_title,
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_libertystage")
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id=article["target_id"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("Event1").insert(article).execute()
   

