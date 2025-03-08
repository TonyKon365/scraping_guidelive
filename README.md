#######################setup environment######################

sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install selenium

######################run the server######################

source venv/bin/activate
python main.py


######################Architecture Overview######################
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


######################Step 4: Keep the FastAPI Server Always Running######################

1.Create a systemd service file:

  sudo nano /etc/systemd/system/fastapi.service
2.Add the following configuration:

  [Unit]
  Description=FastAPI Server
  After=network.target

  [Service]
  User=ubuntu
  WorkingDirectory=/path/to/project
  ExecStart=/path/to/project/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8002
  Restart=always

  [Install]
  WantedBy=multi-user.target

3.Reload the systemd daemon:

  sudo systemctl daemon-reload

4.Enable and start the FastAPI service:

  sudo systemctl enable fastapi.service
  sudo systemctl start fastapi.service

5.Check the status of the server:

  sudo systemctl status fastapi.service



###################### set cron workikng ######################

Step 1: develop Python Script
The Python script (test_scraper.py) simulates the scraping process and will log timestamps every time it runs.

Navigate to the scraping_guidelive folder:

cd /home/ubuntu/scraping_guidelive
Create the test_scraper.py file:

nano test_scraper.py
Add the following code:

from datetime import datetime

# A simple test script to simulate scraping
def test_scraping():
    print(f"Scraping task running at {datetime.now()}")

    # Simulate scraping by writing to a log file
    with open("test_scraper.log", "a") as log_file:
        log_file.write(f"Scraping task ran at {datetime.now()}\n")

if __name__ == "__main__":
    test_scraping()
    

What this does: Each time the script is run, it appends a log entry to test_scraper.log in the same folder.

#Step 2: Bash Script
The bash script (run_test_scraper.sh) is used to run the Python script, and it will ensure the scraping process runs correctly.

Create the run_test_scraper.sh file:

nano run_test_scraper.sh
Add the following code:

#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/scraping_guidelive

# Activate the Python virtual environment (if you use one)
source venv/bin/activate

# Run the test scraper script
python test_scraper.py

Make the script executable:

chmod +x run_test_scraper.sh
What this does: The bash script navigates to the project folder, activates the virtual environment (if applicable), and runs the Python scraper script.

#Step 3: Testing with Cron (Every Minute)
To verify that the script works, schedule it to run every minute.

Open the crontab editor:

crontab -e
Add the following line to schedule the test script to run every minute:

* * * * * /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/cron_test.log 2>&1
Explanation:

* * * * *: Run the job every minute.
/home/ubuntu/scraping_guidelive/run_test_scraper.sh: Executes the bash script.
>> /home/ubuntu/scraping_guidelive/cron_test.log 2>&1: Logs output and errors to cron_test.log.
Save and exit the crontab editor.

#Step 4: Verify the Cron Job
To confirm the cron job is active, list all cron jobs:

crontab -l
You should see the line:

* * * * * /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/cron_test.log 2>&1
Wait a minute or two, then check the logs:

Test script log (test_scraper.log):

cat /home/ubuntu/scraping_guidelive/test_scraper.log
Example output:

Scraping task ran at 2025-03-07 01:00:00
Scraping task ran at 2025-03-07 01:01:00
Scraping task ran at 2025-03-07 01:02:00
Cron job log (cron_test.log):

cat /home/ubuntu/scraping_guidelive/cron_test.log
This should be empty unless there are errors.

If everything works, the script is running every minute as expected.

#Step 5: Schedule for Weekly Execution
Once you’ve verified that the cron job works, modify the schedule to run weekly on Monday at 1:00 AM NZT.

Open the crontab editor again:

crontab -e
Replace the cron job (* * * * * ...) with the following:

0 1 * * 1 /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/scraper.log 2>&1
Explanation:

0 1 * * 1: Run at 1:00 AM every Monday.
/home/ubuntu/scraping_guidelive/run_test_scraper.sh: Executes the bash script.
>> /home/ubuntu/scraping_guidelive/scraper.log 2>&1: Logs output and errors to scraper.log.
Save and exit the editor.

#Step 6: Verify Weekly Schedule
To confirm the weekly cron job is active:

crontab -l
You should see the updated line:

0 1 * * 1 /home/ubuntu/scraping_guidelive/run_test_scraper.sh >> /home/ubuntu/scraping_guidelive/scraper.log 2>&1
You can manually run the script to check if it works:

/home/ubuntu/scraping_guidelive/run_test_scraper.sh
Then check the output logs:

cat /home/ubuntu/scraping_guidelive/test_scraper.log
cat /home/ubuntu/scraping_guidelive/scraper.log
#Step 7: Replace Test Script with Actual Scraper
Once you confirm the cron job works, replace the test_scraper.py with your actual scraping script (e.g., scraper.py).

Edit the bash script run_test_scraper.sh to run the real scraper:

#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/scraping_guidelive

# Activate the Python virtual environment (if you use one)
source venv/bin/activate

# Run the actual scraper script
python scraper.py
Save the changes and ensure it works as expected.



#############################FastAPI server#################
Open the server_logs.txt file to see the logs:
cat server_logs.txt
