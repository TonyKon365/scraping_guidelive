import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_from_womad():
    url = "https://www.womad.co.nz/lineup/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("a", class_="show-item-link")
    print(len(rows))

    for item in rows:
        # Extract the title and description
        event_url='https://www.womad.co.nz'+item['href']
        event_title=item.find('h3').text
        country=item.find('p',class_='country').text
        event_img="https://www.womad.co.nz"+item.find('source')['srcset']
        evnet_desciption=scrape_detail_page(event_url)
        article={
                "target_id": "womadEvent",
                "target_url": "https://www.womad.co.nz/",
                "event_imgurl": event_img,
                "event_url": "https://www.womad.co.nz/",
                "event_title": event_title,
                "start_date": '',
                "end_date": '',
                "end_time":'',
                "event_description":evnet_desciption,
                "start_time": '',
                "event_category":["show"],
                "add_to_cart_url":event_url,
                "event_location": {
                    "title" : "",
                    "street" :'',
                    "region" : '',
                    "country" : country
                },
            }
        await save_to_supabase(article)


def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")
    detial_data=soup.find('div',class_='details-data mb-2')
    
    event_description_div = soup.find("div", class_="py-5")
    article_content=''
    if event_description_div:
        # Extract all <p> elements within the div
        article_content = event_description_div.find("p").text
    else:
        print("descri not ther",news_url)

 
    return article_content


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    title = article["event_title"]
 
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).execute()
    )

    if not existing_article.data:
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("guideEvent").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")




