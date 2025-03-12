from fastapi import FastAPI
import os
from dotenv import load_dotenv
from supabase import create_client, Client  # type: ignore
from datetime import datetime
import json
import logging
import uvicorn

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Configure logging
logging.basicConfig(
    filename="server_logs.txt",  # Log file name
    level=logging.INFO,          # Log level (INFO, DEBUG, ERROR, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

# Initialize FastAPI app
app = FastAPI()


# HTTP Request - Retrieve Events
@app.get("/events/{target_id}")
def retrieve_event(target_id: str, offset: int, limit: int):
    logging.info(f"Fetching events for target_id: {target_id}, offset: {offset}, limit: {limit}")
    response = (
        supabase.from_("Event3")
        .select(
            "event_title, event_category, event_description, event_location, event_imgurl, start_date, start_time, end_date, end_time, add_to_cart_url"
        )
        .eq("target_id", target_id)
        .offset(offset)
        .limit(limit)
        .execute()
    )
    logging.info(f"Response from Supabase: {response}")
    return response


# HTTP Request - Retrieve News
@app.get("/news/{target_id}")
def retrieve_news(target_id: str, offset: int, limit: int):
    logging.info(f"Fetching news for target_id: {target_id}, offset: {offset}, limit: {limit}")
    response = (
        supabase.from_("News")
        .select("title, imageUrl, content, date, news_url")
        .eq("target_id", target_id)
        .offset(offset)
        .limit(limit)
        .execute()
    )
    logging.info(f"Response from Supabase: {response}")
    return response


    # Parse the event_location as JSON
    if response.data:
        for event in response.data:
            if "event_location" in event and event["event_location"]:
                event["event_location"] = json.loads(event["event_location"])

    logging.info(f"Response from Supabase: {response}")
    return response


if __name__ == "__main__":
    logging.info("Starting FastAPI server at port 8002")
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)