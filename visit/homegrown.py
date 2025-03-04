import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import time
import re
from Utils.open_ai import customize, customizable

# Set up Chrome options for headless mode

# Function to scrape the main page and get article details
async def get_event_homegrown():

    event_imgurl = 'https://homegrown.flicket.co.nz'+'/_next/image?url=https%3A%2F%2Fstorage.googleapis.com%2Fflicket-uploads%2Fevents%2F2ea31011-8ed0-4c92-8bbd-1d9a88c3fa14%2Ff28c5f83-22fe-4050-a8ae-a6f96b0ff562.webp&w=1200&q=75 1x, /_next/image?url=https%3A%2F%2Fstorage.googleapis.com%2Fflicket-uploads%2Fevents%2F2ea31011-8ed0-4c92-8bbd-1d9a88c3fa14%2Ff28c5f83-22fe-4050-a8ae-a6f96b0ff562.webp&w=3840&q=75 2x'
    event_title = 'Jim Beam Homegrown 2025'
    event_description="ABOUT THE FESTIVAL:  Get ready for an electrifying experience at Jim Beam Homegrown 2025! Spanning across five massive stages on the stunning Wellington waterfront, this festival is the ultimate celebration of Aotearoa’s musical prowess. We're kicking things up a notch this year with an extra special Friday night kickoff at Park Stage, starting at 5:30pm."
    articles={
                "target_id": "homegrown",
                "target_url": "https://homegrown.flicket.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date":   '2025-03-14',
                "end_date": '2025-03-15',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":'https://homegrown.flicket.co.nz/',
                "event_category":["music"],
                "event_location": {
                    "title" : 'Wellington Waterfront',
                    "street" : "",
                    "region" : "Wellington",
                    "country" : "New zealand"
                },
            }
        

    await save_to_supabase(articles)
    print("get_event_homegrown")
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





