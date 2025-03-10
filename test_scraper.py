from datetime import datetime

# A simple test script to simulate scraping
def test_scraping():
    print(f"Scraping task running at {datetime.now()}")

    # Simulate scraping by writing to a log file
    with open("/home/ubuntu/scraping_guidelive/test_scraper.log", "a") as log_file:
        log_file.write(f"Scraping task ran at {datetime.now()}\n")

if __name__ == "__main__":
    test_scraping()