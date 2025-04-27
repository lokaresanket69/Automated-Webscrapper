import re
import csv
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

class WebScraper:
    def __init__(self):
        self.csv_file = 'scrapper1.csv'
        self.urls_per_day = 30
        self.max_contacts_per_site = 3
        
    def extract_emails(self, text):
        """Extract email addresses from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return list(set(emails))[:self.max_contacts_per_site]
    
    def extract_phones(self, text):
        """Extract phone numbers from text"""
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return list(set(phones))[:self.max_contacts_per_site]
    
    def get_domain_urls(self, query, num_results=30):
        """Get URLs based on the domain/industry"""
        # Dictionary of industry-specific domains
        industry_domains = {
            'cloud': [
                'https://aws.amazon.com',
                'https://cloud.google.com',
                'https://azure.microsoft.com',
                'https://www.digitalocean.com',
                'https://www.heroku.com',
                'https://www.salesforce.com',
                'https://www.oracle.com/cloud',
                'https://www.ibm.com/cloud',
                'https://www.rackspace.com',
                'https://www.vultr.com',
                'https://www.linode.com',
                'https://www.cloudflare.com',
                'https://www.ovhcloud.com',
                'https://www.hetzner.com',
                'https://www.digitalocean.com',
                'https://www.netlify.com',
                'https://www.vercel.com',
                'https://www.heroku.com',
                'https://www.redhat.com/en/technologies/cloud-computing/openshift',
                'https://cloud.vmware.com',
                'https://www.alibabacloud.com',
                'https://www.tencent.com/en-us/cloud.html',
                'https://www.huaweicloud.com',
                'https://www.scaleway.com',
                'https://www.backblaze.com',
                'https://www.upcloud.com',
                'https://www.kamatera.com',
                'https://www.atlantic.net',
                'https://www.cloudsigma.com',
                'https://www.phoenixnap.com'
            ],
            # Add more industries here as needed
        }
        
        # Clean and lowercase the query
        query_lower = query.lower()
        
        # Find matching industry
        urls = []
        for industry, domains in industry_domains.items():
            if industry in query_lower or any(keyword in query_lower for keyword in [industry, f'{industry} services', f'{industry} providers']):
                urls = domains
                break
        
        # If no specific industry found, use cloud services as default
        if not urls:
            print(f"No specific domains found for '{query}', using cloud services domains...")
            urls = industry_domains['cloud']
        
        print(f"Found {len(urls)} URLs to scrape")
        return urls[:num_results]
    
    def scrape_website(self, url):
        """Scrape a single website for contact information with retries"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Rotate between different user agents
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
                ]
                headers = {
                    'User-Agent': user_agents[attempt % len(user_agents)],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Connection': 'keep-alive',
                }
                
                # Add session handling and longer timeout
                session = requests.Session()
                response = session.get(url, headers=headers, timeout=30, allow_redirects=True, verify=False)
                session.close()
                if response.status_code != 200:
                    print(f"Error status {response.status_code} for {url}")
                    time.sleep(retry_delay)
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # First try to get contact information from contact/about pages
                contact_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.text.lower()
                    if any(word in text for word in ['contact', 'about', 'support']):
                        if href.startswith('/'):
                            href = url.rstrip('/') + '/' + href.lstrip('/')
                        elif not href.startswith('http'):
                            href = url.rstrip('/') + '/' + href
                        contact_links.append(href)
                
                # Combine text from main page and contact pages
                all_text = [soup.get_text()]
                for contact_url in contact_links[:2]:  # Only try first 2 contact pages
                    try:
                        contact_response = requests.get(contact_url, headers=headers, timeout=10)
                        if contact_response.status_code == 200:
                            contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                            all_text.append(contact_soup.get_text())
                    except:
                        continue
                
                text_content = ' '.join(all_text)
                
                # Extract contact information
                emails = self.extract_emails(text_content)
                phones = self.extract_phones(text_content)
                
                # Try multiple methods to get company name
                company_name = ''
                if soup.title:
                    company_name = soup.title.string
                if not company_name:
                    meta_name = soup.find('meta', property='og:site_name')
                    if meta_name:
                        company_name = meta_name.get('content', '')
                if not company_name:
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        company_name = meta_desc.get('content', '')
                
                # Clean up company name
                company_name = company_name.strip() if company_name else ''
                if not company_name or len(company_name) > 100:
                    company_name = url.split('/')[2].replace('www.', '')  # Use domain as fallback
                
                return {
                    'company_name': company_name,
                    'url': url,
                    'emails': emails[:3],  # Limit to 3 emails
                    'phones': phones[:3],  # Limit to 3 phone numbers
                    'date_scraped': datetime.now().strftime('%Y-%m-%d')
                }
                
            except Exception as e:
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    print(f"Attempt {attempt + 1} failed for {url}: {str(e)}. Retrying...")
                    time.sleep(retry_delay)
                else:
                    print(f"All attempts failed for {url}: {str(e)}")
                    return None
    
    def clean_text(self, text):
        """Clean text by removing extra whitespace and newlines"""
        if not text:
            return ''
        # Replace newlines and multiple spaces with a single space
        text = ' '.join(text.split())
        # Remove any non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text.strip()
    
    def save_to_csv(self, data):
        """Save scraped data to CSV file with proper cleaning"""
        try:
            # Start fresh with a new file
            fieldnames = ['company_name', 'url', 'emails', 'phones', 'date_scraped']
            
            # Clean and prepare the data
            cleaned_data = []
            for item in data:
                if item:  # Only process non-None items
                    cleaned_item = {
                        'company_name': self.clean_text(item['company_name']),
                        'url': item['url'],
                        'emails': ', '.join(item['emails']),
                        'phones': ', '.join(item['phones']),
                        'date_scraped': item['date_scraped']
                    }
                    cleaned_data.append(cleaned_item)
            
            # Write to CSV file
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cleaned_data)
            
            print(f"\nSuccessfully saved {len(cleaned_data)} results to {self.csv_file}")
            
            # Print a summary of the results
            print("\nSummary of results:")
            print(f"Total companies processed: {len(cleaned_data)}")
            companies_with_emails = sum(1 for item in cleaned_data if item['emails'])
            companies_with_phones = sum(1 for item in cleaned_data if item['phones'])
            print(f"Companies with email addresses: {companies_with_emails}")
            print(f"Companies with phone numbers: {companies_with_phones}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def daily_scrape(self, search_query):
        print(f"Starting daily scrape for: {search_query}")
        
        # Get URLs for the domain
        urls = self.get_domain_urls(search_query, self.urls_per_day)
        
        # Scrape each URL
        results = []
        for url in urls:
            result = self.scrape_website(url)
            if result:
                results.append(result)
            time.sleep(2)  # Be nice to servers
        
        # Save results
        if results:
            self.save_to_csv(results)
        
        print(f"Completed daily scrape. Processed {len(results)} URLs")

def main():
    scraper = WebScraper()
    
    search_query = "cloud services providers"
    scraper.daily_scrape(search_query)
    
    print("\nScraping completed! Results saved to scrapper1.csv")
    print("To run again, simply execute this script with a different search query.")

if __name__ == "__main__":
    main()
