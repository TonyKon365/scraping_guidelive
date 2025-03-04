import aiohttp
from bs4 import BeautifulSoup
from Utils.open_ai import customize, customizable
from supabase import create_client, Client
import os

target_url = 'https://www.wellingtonnz.com'
target_id = 'wellingtonnz'
Server_API_URL = "https://www.wellingtonnz.com/visit/events"

async def get_events_from_wellingtonnz():
    result = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(Server_API_URL) as response:
                raw = await response.read()
                soup = BeautifulSoup(raw, 'lxml')
                carousel = soup.find('div', class_='scroll-carousel')
                articles = carousel.find_all('a', class_='featured-item highlighted-item') if carousel else None
        except aiohttp.ClientError as e:
            print(f"Error fetching events page: {e}")
            return
        except Exception as e:
            print(f"Error parsing events page: {e}")
            return

        for article in articles:
            try:
                detail_url = target_url + article.get('href')
                event_title = article.find('h2', class_='featured-item__title').text.strip()
                img_tag = article.find('img', class_='site-picture__img--default site-picture__img')
                event_imgurl = img_tag.get('src') if img_tag else ""

                async with session.get(detail_url) as response:
                    raw1 = await response.read()
                    soup1 = BeautifulSoup(raw1, 'lxml')
                        # time
                    time_tag = soup1.find('ul', class_='image-header__details-list--primary')
                    event_time = time_tag.text.strip() if time_tag else ""
                        # location
                    location_tag = soup1.find('ul', class_='image-header__details-list--secondary')
                    event_location = location_tag.text.strip() if location_tag else ""
                        # category
                    event_category = 'Visit'
                    event_description = ""
                    typography_div = soup1.find('div', class_='typography')
                    if typography_div:
                        paragraphs = typography_div.find_all('p')
                        for p in paragraphs:
                            event_description += p.get_text(strip=True) + " "
              
                
                    result.append({
                            "target_id": target_id,
                            "target_url": target_url,
                            "event_title": event_title,
                            "event_description": event_description.strip(),
                            "event_category": [event_category],
                            "start_date": event_time,
                            "end_date": '',
                            "end_time": "",
                            "start_time": "",
                            "add_to_cart_url": detail_url,
                            "event_location": {
                                "title": event_location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            },
                            "event_imgurl": event_imgurl,
                        })

            except Exception as e:
                print(f"Error processing an event: {e}")
                continue

        await save_to_supabase(result)
    print("get_events_from_wellingtonnz")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(articles):
    for article in articles:
        temp_obj = await customize(article)
        card = customizable(temp_obj)
        title = card["event_title"]
        start_date = card["start_date"]

        existing_article = (
            supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
            )
        if not existing_article.data:
            response = supabase.table("Event1").insert(card).execute()



