import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
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

# Function to scrape the main page and get article details
async def get_event_stetsongroup():
    url='https://www.stetsongroup.com/'
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "et_pb_gallery_item et_pb_grid_item et_pb_bg_layout_light et_pb_gallery_item_0_2 on_last_row"))
        )
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all("div", class_='et_pb_gallery_item et_pb_grid_item et_pb_bg_layout_light et_pb_gallery_item_0_2 on_last_row')
        print(len(raws))
        articles = []

        for item in raws:
            try:
                event_imgurl =item.find('img')['src']
                
                event_title =item.find('h3')
                
                event_url = item.find('a')['href']

                date, content = scrape_detail_date_page(event_url)
                articles={
                "target_id": "abstract",
                "target_url": "https://abstract.net.au/",
                "event_imgurl": event_imgurl,
                "event_title": event_title,
                "start_date": 'start_date',
                "end_date": '',
                "event_description": 'event_description',
                "start_time": '',
                "end_time": "",
                "add_to_cart_url":event_url,
                "event_category":["tour"],
                "event_location": {
                    "title" : 'Australia',
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                },
            }
                await save_to_supabase(articles)
            except Exception as e:
                print(f"Error parsing article item: {e}")

        return articles
    except Exception as e:
        print(f"Error parsing main page content: {e}")
        return []

# Function to scrape the detail page for date and content
def scrape_detail_date_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {news_url}: {e}")
        return "", ""

    try:
        soup = BeautifulSoup(response.content, "html.parser")

        article_div = soup.find("div", class_="article_text")
        if article_div:
            paragraphs = article_div.find_all("p")
            paragraph_content = [p.get_text(separator=" ") for p in paragraphs]
            content = "\n\n".join(paragraph_content) if paragraph_content else None
        else:
            article_div = soup.find("div", class_="tour_bio")
            if article_div:
                paragraphs = article_div.find_all("p")
                paragraph_content = [p.get_text(separator=" ") for p in paragraphs]
                content = "\n\n".join(paragraph_content) if paragraph_content else None
            else:
                print(f"Article content not found in {news_url}")
                return "", ""

        # Extract date
        date_span = soup.find("span", class_="date")
        if date_span:
            date_text = date_span.get_text(strip=True)
            date_match = re.search(r"\b(\d{1,2}th\s\w+,\s\d{4})\b", date_text)
            if date_match:
                date_str = date_match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, "%dth %B, %Y")
                    date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    date = ""
            else:
                date = ""
        else:
            date_span = soup.find("span", class_="tour-date")
            if date_span:
                date = date_span.get_text(strip=True)
            else:
                date = ""
                print(f"Date content not found in {news_url}")

        return date, content
    except Exception as e:
        print(f"Error parsing detail page content: {e}")
        return "", ""

# Initialize Supabase client
try:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    try:
        title = article["title"]
        date = article["date"]
        existing_article = (
            supabase.table("News").select("*").eq("title", title).eq("date", date).execute()
        )

        if not existing_article.data:
            try:
                response = supabase.table("News").insert(article).execute()
   
            except Exception as e:
                print(f"Error inserting article: {e}")

    except Exception as e:
        print(f"Error checking for existing article: {e}")

