
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable
def convert(input_value):
    date_object = datetime.strptime(input_value, "%a %d %b %Y")
    output_date = date_object.strftime("%Y-%m-%d")
    return output_date
# Function to scrape the main page and get article details
async def get_event_enmoretheatreAu():
    main_page_url = "https://www.enmoretheatre.com.au/?s&key=upcoming"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Send the request with headers
    response = requests.get(main_page_url, headers=headers)
    # Check the status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
    else:
        print(f"Error: {response.status_code}")
 
    raws = soup.find_all('a',class_='evt-card') 
    articles = []

    for item in raws:

        event_url =item['href']
        date_div = item.find('div', class_='span-a')
        date_text = date_div.get_text(separator=' ').strip()  # Use separator to handle <br> tags
 
        end_date=''
        start_date=''
        if '-' in date_text:  # Check if '-' is present in the date_text
            start_date, end_date = date_text.split('-')
            start_date = convert(start_date.strip()+' '+'2024')
            end_date = convert(end_date.strip()+' '+'2024')
        else:
            start_date=convert(date_text.strip()+' '+'2024')
        event_title,event_description = scrape_detail_page(event_url)
        event_imgurl=''
        image_span = soup.find('span', class_='image')
        style = image_span['style']
        match = re.search(r'url\((.*?)\)', style)
        if match:
            event_imgurl = match.group(1).strip().strip('"').strip("'")  # Clean up the URL
        articles={
                "target_id": "enmoretheatre",
                "target_url": "https://www.enmoretheatre.com",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": end_date,
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : "NSW",
                    "street" : "118-132 Enmore Road, NEWTOWN",
                    "region" : "NSW, 2042",
                    "country" : "AUSTRALIA"
                },
            }
        
        await save_to_supabase(articles)
    print("get_event_enmoretheatreAu")

    
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Send the request with headers
    response = requests.get(event_url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    print(event_url)
    event_title=soup.find('h1').text
    description_div = soup.find('div', class_='post-content')
    description_text=''
    if description_div:
        description_text = description_div.get_text(separator=' ', strip=True)
    
    return event_title,description_text
