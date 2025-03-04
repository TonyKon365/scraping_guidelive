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
async def get_news_from_undertheradar():
    url='https://www.undertheradar.co.nz/utr/news'
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".news-item"))
        )
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        raws = soup.find_all("div", class_='news-item')
        print(raws[0])
        articles = []

        for item in raws:
            try:
                imageUrl =item.find('img',class_='lazy')['data-original']
                title =item.find('div',class_='item_text').find('a').text.strip()
                news_url = 'https://www.undertheradar.co.nz' + item.find('div',class_='item_text').find('a')['href']

                date, content = scrape_detail_date_page(news_url)
                articles={
                        "target_id": "undertheradarNews",
                        "target_url": "https://www.undertheradar.co.nz/utr/news",
                        "title": title,
                        "news_url": news_url,
                        "imageUrl": imageUrl,
                        "date": date,
                        "content": content,
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

