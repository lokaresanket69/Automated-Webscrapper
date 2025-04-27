from scraper import WebScraper
from datetime import datetime
import logging
import os

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'scraper.log')

# Set up logging
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Starting scheduled scraper run")
        scraper = WebScraper()
        scraper.main()
        logging.info("Scraper run completed successfully")
    except Exception as e:
        logging.error(f"Error during scraper run: {str(e)}")

if __name__ == "__main__":
    main()
