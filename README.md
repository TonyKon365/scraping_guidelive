Setup and Deployment Guide
#Setup Environment
Install Python virtual environment:

sudo apt install -y python3-venv
Create and activate the virtual environment:

python3 -m venv venv
source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
#Run the FastAPI Server
Activate the virtual environment:

source venv/bin/activate
Start the FastAPI server:

python main.py
#Architecture Overview
#FastAPI Server
Purpose: Handles API requests and serves event data.
Data Source: Fetches event data from Supabase.
Note: The server does not handle scraping directly.
#Scraping Task
Purpose: Runs as a standalone Python script to scrape event data.
Automation: Scheduled to run automatically once a week using a cron job.
#Database
Storage: Scraped event data is stored in Supabase.
Integration: The FastAPI server reads data from Supabase to provide it via APIs.
#Keep the FastAPI Server Always Running
#Step 1: Create a Systemd Service
Create a service file:

sudo nano /etc/systemd/system/fastapi.service
Add the following configuration:

[Unit]
Description=FastAPI Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/scraping_guidelive
ExecStart=/home/ubuntu/scraping_guidelive/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
#Step 2: Enable and Start the Service
Reload the systemd daemon:

sudo systemctl daemon-reload
Enable the FastAPI service:

sudo systemctl enable fastapi.service
Start the FastAPI service:

sudo systemctl start fastapi.service
Check the status of the service:

sudo systemctl status fastapi.service
#Automating Scraping with Cron
#Step 1: Develop a Python Script
Navigate to the project directory:

cd /home/ubuntu/scraping_guidelive
Create the test_scraper.py file:

nano test_scraper.py
Add the following code:

from datetime import datetime

def test_scraping():
    print(f"Scraping task running at {datetime.now()}")
    with open("test_scraper.log", "a") as log_file:
        log_file.write(f"Scraping task ran at {datetime.now()}\n")

if __name__ == "__main__":
    test_scraping()
What it does: Appends a log entry to test_scraper.log whenever the script runs.

#Step 2: Create a Bash Script
Create the run_test_scraper.sh file:

nano run_test_scraper.sh
Add the following code:

#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/scraping_guidelive

# Activate the Python virtual environment
source venv/bin/activate

# Run the test scraper script
python test_scraper.py
Make the script executable:

chmod +x run_test_scraper.sh
What it does: Runs the Python scraper script in the project directory.

#Step 3: Test with Cron (Run Every Minute)
Open the crontab editor:

crontab -e
Add the following line to schedule the script to run every minute:

* * * * * /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/cron_test.log 2>&1
Explanation:

* * * * *: Runs the job every minute.
/home/ubuntu/scraping_guidelive/run_test_scraper.sh: Executes the Bash script.
>> /home/ubuntu/scraping_guidelive/cron_test.log 2>&1: Logs output and errors to cron_test.log.
Save and exit the editor.

Confirm the cron job is active:

crontab -l
Check the logs:

cat /home/ubuntu/scraping_guidelive/test_scraper.log
#Step 4: Schedule Weekly Execution
Open the crontab editor again:

crontab -e
Replace the cron job with the following line to schedule it for 1:00 AM every Monday:

0 1 * * 1 /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/scraper.log 2>&1
Explanation:

0 1 * * 1: Runs the script at 1:00 AM every Monday.
/home/ubuntu/scraping_guidelive/run_test_scraper.sh: Executes the Bash script.
>> /home/ubuntu/scraping_guidelive/scraper.log 2>&1: Logs output and errors to scraper.log.
Save and exit the editor.

Manually test the script:

/home/ubuntu/scraping_guidelive/run_test_scraper.sh
Check the logs:

cat /home/ubuntu/scraping_guidelive/scraper.log
#Step 5: Replace Test Script with Actual Scraper
Replace test_scraper.py with your actual scraping script (e.g., scraper.py).

Update the run_test_scraper.sh file to use the actual script:

#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/scraping_guidelive

# Activate the Python virtual environment
source venv/bin/activate

# Run the actual scraper script
python scraper.py
Save the changes and confirm it works.

#FastAPI Server Logs
To monitor the FastAPI server logs:

cat server_logs.txt
#Summary
#Summary
Set up the environment with Python and dependencies.
Run the FastAPI server for handling API requests.
Automate the scraping process with a cron job.
Use systemd to ensure the server runs continuously.
Monitor logs for debugging and verification.