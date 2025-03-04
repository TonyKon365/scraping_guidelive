import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable

def convert_dates(input_value):
    if " -" in input_value:
        start_str, end_str = input_value.split(" - ")
        start_date = datetime.strptime(start_str.strip() + " 2024", "%d %b %Y").date()
        end_date = datetime.strptime(end_str.strip(), "%d %b %Y").date()
        return start_date.isoformat(),end_date.isoformat()
    else:
        single_date = datetime.strptime(input_value.strip(), "%d %b %Y").date()
        # Format the output
        end_date=''
        return single_date.isoformat(),end_date

async def get_event_manawatunz():
    main_page_url = "https://manawatunz.co.nz/explore/events/"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all('div',class_='event-block')
    articles = []
    for item in raws:
        event_url =item.find('a')['href']
        event_imgurl = "https:"+item.find('img')['src']  
        event_title = item.find('h1').text.strip()
        div=item.find_all('div',class_='ct-text-block')

        location= div[1].text.strip()
        # location=item.find('div',class_='venue mobile truncate').text.strip()
        event_description,event_category,start_date,end_date=scrape_detail_page(event_url)
        articles={
                "target_id": "manawatunz",
                "target_url": "https://manawatunz.co.nz/explore/events",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": start_date+end_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":[event_category],
                "event_location": {
                    "title" : location,
                    "street" : "",
                    "region" : "",
                    "country" : "New zealand"
                },
            }
        

        await save_to_supabase(articles)
    print("get_event_manawatunz")
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
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('span',id='span-354-228870')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    event_category=soup.find('span',id='span-677-228870').text.strip()
    start_date=soup.find('span',id='span-746-228870').text.strip()
    div_end_date=soup.find('span',id='span-747-228870')
    if div_end_date:
        end_date=div_end_date.text.strip()
    return event_description,event_category,start_date,end_date

