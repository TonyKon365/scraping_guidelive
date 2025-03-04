sudo chown -R ubuntu:ubuntu /home/ubuntu/scraping

python3 -m venv venv



source venv/bin/activate



pip install fastapi uvicorn

python main.py