import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from Utils.open_ai import customizableNews, customizeNews
from supabase import create_client, Client

Server_API_URL = "https://www.neckofthewoods.co.nz/events"
target_id = 'neckofthewoods'
target_url = 'https://www.neckofthewoods.co.nz/'

async def get_news_from_neckofthewoods():
    result = []
    try:
        raw = requests.get(Server_API_URL)
        raw.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {Server_API_URL}: {e}")
        return

    try:
        soup = BeautifulSoup(raw.content, 'lxml')
        articles = soup.find_all('article', class_='eventlist-event eventlist-event--upcoming eventlist-event--multiday')
        for article in articles:
            try:
                event_title = article.find('h1', class_='eventlist-title').get_text(strip=True).upper()
                # Extract event time
                event_time_start_month = article.find('div', class_='eventlist-datetag-startdate--month').get_text(strip=True) + " " + "2024"
                event_time_start_day = article.find('div', class_='eventlist-datetag-startdate--day').get_text(strip=True)
                event_time_end = article.find('div', class_='eventlist-datetag-enddate').get_text(strip=True)
                event_time = f"{event_time_start_month} {event_time_start_day} {event_time_end}"

                # Extract event image URLs
                img_tag = article.find('img', {'data-image': True})
                event_img_url = img_tag['srcset'] if img_tag else ""

                # Extract event description
                description_blocks = article.find_all('div', class_='sqs-block-content')
                event_description = "\n".join(block.get_text(strip=True) for block in description_blocks).strip()

                # Extract event URL
                event_url = article.find('div', class_='sqs-block-button-container').find('a')['href']
                result.append(
                    {
                        'target_id': target_id,
                        'target_url': event_url,
                        'title': event_title,
                        'content': event_description,
                        "date": event_time,
                        'news_url': event_url,
                        'imageUrl': event_img_url,
                    }
                )
            except Exception as e:
                print(f"Error parsing article item: {e}")
    except Exception as e:
        print(f"Error parsing main page content: {e}")

    await save_to_supabase(result)
    print("neckofthewoodsNews")

async def save_to_supabase(articles):
    for article in articles:
        try:
            target_id = article["target_id"]
            title = article["title"]
            existing_article = (
                supabase.table("News").select("*").eq("title", title).eq("target_id", target_id).execute()
            )

            if not existing_article.data:
                try:
                    temp_obj = await customizeNews(article)
                    card = customizableNews(temp_obj)
                    response = supabase.table("News").insert(card).execute()
                
                except Exception as e:
                    print(f"Error customizing or inserting article: {e}")
      
        except Exception as e:
            print(f"Error checking for existing article: {e}")

# Initialize Supabase client
try:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

