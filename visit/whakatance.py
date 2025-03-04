import requests
import json
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customize, customizable

target_url = 'https://www.whakatane.com'
target_id = 'whakatance'
Server_API_URL = "https://www.whakatane.com/events/art-and-culture"


async def get_events_from_whakatance():
    await get_events_from_whakatance_art()
    await get_events_from_whakatance_community()
    await get_events_from_whakatance_feature()
    await get_events_from_whakatance_sports()


async def get_events_from_whakatance_art():
    url="https://www.whakatane.com/events/art-and-culture"
    raw = requests.get(url)
    soup = BeautifulSoup(raw.content, 'lxml')
    articles=soup.find_all('div',class_='views-row')
    for item in articles:
        event_title = item.find('h3').text.strip()
        event_description = item.find('p').text.strip()
        event_imgurl = target_url + item.find('img')['src']
        detailed_url = target_url + item.find('a')['href']
        raw1 = requests.get(detailed_url)
        soup1 = BeautifulSoup(raw1.content, 'lxml')
        event_time = soup1.find('div', class_='date-recur-date').text.strip()
        region = soup1.find('span', class_='locality').text.strip()
        event_location = soup1.find('span',class_='address-line1').text.strip()
        event_data = {
                    "target_id": target_id,
                    "add_to_cart_url": detailed_url,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['art','culture'],
                    "start_date": event_time,
                    "end_date": "",
                    "start_time": '',
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": region,
                        "country": "New Zealand"
                    }
                }
        await save_to_supabase(event_data)

async def get_events_from_whakatance_community():
    url="https://www.whakatane.com/events/community-events-and-markets"
    raw = requests.get(url)
    soup = BeautifulSoup(raw.content, 'lxml')
    content=soup.find('div',class_='view-content row')
    articles=content.find_all('div',class_='views-row')

    for item in articles:
        event_title = item.find('h3').text.strip()
        event_description = item.find('p').text.strip()
        event_imgurl = target_url + item.find('img')['src']
        detailed_url = target_url + item.find('a')['href']
        raw1 = requests.get(detailed_url)
        soup1 = BeautifulSoup(raw1.content, 'lxml')
        event_time=''
        div_event_time = soup1.find('div', class_='date-recur-occurrences')
        if div_event_time:
            event_time=div_event_time.text.strip()
        else:
            event_time=soup1.find('div',class_='date-recur-date').text.strip()
        region = soup1.find('span', class_='locality').text.strip()
        event_location = soup1.find('span',class_='address-line1').text.strip()
        event_data = {
                    "target_id": target_id,
                    "add_to_cart_url": detailed_url,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['community','markets'],
                    "start_date": event_time,
                    "end_date": "",
                    "start_time": '',
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": region,
                        "country": "New Zealand"
                    }
                }
        await save_to_supabase(event_data)

async def get_events_from_whakatance_feature():
    url="https://www.whakatane.com/events/feature-events"
    raw = requests.get(url)
    soup = BeautifulSoup(raw.content, 'lxml')
    articles=soup.find_all('div',class_='views-row')
    for item in articles:
        event_title = item.find('h3').text.strip()
        event_description = item.find('p').text.strip()
        event_imgurl = target_url + item.find('img')['src']
        detailed_url = target_url + item.find('a')['href']
        raw1 = requests.get(detailed_url)
        soup1 = BeautifulSoup(raw1.content, 'lxml')
        event_time = soup1.find('div', class_='date-recur-date').text.strip()
        region = soup1.find('span', class_='locality').text.strip()
        event_location = soup1.find('span',class_='address-line1').text.strip()
        event_data = {
                    "target_id": target_id,
                    "add_to_cart_url": detailed_url,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['feature'],
                    "start_date": event_time,
                    "end_date": "",
                    "start_time": '',
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": region,
                        "country": "New Zealand"
                    }
                }
        await save_to_supabase(event_data)


async def get_events_from_whakatance_sports():
    url="https://www.whakatane.com/events/sports-and-fishing"
    raw = requests.get(url)
    soup = BeautifulSoup(raw.content, 'lxml')
    articles=soup.find_all('div',class_='views-row')
    for item in articles:
        event_title = item.find('h3').text.strip()
        event_description = item.find('p').text.strip()
        event_imgurl = target_url + item.find('img')['src']
        detailed_url = target_url + item.find('a')['href']
        raw1 = requests.get(detailed_url)
        soup1 = BeautifulSoup(raw1.content, 'lxml')
        event_time = soup1.find('div', class_='date-recur-date').text.strip()
        region = soup1.find('span', class_='locality').text.strip()
        event_location = soup1.find('span',class_='address-line1').text.strip()
        event_data = {
                    "target_id": target_id,
                    "add_to_cart_url": detailed_url,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['sports','fishing'],
                    "start_date": event_time,
                    "end_date": "",
                    "start_time": '',
                    "end_time": "",
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": event_location,
                        "street": "",
                        "region": region,
                        "country": "New Zealand"
                    }
                }
        await save_to_supabase(event_data)


   

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

    

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

