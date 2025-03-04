import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from Utils.open_ai import customize, customizable
from supabase import create_client, Client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')) 

Server_API_URL = 'https://www.taupowinterfestival.co.nz/whats-on'
target_id = 'taupowinterfestival'
target_url='https://www.taupowinterfestival.co.nz'

async def get_events_from_taupowinterfestival():
    try:
        response = requests.get(Server_API_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
       
    except requests.RequestException as e:
        print(f"Error fetching events page: {e}")
        return
    except Exception as e:
        print(f"Error parsing events page: {e}")
        return

    card_tags = soup.find_all('div',class_='summary-thumbnail-outer-container')
    print(len(card_tags))
  
    for item in card_tags:
        try:
           
            event_imgurl =item.find('img')['data-src']
            event_url=target_url+item.find('a')['href']
            event_title,start_date,location,event_description=scrape_detail_page(event_url)
            result = {
                "target_id": target_id,
                "target_url": target_url,
                "event_title": event_title,
                "event_description": event_description,
                "event_category": ['music'],
                "add_to_cart_url": event_url,
                "start_date": start_date,
                "end_date": "",
                "start_time": "",
                "end_time": "",
                "event_imgurl": event_imgurl,
                "event_location": {
                    "title": location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                },

            }
            await save_to_supabase(result)
        except Exception as e:
            print(f"Error processing event: {e}")
            continue

    print("get_events_from_taupowinterfestival")

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



def scrape_detail_page(event_url):

    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    
    event_title = soup.find('h1').text.strip()
    article = soup.find('article', id='article-')
    info = article.find_all('p')   
    start_date = info[0].text.strip()+' '+'2024'  +info[1].text.strip() 
    event_description = ''
    for i in range(21, len(info)):  
        event_description += info[i].text.strip() + ' '
    location = info[2].text.strip() 
    return event_title, start_date, location, event_description


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

