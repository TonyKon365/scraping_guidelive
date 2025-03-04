import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Convert date to ‘YYYY-MM-DD’ string
def convert(input_value):
    date_object = datetime.strptime(input_value, "%d %B %Y")  # Adjusted format
    output_date = date_object.strftime("%Y-%m-%d")
    return output_date  # Return as string

async def get_event_queenstownnz():
    page = 0
    driver = webdriver.Chrome(options=chrome_options)

    while True:
        main_page_url = f"https://www.queenstownnz.co.nz/things-to-do/events/event-calendar/?view=list&sort=date&skip={page}"
        driver.get(main_page_url)
        logging.info(f"Accessing URL: {main_page_url}")

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'item'))
            )
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            rows = soup.find_all('div', class_='item')

            if not rows:
                logging.info("No more events found.")
                break

            for item in rows:
                # Extract event details
                event_title = item.find('h4').text.strip()
                event_imgurl = item.find('img')['src']

                # Extract start date
                start_date_raw = item.find('span', class_='day').text.strip()
                end_date = ''
                if 'to' in start_date_raw:
                    start_date_str, end_date_str = start_date_raw.split(" to ")
                    start_date = convert(f"{start_date_str} 2024").isoformat()
                    end_date = convert(f"{end_date_str} 2024").isoformat()
                else:
                    start_date = convert(f"{start_date_raw} 2024").isoformat()
                event_url = "https://www.queenstownnz.co.nz" + item.find('a')['href']
                event_description, start_time, street, region = scrape_detail_page(event_url)

                location = item.find('li', class_='locations').text.strip()
                articles = {
                    "target_id": "queenstownnz",
                    "target_url": "https://www.queenstownnz.co.nz",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,  # Already a string
                    "end_date": end_date or None,  # Handle None case
                    "event_description": event_description,
                    "start_time": start_time,
                    "end_time": "",
                    "add_to_cart_url": event_url,
                    "event_category": ["movie"],
                    "event_location": {
                        "title": location,
                        "street": street,
                        "region": region,
                        "country": "New Zealand"
                    },
                }

                await save_to_supabase(articles)

            logging.info(f'Processed page: {page}')
            page += 12

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            driver.quit()
            print("get_event_queenstownnz")
        finally:
            driver.quit()
            print("get_event_queenstownnz")
    logging.info('Completed scraping from QueenstownNZ')

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_to_supabase(article):
    title = article["event_title"]
    target_id = article["target_id"]
    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("target_id", target_id).execute()
    )

    if not existing_article.data:
        response = supabase.table("Event1").insert(article).execute()
        logging.info(f"Inserted article: {title}")

def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div', class_='description')

    event_description = ''
    if description_div:
        event_description = ' '.join(p.text.strip() for p in description_div.find_all('p'))

    div_start_time = soup.find('p', class_='date times')
    start_time = ''
    if div_start_time:
        start_time = div_start_time.text.strip()

    address = soup.find_all('p')
    street = address[0].text.strip() if len(address) > 0 else ''
    region = address[1].text.strip() if len(address) > 1 else ''

    return event_description, start_time, street, region