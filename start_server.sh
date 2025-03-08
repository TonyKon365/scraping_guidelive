#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/scraping_guidelive

# Activate the virtual environment (if you use one)
source venv/bin/activate

# Start the FastAPI server with Uvicorn using PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8002" --name fastapi-server --interpreter python3