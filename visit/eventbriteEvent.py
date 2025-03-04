import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from Utils.open_ai import customize, customizable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


target_id = 'eventbriteNZ'
target_url = 'https://www.eventbrite.co.nz/d/new-zealand/events/'

async def get_event_from_eventbriteNZ():
    await get_event_from_eventbriteMusic()
    await get_event_from_eventbritebusiness()
    await get_event_from_eventbritefood()
    await get_event_from_eventbriteHealth()
    await get_event_from_eventbritearts()
    print('get_event_from_eventbriteNZ')
async def get_event_from_eventbriteMusic():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.eventbrite.co.nz/b/new-zealand/music/"
    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-card-simple-carousel-slide"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all('div',class_='simple-carousel__slide__tablet--two')
        print(len(raws))
        for item in raws:
            event_title_element = item.find('h3')
            event_url_element = item.find('a')
            event_img_element = item.find('img')

            # Check if elements are found
            if event_title_element and event_url_element and event_img_element:
                event_title = event_title_element.text.strip()
                event_url = event_url_element['href']
                event_imgurl = event_img_element['src']

                response1 = requests.get(event_url)
                soup1 = BeautifulSoup(response1.content, "lxml")

                location_element = soup1.find('p', class_='location-info__address-text')
                div_event_time = soup1.find('span', class_='date-info__full-datetime')

                # Check if location and time elements exist
                location = location_element.text.strip() if location_element else 'Location not found'
                start_date = end_date = ''

                if div_event_time:
                    event_time = div_event_time.text.strip()
                    if '-' in event_time:
                        start_date, end_date = event_time.split('-')
                    else:
                        start_date = event_time

                    event_description_element = soup1.find('div', class_='structured-content-rich-text')
                    event_description = event_description_element.text.strip() if event_description_element else ''
                    
                    obj = {
                        "target_id": target_id,
                        "target_url": target_url,
                        "event_title": event_title,
                        "event_description": event_description,
                        "event_category": ['music'],
                        "start_date": start_date,
                        "start_time": '',  # Convert to string if needed
                        "end_date": end_date,
                        "end_time": "",
                        "add_to_cart_url": event_url,
                        "event_imgurl": event_imgurl,
                        "event_location": {
                            "title": location,
                            "street": '',
                            "region": '',
                            "country": "New Zealand"
                        },
                    }
                    await save_to_supabase(obj)
            else:
                print("One or more elements were not found in the event card.")
        print('get_event_from_eventbriteMusic')
        driver.quit()
    
    except Exception as e:
        print(f"Error parsing events page: {e}")
        driver.quit()
        return

async def get_event_from_eventbritebusiness():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.eventbrite.co.nz/b/new-zealand/business/"
    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-card-simple-carousel-slide"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all('div',class_='event-card-simple-carousel-slide')
        for item in raws:
            event_title=item.find('h3').text.strip()
            event_url=item.find('a')['href']
            event_imgurl=item.find('img')['src']
            response1 = requests.get(event_url)
            soup1 = BeautifulSoup(response1.content, "lxml")
            location=soup1.find('p',class_='location-info__address-text').text.strip()
            start_date=''
            end_date=''
            div_event_time=soup1.find('span',class_='date-info__full-datetime')
            event_description=''
            if div_event_time:
                event_time=div_event_time.text.strip()
                if '-' in event_time:
                    start_date,end_date=event_time.split('-')
                else:
                    start_date=event_time
                div_event_description=soup1.find('div',class_='structured-content-rich-text')
                if div_event_description:
                    event_description=div_event_description.text.strip()
                obj = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['business'],
                    "start_date": start_date,  # Convert to string
                    "start_time": '',  # Convert to string
                    "end_date": end_date,
                    "end_time": "",
                    "add_to_cart_url": event_url,
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(obj)
        print('get_event_from_eventbriteBusiness')
        driver.quit()
    
    except Exception as e:
        print(f"Error parsing events page: {e}")
        driver.quit()
        return

