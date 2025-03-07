#setup environment
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install selenium

#run the server
source venv/bin/activate
python main.py



Architecture Overview
FastAPI Server:

The server will always run and handle API requests.
The server serves event data from the supabase.
The server does not handle scraping directly.

Scraping Task:

A standalone Python script or function that performs the scraping task.
This script runs automatically once a week using a cron job.

Database:
The scraped event data is stored in a supabase.
The FastAPI server reads from the supabase to provide data via APIs.
