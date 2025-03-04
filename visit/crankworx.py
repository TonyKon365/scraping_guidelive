import requests
import json
from bs4 import BeautifulSoup
import re
import os
import re
from Utils.open_ai import customize, customizable
from supabase import create_client, Client


target_url = 'https://www.crankworx.com/'
target_id = 'crankworx'
Server_API_URL = "https://www.crankworx.com/rotorua/events/"

async def get_events_from_crankworx():
    result = []
    response = requests.get(Server_API_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    temp = soup.find('div', class_='main-content')
    articles = temp.find_all('a', class_='section__link--button') if temp else None
    print(len(articles))
    for article in articles:
                #title, description, img, time
        event_url = article.get('href')
        event_imgurl = article.find('img').get('src')
        event_title = article.find('div', class_='section__link--button__txt').text.strip()
                
        raw1 = requests.get(event_url)
        if raw1.status_code == 200:
            soup1 = BeautifulSoup(raw1.content, 'lxml')
                        #location
            match = re.search(r"Location:<br>(.*?)<br>", raw1.text)
            event_location = match.group(1) if match else ''                    
            event_category = ['Race']
            script_link = soup1.find('link', {'type': 'application/json'}).get('href')
            script_data = requests.get(script_link)
            json_data = json.loads(script_data.text)
            json_data['startDate'] = json_data['date']
            json_data['endDate'] = json_data['modified']
            soup2 = BeautifulSoup(json_data['content']['rendered'], 'lxml')
            event_description = soup2.text if soup2 else ""
                        #datetime
            event_time = json_data['date']

            result={
                "target_id": target_id,
                 "target_url": target_url,
                 "event_title": event_title,
                 "event_description": event_description,
                 "event_category": event_category,
                 "start_date": event_time,
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
          
     
            await save_to_supabase(result)
    print('get_events_from_crankworx')

async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]

    # existing_article = (
    #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
    #     )
    # if not existing_article.data:
    response = supabase.table("Event1").insert(article).execute()




url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

