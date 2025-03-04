import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
async def get_event_lovetaupo():
    main_page_url_music = "https://www.lovetaupo.com/en/see-do/music-events"
    main_page_url_art_culture ='https://www.lovetaupo.com/en/see-do/art-culture-events/'
    main_page_url_sports ='https://www.lovetaupo.com/en/see-do/sports-events/'
    main_page_url_festival_lifestyle = 'https://www.lovetaupo.com/en/see-do/festival-lifestyle-events/'
    main_page_url_family = 'https://www.lovetaupo.com/en/see-do/family-events/'
    response_music = requests.get(main_page_url_music)
    response_art_culture = requests.get(main_page_url_art_culture)
    response_sports = requests.get(main_page_url_sports)
    response_festival_lifestyle = requests.get(main_page_url_festival_lifestyle)
    response_family = requests.get(main_page_url_family)
    soup = BeautifulSoup(response_music.content, "lxml")
    raws = soup.find_all('li',class_='o-grid__item u-1/1 u-1/2-s u-1/4-l u-1/5-xl')
    articles = []
    for item in raws:
        event_url ='https://www.lovetaupo.com'+item.find('a')['href']
        div_style = soup.find('div', {'class': 'o-event-tile__figure'})['style']
        url_start = div_style.find('url(') + 4
        url_end = div_style.find(')', url_start)
        event_imgurl = div_style[url_start:url_end]
        event_title = item.find('h3').text.strip()
        event_time = item.find('span',class_='o-event-tile__date').text.strip()
        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "lovetaupo",
                "target_url": "https://www.lovetaupo.com/en/see-do/events/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["music"],
                "event_location": {
                    "title" : location,
                    "street" : "The Hub, Level 1, 32 Roberts Street",
                    "region" : "Taupo",
                    "country" : "New Zealand",
                },
            }
        

        await save_to_supabase(articles)
    soup = BeautifulSoup(response_art_culture.content, "lxml")
    raws = soup.find_all('li',class_='o-grid__item u-1/1 u-1/2-s u-1/4-l u-1/5-xl')
    articles = []
    for item in raws:
        event_url ='https://www.lovetaupo.com'+item.find('a')['href']
        div_style = soup.find('div', {'class': 'o-event-tile__figure'})['style']
        url_start = div_style.find('url(') + 4
        url_end = div_style.find(')', url_start)
        event_imgurl = div_style[url_start:url_end]
        event_title = item.find('h3').text.strip()
        event_time = item.find('span',class_='o-event-tile__date').text.strip()
        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "lovetaupo",
                "target_url": "https://www.lovetaupo.com/en/see-do/events/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["art_culture"],
                "event_location": {
                    "title" : location,
                    "street" : "The Hub, Level 1, 32 Roberts Street",
                    "region" : "Taupo",
                    "country" : "New Zealand",
                },
            }
        

        await save_to_supabase(articles)
    soup = BeautifulSoup(response_sports.content, "lxml")
    raws = soup.find_all('li',class_='o-grid__item u-1/1 u-1/2-s u-1/4-l u-1/5-xl')
    articles = []
    for item in raws:
        event_url ='https://www.lovetaupo.com'+item.find('a')['href']
        div_style = soup.find('div', {'class': 'o-event-tile__figure'})['style']
        url_start = div_style.find('url(') + 4
        url_end = div_style.find(')', url_start)
        event_imgurl = div_style[url_start:url_end]
        event_title = item.find('h3').text.strip()
        event_time = item.find('span',class_='o-event-tile__date').text.strip()
        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "lovetaupo",
                "target_url": "https://www.lovetaupo.com/en/see-do/events/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["sports"],
                "event_location": {
                    "title" : location,
                    "street" : "The Hub, Level 1, 32 Roberts Street",
                    "region" : "Taupo",
                    "country" : "New Zealand",
                },
            }
        

        await save_to_supabase(articles)
    soup = BeautifulSoup(response_festival_lifestyle.content, "lxml")
    raws = soup.find_all('li',class_='o-grid__item u-1/1 u-1/2-s u-1/4-l u-1/5-xl')
    articles = []
    for item in raws:
        event_url ='https://www.lovetaupo.com'+item.find('a')['href']
        div_style = soup.find('div', {'class': 'o-event-tile__figure'})['style']
        url_start = div_style.find('url(') + 4
        url_end = div_style.find(')', url_start)
        event_imgurl = div_style[url_start:url_end]
        event_title = item.find('h3').text.strip()
        event_time = item.find('span',class_='o-event-tile__date').text.strip()
        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "lovetaupo",
                "target_url": "https://www.lovetaupo.com/en/see-do/events/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["festival"],
                "event_location": {
                    "title" : location,
                    "street" : "The Hub, Level 1, 32 Roberts Street",
                    "region" : "Taupo",
                    "country" : "New Zealand",
                },
            }
        

        await save_to_supabase(articles)
    soup = BeautifulSoup(response_family.content, "lxml")
    raws = soup.find_all('li',class_='o-grid__item u-1/1 u-1/2-s u-1/4-l u-1/5-xl')
    articles = []
    for item in raws:
        event_url ='https://www.lovetaupo.com'+item.find('a')['href']
        div_style = soup.find('div', {'class': 'o-event-tile__figure'})['style']
        url_start = div_style.find('url(') + 4
        url_end = div_style.find(')', url_start)
        event_imgurl = div_style[url_start:url_end]
        event_title = item.find('h3').text.strip()
        event_time = item.find('span',class_='o-event-tile__date').text.strip()
        event_description,location=scrape_detail_page(event_url)
        articles={
                "target_id": "lovetaupo",
                "target_url": "https://www.lovetaupo.com/en/see-do/events/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["family"],
                "event_location": {
                    "title" : location,
                    "street" : "The Hub, Level 1, 32 Roberts Street",
                    "region" : "Taupo",
                    "country" : "New Zealand",
                },
            }
        

        await save_to_supabase(articles)

    print("get_event_lovetaupo")
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id=article["target_id"]
    article["start_date"]=article["start_date"]+' '+'2024'
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        response = supabase.table("Event1").insert(card).execute()


def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")

    description_div = soup.find('div',class_='c-layout-header__lede')
    event_description=''
    if description_div:
      event_description = ' '.join(p.text.strip() for p in description_div.find_all('p')) 
    div_location=soup.find_all('dd',class_='c-contact__detail')
    location=div_location[2].text.strip()
    return event_description,location

