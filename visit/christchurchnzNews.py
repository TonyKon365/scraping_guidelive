import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customizableNews, customizeNews


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    try:
        response = requests.get(f"{url}?page={page}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {url}: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        raws = soup.find_all("li", class_="c-news_list__item")
        articles = []

        for item in raws:
            try:
                title = item.find("h2", class_="c-card_news__title").text.strip()
                news_element = item.find("a", class_="c-card_news__img_link")
                news_url = news_element["href"] if news_element else None
                news_full_url = urljoin("https://www.christchurchnz.com/", news_url)

                synopsis_div = item.find("div", class_="c-card_news__synopsis")
                if synopsis_div is None:
                    print(f"Synopsis content not found in {news_url}")
                    continue
                synopsis_text = ''.join([str(content) for content in synopsis_div.contents if isinstance(content, str)]).strip()

                img_element = item.find("img", class_="c-card_news__img")
                img_url = img_element["src"] if img_element else None
                img_full_url = urljoin("https://www.christchurchnz.com/", img_url)

                date_element = item.find("time", class_="c-card_news__date")
                date = date_element.text.strip() if date_element else None
                date_obj = datetime.strptime(date, "%A, %d %B %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")

                articles.append(
                    {
                        "target_id": "christchurchnzNews",
                        "target_url": "https://www.christchurchnz.com/about-us/news",
                        "title": title,
                        'content': synopsis_text,
                        "news_url": news_full_url,
                        "imageUrl": img_full_url,
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
        article_content = soup.find("div", class_="t-rich_text  t-rich_text--editorial")
        if article_content is not None:
            article_div = article_content.find_all("p")
            paragraph_content = [p.get_text(separator=" ") for p in article_div]
            result = "\n\n".join(paragraph_content)
        else:
            result = "No content found"

        return result

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
            supabase.table("News").select("*").eq("title", title).eq("date", date).execute()
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


async def get_news_from_christchurchnz():
    main_page_url = "https://www.christchurchnz.com/about-us/news"
    page = 1
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break
        for article in articles:
            try:
                article['content'] = scrape_detail_page(article['news_url'])
                await save_to_supabase(article)
            except Exception as e:
                print(f"Error processing article {article['title']}: {e}")
        page += 1
    print('Finished fetching news from ChristchurchNZ.')