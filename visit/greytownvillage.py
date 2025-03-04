import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_greytownvillage():
    main_page_url = "https://www.greytownvillage.com/greytown-festival-of-christmas-sponsors"
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
  
    event_imgurl = soup.find('img')['src']  
    event_title = soup.find('h2').text.strip()

    event_description=soup.find('div',class_='sqs-block-content')

    h2_tag = event_description.find('h2')
    if h2_tag:
        h2_tag.decompose()  # This will remove the <h2> tag from the soup

    # Extract all the text from the remaining content
    description = event_description.get_text(separator=' ', strip=True)
    
    articles={
                "target_id": "                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ",
                "target_url": "https://www.greytownvillage.com/greytown-festival-of-christmas-sponsors",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": '',
                "end_date": '',                                                                                                                                                                                                                                                                                                                                                                                                                                             
                "event_description": description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":'https://www.greytownvillage.com/greytown-festival-of-christmas-sponsors',
                "event_category":["festival"],
                "event_location": {
                    "title" : '',
                    "street" : "",                                           
                    "region" : "",
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
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("Event1").insert(article).execute()


def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='landing-page-description')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    else:
        description_div1 = soup.find('div',class_='moduleseparator')
        if description_div1:
          event_description=' '.join(p.text.strip() for p in description_div1.find_all('p')) 

    return event_description

