import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customizableNews, customizeNews

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
        target_id = article["target_id"]
        existing_article = (
            supabase.table("News").select("*").eq("title", title).eq("target_id", target_id).execute()
        )

        if not existing_article.data:
            try:
                temp_obj = await customizeNews(article)
                card = customizableNews(temp_obj)
                response = supabase.table("News").insert(card).execute()
         
            except Exception as e:
                print(f"Error customizing or inserting article: {e}")
        else:
            print(f"Duplicate article found: {title}")
    except Exception as e:
        print(f"Error checking for existing article: {e}")

def scrape_main_page(main_page_url):
    try:
        response = requests.get(main_page_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {main_page_url}: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        raws = soup.find_all("a", class_="featured-item featured-item--with-summary")
        articles = []

        for item in raws:
            try:
                target_url = 'https://www.wellingtonnz.com' + item['href']
                title = item.find("h2", class_="featured-item__title").text.strip()
                content = item.find("p", class_="featured-item__summary").text.strip()
                img_element = item.find("img", class_="site-picture__img--default site-picture__img")
                img_url = img_element["src"] if img_element else None
                date = ""
                articles.append(
                    {
                        "target_id": "wellingtonnzNews",
                        "target_url": "https://www.wellingtonnz.com/venues-wellington/our-venues",
                        "date": date,
                        "title": title,
                        "imageUrl": img_url,
                        "content": content,
                        "news_url": target_url
                    }
                )
            except Exception as e:
                print(f"Error parsing article item: {e}")

        return articles
    except Exception as e:
        print(f"Error parsing main page content: {e}")
        return []

async def get_news_from_wellingtonnz():
    main_page_url = "https://www.wellingtonnz.com/venues-wellington"
    try:
        articles = scrape_main_page(main_page_url)
        if not articles:
            print("No articles found.")
            return

        for article in articles:
            try:
                await save_to_supabase(article)
            except Exception as e:
                print(f"Error processing article {article['title']}: {e}")
        print("wellingtonnzNews")
    except Exception as e:
        print(f"Error getting news from WellingtonNZ: {e}")