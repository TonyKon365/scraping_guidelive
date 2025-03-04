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
        raws = soup.select(
            "div.fl-post-grid-post.fl-post-grid-image-above-title.fl-post-align-default"
        )
        articles = []

        for item in raws:
            try:
                date = item.find("meta", itemprop="dateModified")["content"]
                title = item.find("h4", class_="fl-post-grid-title").a.text
                imageUrl = item.find("div", itemprop="image").find("meta", itemprop="url")["content"]
                news_url = item.find("a", class_="fl-post-grid-more")["href"]

                articles.append(
                    {
                        "target_id": "voicesnzNews",
                        "target_url": "https://www.voicesnz.com/about/news/",
                        "title": title,
                        "news_url": news_url,
                        "imageUrl": imageUrl,
                        "date": date,
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
        article_content = soup.find("div", class_="omni-post-content")
        text_content = article_content.get_text(separator="\n", strip=True) if article_content else "No content found"
        return text_content
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
        target_id = article["target_id"]
        existing_article = (
            supabase.table("News").select("*").eq("target_id", target_id).eq("title", title).eq("date", date).execute()
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

async def get_news_from_voicesnz():
    main_page_url = "https://www.voicesnz.com/about/news/"
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
        print('voicesnzNews')
    except Exception as e:
        print(f"Error getting news from VoicesNZ: {e}")