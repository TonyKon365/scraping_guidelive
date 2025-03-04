import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
from Utils.open_ai import customizableNews, customizeNews

# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    try:
        response = requests.get(f"{url}&page={page}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {url} (page {page}): {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        raws = soup.find_all("div", class_="card-image card-image__secondary")
        articles = []

        for item in raws:
            try:
                title = item.find("h3").get_text(strip=True)
                date_raw = item.find("p").find("span").get_text(strip=True)
                news_url = item.find("a", class_="card-image__image")["href"]
                img_full_url = urljoin("https://www.rotoruanz.com", news_url)
                image_url = item.find("img")["src"]

                date_obj = datetime.strptime(date_raw, "%B %d, %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")

                articles.append(
                    {
                        "target_id": "rotoruanzNews",
                        "target_url": "https://www.rotoruanz.com/stories-articles?type=news",
                        "title": title,
                        "news_url": img_full_url,
                        "imageUrl": image_url,
                        "date": formatted_date,
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
        article_content = soup.find("div", class_="inner-page__content bullet-points--active")
        text = article_content.get_text(separator="\n", strip=True) if article_content else "No content found"
        return text
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

async def get_news_from_rotoruanz():
    main_page_url = "https://www.rotoruanz.com/stories-articles?type=news"
    page = 1
    while True:
        try:
            articles = scrape_main_page(main_page_url, page)
            if not articles:
                break

            for article in articles:
                try:
                    article["content"] = scrape_detail_page(article["news_url"])
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing article {article['title']}: {e}")

            page += 1
        except Exception as e:
            print(f"Error fetching articles from page {page}: {e}")
            break
    print("get_news_from_rotoruanz finished")