async def get_event_from_eventbritefood():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.eventbrite.co.nz/b/new-zealand/food-and-drink/"
    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-card-simple-carousel-slide"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all('div',class_='event-card-simple-carousel-slide')
        for item in raws:
            event_title=item.find('h3').text.strip()
            event_url=item.find('a')['href']
            event_imgurl=item.find('img')['src']
            response1 = requests.get(event_url)
            soup1 = BeautifulSoup(response1.content, "lxml")
            location=soup1.find('p',class_='location-info__address-text').text.strip()
            start_date=''
            end_date=''
            div_event_time=soup1.find('span',class_='date-info__full-datetime')
            if div_event_time:
                event_time=div_event_time.text.strip()
                if '-' in event_time:
                    start_date,end_date=event_time.split('-')
                else:
                    start_date=event_time
                event_description_element = soup1.find('div', class_='structured-content-rich-text')
                event_description = event_description_element.text.strip() if event_description_element else ''
                    
                obj = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['food'],
                    "start_date": start_date,  # Convert to string
                    "start_time": '',  # Convert to string
                    "end_date": end_date,
                    "end_time": "",
                    "add_to_cart_url": event_url,
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(obj)
        print('get_event_from_eventbritefood')
        driver.quit()
    
    except Exception as e:
        print(f"Error parsing events page: {e}")
        driver.quit()
        return

async def get_event_from_eventbriteHealth():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.eventbrite.co.nz/b/new-zealand/health/"
    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-card-simple-carousel-slide"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all('div',class_='event-card-simple-carousel-slide')
        for item in raws:
            event_title=item.find('h3').text.strip()
            event_url=item.find('a')['href']
            event_imgurl=item.find('img')['src']
            response1 = requests.get(event_url)
            soup1 = BeautifulSoup(response1.content, "lxml")
            location=soup1.find('p',class_='location-info__address-text').text.strip()
            start_date=''
            end_date=''
            div_event_time=soup1.find('span',class_='date-info__full-datetime')
            if div_event_time:
                event_time=div_event_time.text.strip()
                if '-' in event_time:
                    start_date,end_date=event_time.split('-')
                else:
                    start_date=event_time
             
                event_description_element = soup1.find('div', class_='structured-content-rich-text')
                event_description = event_description_element.text.strip() if event_description_element else ''
                    
                obj = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['health'],
                    "start_date": start_date,  # Convert to string
                    "start_time": '',  # Convert to string
                    "end_date": end_date,
                    "end_time": "",
                    "add_to_cart_url": event_url,
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(obj)
        print('get_event_from_eventbriteHealth')
        driver.quit()
    
    except Exception as e:
        print(f"Error parsing events page: {e}")
        driver.quit()
        return

async def get_event_from_eventbritearts():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.eventbrite.co.nz/b/new-zealand/arts/"
    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-card-simple-carousel-slide"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all('div',class_='event-card-simple-carousel-slide')
        for item in raws:
            event_title=item.find('h3').text.strip()
            event_url=item.find('a')['href']
            event_imgurl=item.find('img')['src']
            response1 = requests.get(event_url)
            soup1 = BeautifulSoup(response1.content, "lxml")
            location=soup1.find('p',class_='location-info__address-text').text.strip()
            start_date=''
            end_date=''
            div_event_time=soup1.find('span',class_='date-info__full-datetime')
            if div_event_time:
                event_time=div_event_time.text.strip()
                if '-' in event_time:
                    start_date,end_date=event_time.split('-')
                else:
                    start_date=event_time
             
                event_description_element = soup1.find('div', class_='structured-content-rich-text')
                event_description = event_description_element.text.strip() if event_description_element else ''
                    
                obj = {
                    "target_id": target_id,
                    "target_url": target_url,
                    "event_title": event_title,
                    "event_description": event_description,
                    "event_category": ['arts'],
                    "start_date": start_date,  # Convert to string
                    "start_time": '',  # Convert to string
                    "end_date": end_date,
                    "end_time": "",
                    "add_to_cart_url": event_url,
                    "event_imgurl": event_imgurl,
                    "event_location": {
                        "title": location,
                        "street": '',
                        "region": '',
                        "country": "New Zealand"
                    },
                }
                await save_to_supabase(obj)
        print('get_event_from_eventbritearts')
        driver.quit()
    
    except Exception as e:
        print(f"Error parsing events page: {e}")
        driver.quit()
        return





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


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

