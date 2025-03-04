import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# Function to scrape the main page and get article details
async def get_event_premierAU():
    page = 1
    driver = webdriver.Chrome(options=chrome_options)

    while True:
        main_page_url = f"https://premier.ticketek.com.au/shows/whatson.aspx?d=NDays&dn=30&page=1"
        driver.get(main_page_url)
        print(main_page_url)

        try:
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'resultModule'))  # Adjust this based on actual elements on the page
            )

            time.sleep(2)  # Give some additional time for the page to stabilize

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            raws = soup.find_all('div', class_='item')
            print(len(raws))
            if not raws:
                break  # Exit the loop if no items found

            for item in raws:
                event_url = "https://premier.ticketek.com.au" + item.find('a')['href']
                event_imgurl = "https://premier.ticketek.com.au" + item.find('img')['src']
                event_title = item.find('h6').text.strip() if item.find('h6') else ""
                event_description = item.find('div', class_='contentResultSummary').text.strip() if item.find('div', class_='contentResultSummary') else ""
                location = scrape_detail_page(event_url)

                article = {
                    "target_id": "premierAU",
                    "target_url": "https://premier.ticketek.com.au",
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "event_title": event_title,
                    "start_date": '',
                    "end_date": '',
                    "start_time": '',
                    "end_time": '',
                    "event_description": event_description,
                    "event_category": ["music"],
                    "add_to_cart_url": event_url,
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": 'Australia'
                    },
                }
                await save_to_supabase(article)

            print('Page', page)
            page += 1

        except Exception as e:
            print("An error occurred:", e)
            break

    driver.quit()

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
        response = supabase.table("Event1").insert(article).execute()
        print(f"Inserted article: {article}")

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