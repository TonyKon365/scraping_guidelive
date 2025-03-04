import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
from Utils.open_ai import customize, customizable
import time
from datetime import datetime
# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment this line to run in headless mode
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def convert(date_str):
    parsed_date = datetime.strptime(date_str, "%A | %B %d %Y")

    # Format the date to "YYYY-MM-DD"
    formatted_date = parsed_date.strftime("%Y-%m-%d")

    # Print the formatted date
    return formatted_date


async def get_event_unitedcinemas():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.unitedcinemas.co.nz/coming-soon"
    driver.get(url)


    try:
        # Wait for the <article class="coming-soon"> elements to be present in the DOM
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.coming-soon"))  # Waiting for <article class="coming-soon">
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        raws = soup.find_all('article', class_='coming-soon')  # Find all articles with class 'coming-soon'
        print(f'Found {len(raws)} articles.')

        articles = []
        for item in raws:
            event_url = "https://www.unitedcinemas.co.nz"+item.find('a')['href']
            event_imgurl = "https://www.unitedcinemas.co.nz" + item.find('img')['src']
            event_title = item.find('h3').text.strip()
            event_time = item.find('p', class_='coming-soon__date').text.strip()+' '+'2024'
           
         
            event_description = scrape_detail_page(event_url)

            article = {
                "target_id": "unitedcinemas",
                "target_url": "https://www.unitedcinemas.co.nz/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url": event_url,
                "event_category":["movies"],
                "event_location": {
                    "title": 'United Cinemas Bayfair ',
                    "street": "Maunganui Road",
                    "region": "Manganui",
                    "country": "New Zealand"
                },
            }
            articles.append(article)
            await save_to_supabase(article)
        print("get_event_unitedcinemas")
        driver.quit()
    except Exception as e:
        print("An error occurred:", e)
        driver.quit()
    print("get_event_unitedcinemas")

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
    event_description=''
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(event_url)
        WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.single-movie__description"))  # Waiting for <article class="coming-soon">
            )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        div=soup.find('section',class_='single-movie__description')
        print(div)
        if div:
            event_description=div.text.strip()
        else:
            print("div not there in ",event_url)
        print(event_description)
        driver.quit()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()
    return event_description