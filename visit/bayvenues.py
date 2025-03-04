import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from Utils.open_ai import customize, customizable

Server_API_URL = "https://www.bayvenues.co.nz/what-s-on"
target_id = 'bayvenues'
target_url = 'https://www.bayvenues.co.nz/what-s-on'

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def get_events_from_bayvenues():
    result = []

    page = 1
    page_url = 'https://www.bayvenues.co.nz/search/event?q=&type=&date=&location=&site=default&sort=date_when&limit=6&page={}'

    try:
        page_response = requests.get(page_url.format(page))
        page_response.raise_for_status()
        page_data = page_response.json()
        last_page = page_data.get('last_page', None)
    except requests.RequestException as e:
        print(f"Error fetching initial page: {e}")
        return result
    print(page,last_page)
    while page <= last_page:
        try:
            print(page)
            raw = requests.get(page_url.format(page))
            raw.raise_for_status()
            page_data = raw.json()
            html_content = page_data['html']
            soup = BeautifulSoup(html_content, 'html.parser')
            events = soup.find_all('div', class_='w-full mb-4')
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        except Exception as e:
            print(f"Error parsing page {page}: {e}")
            break

        for event_div in events:
            try:
                event_title = event_div.find('h2').text.strip()
                event_location = event_div.select_one('.card-details p:nth-of-type(2)').text.strip()
                event_description = event_div.select_one('.card-details p:nth-of-type(3)').text.strip()
                event_img_url = 'https://www.bayvenues.co.nz' + event_div.find('img')['src']
                event_url = 'https://www.bayvenues.co.nz' + event_div.find('a')['href']

                response = requests.get(event_url)
                response.raise_for_status()
                soup1 = BeautifulSoup(response.content, "lxml")

                start_date = ''
                start_time = ''
                add_to_cart_url=soup1.find('a')['href']
                address_info_div = soup1.find('div', id='where_address')
                if address_info_div:
                    address_info = address_info_div.find_all('p')
                    if len(address_info) >= 4:
                        start_date = address_info[3].text.split(': ')[0].strip()
                        if len(address_info[3].text.split(': ')) >= 2:
                            start_time = address_info[3].text.split(': ')[1].strip()

                result={
                    'target_id': target_id,
                    'target_url': target_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category': ['Show'],
                    "start_date": start_date,
                    "end_date": "",
                    "start_time": start_time,
                    "end_time": "",
                    'event_imgurl': event_img_url,
                    'add_to_cart_url':event_url,
                    "event_location": {
                        "title": event_location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    }
                }
                await save_to_supabase(result)
            except requests.RequestException as e:
                print(f"Error fetching event details: {e}")
                continue
            except Exception as e:
                print(f"Error processing an event: {e}")
                continue

        
        page += 1


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




