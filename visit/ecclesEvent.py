import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

def scrape_event_description(event_url):

    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    event_title=soup.find('h2').get_text()
    # Find the div with class description and extract its text content
    div_strong=soup.find('div',class_='sqs-html-content')
    strong=div_strong.find_all('strong')
    event_time=strong[0].get_text()
    event_location=strong[1].get_text()

# Extract all <p> tags within that <div>
    div_container=soup.find('div',class_='sqs-block html-block sqs-block-html')
    if div_container:
      paragraphs = div_container.find_all("p")
      # Extract and print the text content of each <p> tag
      for p in paragraphs:
          event_description=p.get_text(separator=" ")
    else:
        print("The specified <div> was not found.")
   
    return event_title,event_description,event_time,event_location
    
     
# Function to scrape the main page and get article details
async def get_event_from_eccles():
    main_page_url = "https://eccles.co.nz/touring"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    soup1=soup.find('div',id='block-yui_3_17_2_1_1643229216977_1792')
    raws = soup1.find_all("a", class_="image-slide-anchor content-fill")
 

    for item in raws:
        event_url = 'https://eccles.co.nz'+item['href']
        event_imgurl =item.find('img')['src']
        event_title,event_description,event_time,event_location, = scrape_event_description(event_url)
        articles={
                "target_id": "ecclesEvent",
                "target_url": "https://eccles.co.nz/touring",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date":event_time,  # Convert to string
                "end_date": "",
                "event_description":event_description,
                "start_time": '',  # Convert to string
                "end_time": "",
                "event_category":["music"],
                "add_to_cart_url":event_url,
                "event_location": {
                    "title" : event_location,
                    "street" : '',
                    "region" : '',
                    "country" : "New zealand"
                },
            }
        await save_to_supabase(articles)
        
    print("get_event_from_eccles")

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







