# Web Scraper Project

This is an automated web scraper that:
- Scrapes 30 URLs daily
- Extracts emails and phone numbers (max 4 per site)
- Focuses on specific domains (e.g., cloud services providers)
- Saves results to scrapper.csv

## Setup
1. Install Python 3.x
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the scraper:
```bash
python scraper.py
```

The scraper will:
- Run immediately upon starting
- Schedule daily runs at midnight
- Save results to scrapper.csv in the same directory

## Configuration
You can modify the search query in scraper.py to target different domains.
