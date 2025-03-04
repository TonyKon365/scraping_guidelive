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


async def get_event_wildfortaranaki():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://action.wildfortaranaki.nz/upcomingevents"
    driver.get(url)

    try:
        # Wait for the main content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'card'))  # Wait for card elements to be present
        )
        
        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Extract the relevant information
        raws = soup.find_all('div', class_='card')

        for item in raws:
            # event_url = item['href']
            image_div = item.find('div', class_='card-img-top hostimagesgrid hostselectinnergridlist')   
            image_url=''
            if image_div:
                # Extract the style attribute
                style = image_div.get('style', '')
                
                # Use regex to find the URL in the background-image style
                match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                if match:
                    image_url = match.group(1)

            event_title=''
            event_category=item.find('div',class_='col-md-12 infotext nopad').text.strip()
            div_event_title = item.find('h2')
            if div_event_title:
                event_title=div_event_title.text.strip()
            start_date=''
            div_start_date = item.find('div', class_='caldisplayhead')
            if div_start_date:
                start_date=div_start_date.text.strip()+' '+'2024' 
            start_time=item.find_all('div',class_='col-md-12 col-sm-3 xol-xs-3 nopad')[1].text.strip()
            print(start_time)
            event_description = item.find('div',class_='innerdescriptionevent').text.strip()
        
            # try:
            current_url=scrape_detail_page()
           
            article = {
                "target_id": "wildfortaranaki",
                "target_url": 'https://action.wildfortaranaki.nz/upcomingevents',
                "event_imgurl": image_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_description": event_description,
                "start_time": start_time,
                "end_time": '',
                "add_to_cart_url":current_url,
                "event_category": [event_category],
                "event_location": {
                    "title": 'Wild for Taranaki',
                    "street": "",
                    "region": "Taranaki",
                    "country": "New zealand"
                },
            }
            print(article)
            await save_to_supabase(article)

    except Exception as e:
        print("An error occurred:", e)
        driver.quit()
        print("get_event_wildfortaranaki")
    finally:
        driver.quit()
        print("get_event_wildfortaranaki")

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





def scrape_detail_page():
    driver = webdriver.Chrome(options=chrome_options)
     
    url = "https://action.wildfortaranaki.nz/upcomingevents"
    driver.get(url)
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'card'))  # Wait for card elements to be present
        )
   
    view_event_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.eventmore'))
            )       
           
    print('view_event_link1',view_event_link)
    current_url=''        
    if view_event_link:
        try:
            print('view_event_link:', view_event_link) 
            driver.execute_script("arguments[0].click();", view_event_link)
            time.sleep(2) 
            current_url = driver.current_url
            print("Current URL after click:", current_url)
        except Exception as e:
            print("Error clicking the 'View Event' link:", str(e))
            current_url = ''    
        driver.quit()
        return current_url