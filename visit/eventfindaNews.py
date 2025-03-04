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
        print(f"Error fetching main page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    try:
        raws_prefix = soup.select_one("div.module.news.clearfix")
        raws = soup.select_one("div.module.listings-basic.news.clearfix").select(
            "div.col-lg-4.col-md-6.col-12"
        )
    except AttributeError as e:
        print(f"Error parsing main page: {e}")
        return []

    articles = []

    try:
        title_prefix = raws_prefix.select_one(
            "h2.p-summary.p-name a.url.summary"
        ).get_text()
        date_prefix = raws_prefix.select_one("p.meta-date").get_text().strip()
        date_pre = datetime.strptime(date_prefix, "%A  %d %B %Y").strftime("%Y-%m-%d")
        img_prefix = raws_prefix.select_one("img.card-img-top")["src"]
        news_prefix = raws_prefix.select_one("p.read-more a")["href"]
        full_prefix = urljoin("https://www.eventfinda.co.nz", news_prefix)
        articles.append(
            {
                "target_id": "eventfindaNews",
                "target_url": "https://www.eventfinda.co.nz/news",
                "title": title_prefix,
                "news_url": full_prefix,
                "imageUrl": img_prefix,
                "date": date_pre,
            }
        )
    except AttributeError as e:
        print(f"Error parsing prefix article: {e}")

    for item in raws:
        try:
            title_element = item.select_one("h2.p-summary.p-name a.url.summary")
            title = title_element.get_text()

            # Extract the date
            date_element = item.select_one("p.meta-date")
            date_text = date_element.get_text().strip()
            date = datetime.strptime(date_text, "%A  %d %B %Y").strftime("%Y-%m-%d")

            # Extract the image URL
            img_element = item.select_one("img.card-img-top")
            imgUrl = img_element["src"]

            # Extract the news URL
            news_url_element = item.select_one("p.read-more a")
            news_url = news_url_element["href"]
            full_url = urljoin("https://www.eventfinda.co.nz", news_url)

            articles.append(
                {
                    "target_id": "eventfindaNews",
                    "target_url": "https://www.eventfinda.co.nz/news",
                    "title": title,
                    "news_url": full_url,
                    "imageUrl": imgUrl,
                    "date": date,
                }
            )
        except AttributeError as e:
            print(f"Error parsing article: {e}")

    return articles


# Function to scrape the detail page for article content
def scrape_detail_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return ""

    soup = BeautifulSoup(response.content, "html.parser")

    try:
        article_content = soup.find("article").get_text(separator="\n").strip()
    except AttributeError as e:
        print(f"Error parsing detail page: {e}")
        return ""

    return article_content


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
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


async def get_news_from_eventfinda():
    main_page_url = "https://www.eventfinda.co.nz/news"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["content"] = scrape_detail_page(article["news_url"])
        await save_to_supabase(article)
    print("eventfindaNews")