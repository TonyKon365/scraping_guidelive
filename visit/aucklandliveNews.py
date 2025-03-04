import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import json
from Utils.open_ai import customizableNews, customizeNews

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
chrome_options = Options()
chrome_options.add_argument("--ss")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for headless mode


# Function to scrape the main page and get article details
async def get_news_from_aucklandlive():
    driver = webdriver.Chrome(options=chrome_options)
# Open the target URL
    url = "https://www.aucklandlive.co.nz/news" 
    driver.get(url)
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.tile-horizontal"))
    )
    time.sleep(2) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    rows=soup.find_all('a',class_='tile-horizontal')
    print(rows[1])
    print(len(rows))

    for item in rows:
        title=''
        div_title=item.find('h5')
        if div_title:
            title=div_title.text.strip()
        else:
            title=item.find('h3').text.strip()
        content=item.find('p',class_='description').text.strip()
        imageUrl=item.find('img')['src']
        news_url='https://www.aucklandlive.co.nz'+item['href']
        date=scrape_detail_page(news_url)
        articles={
            "target_id": "aucklandliveNews",
            "target_url": "https://www.aucklandlive.co.nz/news",
            "title": title,
            "news_url": news_url,
            "imageUrl": imageUrl,
            "content": content,
            "date": date,
        }
        await save_to_supabase(articles)
    driver.quit()
    print("get_news_from_aucklandlive")
async def save_to_supabase(article):
    title = article["title"]
    date = article["date"]
    target_id = article["target_id"]
    try:
        existing_article = (
            supabase.table("News").select("*").eq("title", title).eq("target_id", target_id).execute()
        )
    except Exception as e:
        print(f"Error checking for existing article: {e}")
        return

    if not existing_article.data:
        try:
            temp_obj = await customizeNews(article)
            card = customizableNews(temp_obj)
            response = supabase.table("News").insert(card).execute()
        except Exception as e:
            print(f"Error inserting article into Supabase: {e}")



def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "lxml")
    description_div = soup.find('div',class_='content-primary')
    start_date=description_div.find('p').text.strip()
    output_date = start_date.split(": ", 1)[1]
    return output_date



url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
