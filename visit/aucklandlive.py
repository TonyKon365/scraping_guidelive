import requests
from bs4 import BeautifulSoup
import os
from Utils.open_ai import customize, customizable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from supabase import create_client, Client

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment this line to run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

target_url = 'https://www.aucklandlive.co.nz'
target_id = "aucklandlive"


async def get_events_from_aucklandlive():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.aucklandlive.co.nz/search/events?page=7"
    driver.get(url)
    WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.tile-verticle"))  # Waiting for <article class="coming-soon">
        )
    driver.implicitly_wait(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    raws = soup.find_all('a',class_='tile-verticle')
    for item in raws:
        event_url = "https://www.aucklandlive.co.nz"+item['href']
        event_imgurl =item.find('img')['src']
        event_title = item.find('h4').text.strip()
        event_time = item.find('time').text.strip()
        location=item.find('p',class_='location').text.strip()
        event_description = scrape_detail_page(event_url)
        event_category=item.find('div',class_='further').find_all('p')[1].text.strip()
        article = {
                "target_id": "aucklandlive",
                "target_url": "https://www.aucklandlive.co.nz",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": event_time,
                "end_date": '',
                "event_description": event_description,
                "start_time": '',
                "end_time": "",
                "add_to_cart_url": event_url,
                "event_category":[event_category],
                "event_location": {
                    "title": location,
                    "street": "",
                    "region": "",
                    "country": "New Zealand"
                },
            }
  
        await save_to_supabase(article)

    print("aucklandlive")
    driver.quit()


def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='content-primary')
    event_description=''
    if description_div:
      event_description =description_div.text.strip()

    return event_description

async def save_to_supabase(article):
    # temp_obj = await customize(article)
    # card = customizable(temp_obj)
    # title = card["event_title"]
    # start_date = card["start_date"]

    # existing_article = (
    #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
    #     )
    # if not existing_article.data:
        response = supabase.table("Event1").insert(article).execute()
 

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


