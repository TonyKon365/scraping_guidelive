import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(f"{url}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("a", class_="show-item")
    articles = []

    for item in raws:
        event_url = item['href']
        # Locate the <img> tag within the <a> tag
        event_title=item.find('span',class_='title').text


        div_element = soup.find('div', class_='image')
        style_attr = div_element['style']
        url_match = re.search(r"url\('([^']+)'\)", style_attr)
        if url_match:
            event_imgurl = url_match.group(1)
        else:
            print("URL not found")
        event_description,start_date,start_time,=scrape_detail_page(event_url)
        articles.append(
            {
                "target_id": "  ",
                "target_url": "https://forummelbourne.com.au/",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": '',
                "event_category": ['show'],
                "event_description": event_description,
                "start_time": start_time,
                "add_to_cart_url":event_url,
                "end_time": "",
                "event_location": {
                    "title" : "154 Flinders St Melbourne VIC 3000",
                    "street" : "154 Flinders St",
                    "region" : "Melbourne VIC 3000",
                    "country" : "Australia"
	            },
            }
        )

    return articles

def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")
    calendar_div=soup.find('div',class_='content')
    start_date_div=calendar_div.find('span',class_='full-date')
    start_date=''
    start_time=''
    if start_date_div:
       start_date=start_date_div.text
    else:
        print("not there date",news_url)
    time_div=calendar_div.find('span',class_='time')
    if time_div:
        start_time=time_div.text
    else:
        print("not there time",news_url)
    div_element = soup.find('div', class_='column left')
    article_content = div_element.get_text(separator=' ', strip=True)
    return article_content,start_date,start_time
# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    temp_obj = await customize(article)
    card = customizable(temp_obj)
    title = card["event_title"]
    start_date = card["start_date"]

    existing_article = (
        supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
        )
    if not existing_article.data:
        response = supabase.table("Event1").insert(card).execute()




async def get_event_from_forummelbourne():
    main_page_url = "https://forummelbourne.com.au/shows?"
    articles = scrape_main_page(main_page_url)
    for article in articles:
        await save_to_supabase(article)
    print('get_event_from_forummelbourne')

