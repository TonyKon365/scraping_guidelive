import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
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
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        for item in soup.select('.items .item'):
            try:
                title_element = item.select_one('h3.item-title.h3')
                if title_element:
                    title = title_element.get_text(strip=True)
                    news_url = item.select_one('.item-title-wrap')['href']
                    date_text = item.select_one('time[itemprop="datePublished"]')
                    if date_text:
                        date_span = date_text.find('span', {'class': 'date'})
                        if date_span:
                            date = date_span.text
                            parsed_date = datetime.strptime(date, "%d %b %Y")
                            output_date = parsed_date.strftime("%Y-%m-%d")

                            content = " ".join([p.get_text(strip=True) for p in item.select('.item-text p')])

                            articles.append({
                                'target_id': 'totarastreetNews',
                                'target_url': 'https://totarastreet.co.nz/news',
                                'title': title,
                                'news_url': news_url,
                                'content': content,
                                'date': output_date
                            })
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
        return None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_url = soup.select_one('.grid-image img')['src'] if soup.select_one('.grid-image img') else None
        return img_url
    except Exception as e:
        print(f"Error parsing detail page content: {e}")
        return None

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
            supabase.table("News").select("*").eq("target_id", target_id).eq("title", title).execute()
        )

        if not existing_article.data:
            try:
                temp_obj = await customizeNews(article)
                card = customizableNews(temp_obj)
                response = supabase.table('News').insert(card).execute()

            except Exception as e:
                print(f"Error customizing or inserting article: {e}")

    except Exception as e:
        print(f"Error checking for existing article: {e}")

async def get_news_from_totarastreet():
    main_page_url = "https://totarastreet.co.nz/news"
    try:
        articles = scrape_main_page(main_page_url)
        if not articles:
            print("No articles found.")
            return

        for article in articles:
            try:
                image_url = scrape_detail_page(article['news_url'])
                if image_url:
                    article['imageUrl'] = 'https://totarastreet.co.nz' + image_url
                await save_to_supabase(article)
            except Exception as e:
                print(f"Error processing article {article['title']}: {e}")
        print("totarastreetNews")
    except Exception as e:
        print(f"Error getting news from Totara Street: {e}")

