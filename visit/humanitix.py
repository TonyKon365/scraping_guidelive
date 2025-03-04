
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
from Utils.open_ai import customize, customizable

async def get_events_from_humanitix():

    # await get_events_from_humanitix_businessAndProfessional()
    # await get_events_from_humanitix_communityAndCulture()
    # await get_events_from_humanitix_charityAndCauses()
    # await get_events_from_humanitix_familyAndEducation()
    # await get_events_from_humanitix_fashionAndBeauty()
    # await get_events_from_humanitix_filmMediaAndEntertainment()
    # await get_events_from_humanitix_foodAndDrink()
    # await get_events_from_humanitix_healthAndWellness()
    # await get_events_from_humanitix_governmentAndPolitics()
    # await get_events_from_humanitix_homeAndLifestyle()     
    # await get_events_from_humanitix_music()
    # await get_events_from_humanitix_performingAndVisualArts()
    # await get_events_from_humanitix_religionAndSpirituality()
    # await get_events_from_humanitix_schoolActivities()
    # await get_events_from_humanitix_scienceAndTechnology()
    # await get_events_from_humanitix_seasonalAndHoliday()
    # await get_events_from_humanitix_sportsAndFitness()
    await get_events_from_humanitix_travelAndOutdoor()
    await get_events_from_humanitix_autoBoatAndAir()

async def get_events_from_humanitix_autoBoatAndAir():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=autoBoatAndAir&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")

            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['autoBoatAndAir'],
                            "event_imgurl": event_imgurl,
         
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_businessAndProfessional():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=businessAndProfessional&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
         
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['business'],
                            "event_imgurl": event_imgurl,
                 
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_communityAndCulture():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=communityAndCulture&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
          
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['culture'],
                            "event_imgurl": event_imgurl,
                       
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_charityAndCauses():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=charityAndCauses&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
        
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['charity'],
                            "event_imgurl": event_imgurl,
                   
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_familyAndEducation():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=familyAndEducation&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
          
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['family'],
                            "event_imgurl": event_imgurl,
                    
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_fashionAndBeauty():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=fashionAndBeauty&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
 
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['fashion'],
                            "event_imgurl": event_imgurl,
                          
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_filmMediaAndEntertainment():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=filmMediaAndEntertainment&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
          
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['film'],
                            "event_imgurl": event_imgurl,
                    
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")

async def get_events_from_humanitix_foodAndDrink():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=foodAndDrink&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
         
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['food','drink'],
                            "event_imgurl": event_imgurl,
                 
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_healthAndWellness():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=healthAndWellness&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
      
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['health','wellness'],
                            "event_imgurl": event_imgurl,
                      
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_hobbiesAndSpecialInterest():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=hobbiesAndSpecialInterest&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
       
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['special'],
                            "event_imgurl": event_imgurl,
                      
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_governmentAndPolitics():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=governmentAndPolitics&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
      
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['government','Politics'],
                            "event_imgurl": event_imgurl,
            
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_homeAndLifestyle():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=homeAndLifestyle&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
       
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Lifestyle'],
                            "event_imgurl": event_imgurl,
                     
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_music():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=music&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
   
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['music'],
                            "event_imgurl": event_imgurl,
              
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_performingAndVisualArts():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=performingAndVisualArts&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
          
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Performing','VisualArts'],
                            "event_imgurl": event_imgurl,
                     
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_religionAndSpirituality():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=religionAndSpirituality&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
         
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Religion','Spirituality'],
                            "event_imgurl": event_imgurl,
                    
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_schoolActivities():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=schoolActivities&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
            
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['school'],
                            "event_imgurl": event_imgurl,
                         
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_scienceAndTechnology():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=scienceAndTechnology&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
            
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Science','Technology'],
                            "event_imgurl": event_imgurl,
                        
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_seasonalAndHoliday():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=seasonalAndHoliday&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")

            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Seasonal','Holiday'],
                            "event_imgurl": event_imgurl,
                          
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_sportsAndFitness():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=sportsAndFitness&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
      
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Sports','Fitness'],
                            "event_imgurl": event_imgurl,
                          
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                            'add_to_cart_url': event_url,
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")
async def get_events_from_humanitix_travelAndOutdoor():
    page=0
    while True:
        main_page_url = f"https://humanitix.com/au/search?categories=travelAndOutdoor&page={page}"
        try:          
            response = requests.get(main_page_url)
           
            soup = BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            raws = soup.find_all("a", class_="sc-eb5cf798-0 hMcWrb")
      
            if raws==None:
                break 
            for item in raws:
                try:
                    # Extract the event title
                    event_title = item.find('h6').text
                    
                    start_date = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-3 swyla bpXsMF').text
                    location = item.find('p', class_='sc-8821f522-0 sc-eb5cf798-5 swyla hwxiUz').text
                    # Extract the event link and join with the base URL
                    event_url = item['href']
                    event_description = scrape_detail_page(event_url)
                    
                    event_imgurl_div = item.find_all('img')
                    event_imgurl = "https://humanitix.com" + event_imgurl_div[1]['src'] if len(event_imgurl_div) > 1 else ""

                    article={
                            "target_id": "humanitix",
                            "target_url": "https://humanitix.com",
                            "event_title": event_title,
                            "event_category": ['Travel','Outdoor'],
                            "event_imgurl": event_imgurl,
                            "start_date": start_date,
                            "end_date": "",
                            "start_time": '',
                            "end_time": "",
                 
                            "event_description": event_description,
                            "event_location": {
                                "title": location,
                                "street": "",
                                "region": "",
                                "country": "New Zealand"
                            }
                    }
                    await save_to_supabase(article)
                except Exception as e:
                    print(f"Error processing an event: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing main page: {e}")
            return []
        page += 1
    print("get_events_from_humanitix")

def scrape_detail_page(event_url):
    try:
        response = requests.get(event_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        rich_content_div = soup.find('div', class_='RichContent f-body-3 svelte-5lieqp')
        paragraphs = rich_content_div.find_all('p') if rich_content_div else []
        description = ' '.join(p.text.strip() for p in paragraphs if p.text.strip())
    except requests.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return ""
    except Exception as e:
        print(f"Error parsing detail page: {e}")
        return ""

    return description


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
async def save_to_supabase(article):
    try:
        # date=article['start_date']
        # if '2025' in date:
        #     date=date
        # else:
        #     date=date+' '+'2024'
        # temp_obj = await customize(article)
        # card = customizable(temp_obj)
        # title = card["event_title"]
        # start_date = card["start_date"]

        # existing_article = (
        #     supabase.table("Event1").select("*").eq("event_title", title).eq("start_date", start_date).execute()
        # )

        # if not existing_article.data:
            response = supabase.table("guideEvent").insert(article).execute()
    
    except Exception as e:
        print(f"Error saving to Supabase: {e}")


