import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    

    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.select("div.blog4_item.w-dyn-item")
    articles = []

    for item in raws:
        a_tag = item.find("a", class_="blog4_item-link w-inline-block")

        # Extract the news_url from the href attribute
        news_url = a_tag["href"]
        full_url = urljoin("https://www.flicket.io", news_url)

        # Locate the <img> tag within the <a> element and extract the image URL from the src attribute
        img_tag = a_tag.find("img", class_="blog4_image")
        image_url = img_tag["src"]

        # Locate the <h3> tag within the <a> element and extract the text
        title_tag = a_tag.find("h3", class_="text-size-large")
        title = title_tag.get_text()
        content = scrape_detail_page(news_url)
        articles.append(
            {
                "target_id": "flicketNews",
                "target_url": "https://www.flicket.io/news",
                "title": title,
                "content":content,
                "news_url": full_url,
                "imageUrl": image_url,
                "date": "",
            }
        )
    return articles

def find_article_content(soup, class_names):
    for class_name in class_names:
        article_content = soup.find("div", class_=class_name)
        if article_content:
            return article_content
    return None
def extract_paragraphs(article_content):
    paragraphs = article_content.find_all("p")
    paragraph_content = [p.get_text(separator=" ") for p in paragraphs]
    return "\n\n".join(paragraph_content)
# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    try:
        response = requests.get(news_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {news_url}: {e}")
        return ""
    
    soup = BeautifulSoup(response.content, "html.parser")
    class_names = [
        "edgtf-post-text-inner clearfix",
        "offset-md-1 offset-xl-2 col-md-10 col-xl-8",
        "entry-content",
        "news-details-description"
    ]

    article_content = find_article_content(soup, class_names)
    if article_content:
        return extract_paragraphs(article_content)
    else:
        return "No article content found."


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["title"]
    date = article["date"]
    existing_article = (
        supabase.table("News").select("*").eq("title", title).eq("date", date).execute()
    )

    if not existing_article.data:
        response = supabase.table("News").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")


def get_news_from_flicket():
    main_page_url = "https://www.flicket.io/news"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        
        save_to_supabase(article)
