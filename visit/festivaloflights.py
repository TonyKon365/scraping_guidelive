import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client


target_url = 'https://www.festivaloflights.nz/'
target_id = 'festivaloflights'
Server_API_URL = "https://www.festivaloflights.nz/"

async def get_events_from_festivaloflights():
    result = []
    response = requests.get(Server_API_URL)
    soup = BeautifulSoup(response.content, "lxml")
    raws = soup.find_all('div', class_='col-lg-6')
    # print(soup)
    print(len(raws))
    for item in raws:
                #title, description, img, time
        event_url ='https://www.festivaloflights.nz'+ item.find('a')['href']
        event_location=item.find('div',class_='festival-location').text.strip()
        start_date=item.find('div',class_='festival-dates').text.strip()
        event_title = item.find('div',class_='festival-heading').text.strip()
                
        raw1 = requests.get(event_url)
        if raw1.status_code == 200:
            soup1 = BeautifulSoup(raw1.content, 'lxml')
                        #location
            event_imgurl='https://www.festivaloflights.nz'+soup1.find_all('img')[1]['src']
            event_description=soup1.find('div',class_='col-sm-12').text.strip()
                        #category
            event_category = ['festival']

            result={
                            "target_id": target_id,
                            "target_url": target_url,
                            "event_title": event_title,
                            "event_description": event_description,
                            "event_category": [event_category],
                            "start_date": start_date,
                            "end_date": "",
                            "start_time":'',
                            "end_time": "",
                             'add_to_cart_url':event_url,              
                            "event_imgurl": event_imgurl,
                             "event_location": {
                                "title" : event_location,
                                "street" : "",
                                "region" : "",
                                "country" : "New Zealand"
                            }
                        }
          
            print(result)
            await save_to_supabase(result)
    print('get_events_from_festivaloflights')

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




url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

