import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import json

# Set up logging
logging.basicConfig(level=logging.INFO, filename="/home/ubuntu/scraping_guidelive/test_scraper.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Supabase client setup
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

from visit.livenationEvent import get_event_from_livenationNZ
from visit.livenation import get_events_from_livenation
from visit.frontiertouring import get_events_from_frontiertouring
from visit.ecclesEvent import get_event_from_eccles
from visit.forummelbourneEvent import get_event_from_forummelbourne
from visit.bohmpresentsEvent import get_event_from_bohmpresents
from visit.venuesotautahi import get_events_from_venuesotautahi

async def scrape_events():
    await get_event_from_livenationNZ()
    await get_events_from_livenation()
    await get_events_from_frontiertouring()     
    await get_event_from_forummelbourne()
    await get_events_from_venuesotautahi()


if __name__ == "__main__":
    print("Starting script...")
    try:
        asyncio.run(scrape_events())  # This will run scrape_events and exit
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        print("Script completed.")
