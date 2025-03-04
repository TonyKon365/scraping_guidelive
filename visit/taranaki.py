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
from Utils.open_ai import customize, customizable
# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode

# Initialize the WebDriver


async def get_event_taranaki():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.taranaki.co.nz/visit/whats-on/"
    driver.get(url)
    try:
        # Wait for the main content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'card'))  # Wait for card elements to be present
        )
        time.sleep(4)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Extract the relevant information
        raws = soup.find_all('a', class_='card')
        print(f"Found {len(raws)} events.")

        articles = []
        for item in raws:
            event_url = item['href']
            event_imgurl = "https:" + item.find('img')['src']
            event_title = item.find('h6').text.strip()
            # event_time = item.find('span', class_='h6 btn-card').text.strip() if item.find('div', class_='date truncate') else "No date"
        
            event_description ,event_time,location= scrape_detail_page(event_url)
            category=item.find('span',class_='sub-title').text.strip()
            article = {
                "target_id": "taranaki",
                "target_url": url,
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": '',
                "add_to_cart_url": event_url,
                "event_category": [category],
                "event_location": {
                    "title": location,
                    "street": "",
                    "region": "",
                    "country": "New zealand"
                },
            }

            await save_to_supabase(article)

    except Exception as e:
        print("An error occurred:", e)
        driver.quit()
        print("get_event_taranaki")
    finally:
        driver.quit()
        print("get_event_taranaki")

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id = article["target_id"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        response = supabase.table("Event1").insert(article).execute()


def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div', id='eventDescription')
    event_description = ''
    if description_div:
        event_description = ' '.join(p.text.strip() for p in description_div.find_all('p'))
    event_time= soup.find('span',class_='date').text.strip()
    location=soup.find('span',class_='d-none d-md-inline').text.strip()
    return event_description,event_time,location