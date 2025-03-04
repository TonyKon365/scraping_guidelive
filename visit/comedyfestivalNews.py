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
        response = requests.get(f"{url}?start={page}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page {url}: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        raws = soup.find_all("div", class_="grid-article-tile-container")
        articles = []

        for item in raws:
            try:
                article = item.find("a", class_="grid-article-tile")
                if not article:
                    continue
                
                # Extract the required information
                news_url = article["href"]
                news_full_url = urljoin("https://www.comedyfestival.co.nz", news_url)
                title = article.find("span", class_="title").get_text(strip=True)
                date = article.find("span", class_="subtitle").get_text(strip=True)

                image_style = article.find("span", class_="image")['style']
                image_url_match = re.search(r"url\('(.+?)'\)", image_style)
                if image_url_match:
                    image_url = "https://www.comedyfestival.co.nz" + image_url_match.group(1)
                else:
                    image_url = ""
                
                date_match = re.search(r'\d{1,2} \b\w{3}\b \d{4}', date)

                if date_match:
                    # Extracted date part
                    extracted_date = date_match.group()

                    # Parse the extracted date part
                    try:
                        date_obj = datetime.strptime(extracted_date, "%d %b %Y")
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except ValueError as e:
                        print(f"Error parsing date: {e}")
                        formatted_date = ""

                    articles.append(
                        {
                            "target_id": "comedyfestivalNews",
                            "target_url": "https://www.comedyfestival.co.nz/news-feed/",
                            "title": title,
                            "news_url": news_full_url,
                            "imageUrl": image_url,
                            "date": formatted_date,
                        }
                    )
                else:
                    print(f"Date format not recognized in: {date}")

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
        news_section = soup.find("section", class_="news-page")
        
        if news_section:
            content = news_section.get_text(strip=True)
            text = content.replace("Back to news", "")
            return text
        else:
            return "No content found"
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
 
    except Exception as e:
        print(f"Error checking for existing article: {e}")

async def get_news_from_comedyfestival():
    main_page_url = "https://www.comedyfestival.co.nz/news-feed/filter"
    page = 0
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

            page += 9
        except Exception as e:
            print(f"Error fetching articles from page {page}: {e}")
            break
    print('comedyfestivalNews')
