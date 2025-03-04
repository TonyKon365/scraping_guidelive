from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
from supabase import create_client, Client
import os
import re
from Utils.open_ai import customize, customizable
import requests


# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


def convert(input_value):
    date_object = datetime.strptime(input_value, "%a %d %b %Y")
    output_date = date_object.strftime("%Y-%m-%d")
    return output_date

async def get_event_sydney():
    driver = webdriver.Chrome(options=chrome_options)

# Open the target URL
    url = "https://www.sydney.com/events?10741-classification[]=FESTIVAL"
    driver.get(url)

    # Wait until the page loads
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn.btn-primary.btn-lg.btn-block"))
)

    while True:
        try:
            # Wait for the "Load More" button to be clickable
            load_more_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-lg.btn-block")

            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(6)

        except Exception as e:
            print("No more 'Load More' button or an error occurred:", e)
            break  
    print("click button end")

    # Now extract the HTML from the page source
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        # Find all event items using Beautiful Soup
        div=soup.find('div',class_='product-list__results grid__product-list product-list__results-list')
        event_items = div.find_all('li')  # Adjust the selector based on your needs
        print(len(event_items))
        for item in event_items:
            # Extract relevant information from each event item
            event_title = item.find('h3').text.strip()  # Example selector for the title
            event_description=item.find('div',class_='prod-desc').text.strip()
            event_imgurl=item.find('img')['src']
            start_date=item.find('time',class_='start-date').text.strip()
            end_date=''
            div_end_date=item.find('time',class_='end-date')
            if div_end_date:
                end_date=div_end_date['datetime']+' '+'2024'
            event_url=item.find('a')['href']
            location=scrape_detail_page(event_url)
            articles={
                    "target_id": "sydney",
                    "target_url": "https://www.sydney.com",
                    "event_imgurl": event_imgurl,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "event_description": event_description,
                    "start_time": '',
                    "end_time": "",
                    "add_to_cart_url":event_url,
                    "event_category":["show"],
                    "event_location": {
                        "title" : location,
                        "street" : "",
                        "region" : "",
                        "country" : "Australia"
                    },
                }
            

            await save_to_supabase(articles)
        driver.quit()
        print("get_event_sydney")
    except Exception as e:
        print("No more 'Load More' button or an error occurred:", e)
        driver.quit()
    
        

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)




def scrape_detail_page(event_url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(event_url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    location='Sydney'
    div_location=soup.find('a',class_='product__map-address')
    if div_location:
        location=div_location.text.strip()
  
    return location


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
