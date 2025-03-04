import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    event_title='Plonk'
    event_url = ''

    event_description='The kitchen team Led by head chefConor McdonaLd working alongside James pask riffing off French cLassics breaking the rules  bringing you A bistrotheque'
    articles=[]
    articles.append(
            {
                "target_id": "plonkwinebarEvent",
                "target_url": "https://www.plonkwinebar.co.nz",
                "event_imgurl": 'https://static.wixstatic.com/media/ce95d7_1250e1245836460885af49293681026b~mv2.jpg/v1/fill/w_600,h_600,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/brian-lundquist-53TRIQtQmZg-unsplash_edi.jpg',
                "event_url": "https://www.plonkwinebar.co.nz/",
                "event_title": event_title,
                "start_date": '',
                "end_date": '',
                "end_time":'',
                "event_description": event_description,
                "start_time": '',
                "event_category":["Food"],
                "add_to_cart_url":'',
                "event_location": {
                    "title" : event_title,
                    "street" :'',
                    "region" : '',
                    "country" : 'New zealand'
                },
            }
            )

    return articles


# Initialize Supabase client
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






async def get_event_from_plonkwinebar():
    main_page_url = "https://www.plonkwinebar.co.nz/menu"
    articles = scrape_main_page(main_page_url)
    for article in articles:
        await save_to_supabase(article)
    print("get_event_from_plonkwinebar")