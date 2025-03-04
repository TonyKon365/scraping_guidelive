import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from Utils.open_ai import customize, customizable
# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Initialize the WebDriver


async def get_event_waikatonz():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.waikatonz.com/events/?sort=date"
    driver.get(url)

    try:
        time.sleep(4)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        raws = soup.find_all('li', class_='c-event-result')
        print(f"Found {len(raws)} event results.")

        articles = []
        for item in raws:
            # Check if the item has an 'a' tag with 'href'
            link_tag = item.find('a')
            if link_tag and 'href' in link_tag.attrs:
                event_url = 'https://www.waikatonz.com' + link_tag['href']
            else:
                print("No link found for item:", item)
                continue  # Skip this item if no link is found

            event_image_tag = item.find('img')
            if event_image_tag and 'src' in event_image_tag.attrs:
                event_image = 'https://www.waikatonz.com' + event_image_tag['src']
            else:
                print("No image found for item:", item)
                continue  # Skip this item if no image is found

            event_title = item.find('div', class_='c-event-tile__title').text.strip()
            event_time = item.find('div', class_='c-event-tile__date').text.strip()
            event_description = scrape_detail_page(event_url)
          
            article = {
                "target_id": "waikatonz",
                "target_url": 'https://www.waikatonz.com/events/?sort=date',
                "event_imgurl": event_image,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": '',
                "add_to_cart_url": event_url,
                "event_category": ['show'],
                "event_location": {
                    "title": 'Waikato',
                    "street": "",
                    "region": "Waikato region",
                    "country": "New zealand"
                },
            }

            await save_to_supabase(article)

    except Exception as e:
        print("An error occurred:", e)
        print("get_event_waikatonz")
        driver.quit()
    finally:
        driver.quit()
        print("get_event_waikatonz")
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


 

def scrape_detail_page(event_url):
    print(event_url)
    response = requests.get(event_url)

    soup = BeautifulSoup(response.content, "lxml")
 
    description_div = soup.find('div',class_='c-detailed-component__details-text')
    if description_div:
        event_description =description_div.text.strip()

    return event_description