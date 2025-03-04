import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customizableNews, customizeNews

# Function to scrape the main page and get article details
def scrape_main_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {url}: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        raws = soup.find_all("article", class_="blog-basic-grid--container entry blog-item")
        articles = []

        for item in raws:
            try:
                news_url = item.find("a", class_="image-wrapper")["href"]
                image_url = (
                    item.find("img", class_="image")["srcset"]
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                )
                title = item.find("h1", class_="blog-title").get_text(strip=True)
                full_url = urljoin("https://www.taupowinterfestival.co.nz", news_url)

                articles.append(
                    {
                        "target_id": "taupowinterfestivalNews",
                        "target_url": "https://www.taupowinterfestival.co.nz/news-updates",
                        "title": title,
                        "news_url": full_url,
                        "imageUrl": image_url,
                        "date": "",
                    }
                )
            except Exception as e:
                print(f"Error parsing article item: {e}")

        return articles
    except Exception as e:
        print(f"Error parsing main page content: {e}")
        return []

# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching detail page {news_url}: {e}")
        return "No content found"

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        article_content=''
        des_div=soup.find("div", class_="sqs-html-content")
        if des_div:
            article_content=des_div.get_text(separator="\n").strip()
        
        return article_content
    except Exception as e:
        print(f"Error parsing detail page content: {e}")
        return "No content found"

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
            supabase.table("News").select("*").eq("title", title).execute()
        )

        if not existing_article.data:
            try:
                temp_obj = await customizeNews(article)
                card = customizableNews(temp_obj)
                response = supabase.table("News").insert(card).execute()

            except Exception as e:
                print(f"Error customizing or inserting article: {e}")

    except Exception as e:
        print(f"Error checking for existing article: {e}")

async def get_news_from_taupowinterfestival():
    main_page_url = "https://www.taupowinterfestival.co.nz/news-updates"
    try:
        articles = scrape_main_page(main_page_url)
        if not articles:
            print("No articles found.")
            return

        for article in articles:
            try:
                article["content"] = scrape_detail_page(article["news_url"])
                await save_to_supabase(article)
            except Exception as e:
                print(f"Error processing article {article['title']}: {e}")
        print('taupowinterfestivalNews')
    except Exception as e:
        print(f"Error getting news from Taupo Winter Festival: {e}")

