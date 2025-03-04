import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re


# Function to scrape the main page and get article details
async def get_event_sanfran():
    main_page_url = "https://www.sanfran.co.nz/whats-on"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('li')
    articles = []
    print(raws)
    for item in raws:

        event_url = "https://www.sanfran.co.nz"+item.find('a')['href']

        # Extract event image URL
  
        event_imgurl = "https://www.sanfran.co.nz"+item.find('img')['src']      # Extract event title
        event_title = item.find('p',class_='MuiTypography-root MuiTypography-paragraph prisma55 ns-1lo656q').text.strip()
        event_time=''
        time_tag = item.find('time', class_='ns-rpxx7c')

        if time_tag:
            day_span = time_tag.find('span', class_='ns-1x6z45a')
            month_span = time_tag.find_all('span')[1]
            
            # Extract text and strip any extra whitespace
            day = day_span.get_text(strip=True) if day_span else ''
            month = month_span.get_text(strip=True) if month_span else ''
            
            # Format the date
            formatted_date = f"{day} {month}"+" "+'2024'

            start_time,event_description = scrape_detail_page(event_url)


        articles={
                "target_id": "sanfranEvent",
                "target_url": "https://www.sanfran.co.nz/whats-on",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : "San Fran",
                    "street" : "171 Cuba Stree",
                    "region" : "Te Aro, Wellington 6011",
                    "country" : "New Zealand"
                },
            }
        

        await save_to_supabase(articles)

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id=article["target_id"]
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        response = supabase.table("guideEvent").insert(article).execute()
        print(f"Inserted: {article}")
    else:
        print(f"Duplicate found for {title}")

def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    print(event_url)
    start_time=''
    description_div = soup.find('div', {'data-testid': 'aedp-event-information-block'})
    print('description_div',description_div)
    start_time=description_div.find('time')
    if description_div:
        start_time=description_div.get_text()
    event_description=''
    des=soup.find('section',class_='ns-ohmmtl')
    if des:
        paragraphs = des.find_all('p')
        event_description = ' '.join(p.get_text(strip=True) for p in paragraphs)
    else:
        print("Description div not found")

    

    return start_time,event_description

