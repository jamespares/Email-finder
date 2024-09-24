import requests
import json
import time
from dotenv import load_dotenv
import os
import logging
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
API_KEY = os.getenv('HUNTER_API_KEY')

# Define the API endpoint
API_ENDPOINT = 'https://api.hunter.io/v2/domain-search'

# Input and Output file paths
INPUT_FILE = 'domains.txt'
OUTPUT_FILE = 'emails_found.csv'
LOG_FILE = 'email_scraper.log'

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to read domains from the input file
def read_domains(file_path):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains

# Function to query Hunter.io API for a given domain with retry logic
def get_emails(domain, max_retries=3):
    params = {
        'domain': domain,
        'api_key': API_KEY,
        'limit': 100  # Maximum number of results per request
    }
    retry_count = 0
    backoff_time = 2  # Initial backoff time in seconds

    while retry_count < max_retries:
        try:
            response = requests.get(API_ENDPOINT, params=params, timeout=10)
            if response.status_code == 429:
                # Rate limit exceeded
                logging.warning(f"Rate limit exceeded for {domain}. Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                retry_count += 1
                backoff_time *= 2  # Exponential backoff
                continue
            response.raise_for_status()
            data = response.json()
            logging.info(f"Response data for {domain}: {json.dumps(data, indent=2)}")
            if data.get('data'):
                emails = [email['value'] for email in data['data'].get('emails', [])]
                return emails
            else:
                logging.info(f"No emails found in response data for {domain}")
                return []
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error for {domain}: {http_err}")
            break
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error for {domain}: {conn_err}")
            break
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error for {domain}: {timeout_err}")
            break
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request exception for {domain}: {req_err}")
            break
        except json.JSONDecodeError as json_err:
            logging.error(f"JSON decode error for {domain}: {json_err}")
            break
    logging.error(f"Failed to retrieve emails for {domain} after {max_retries} attempts.")
    return []

# Function to save emails to a CSV file using pandas
def save_emails(emails_dict, file_path):
    df = pd.DataFrame([
        {'Domain': domain, 'Emails': ', '.join(emails) if emails else 'No emails found'}
        for domain, emails in emails_dict.items()
    ])
    df.to_csv(file_path, index=False)
    logging.info(f"Saved emails to {file_path}")

# Main function
def main():
    domains = read_domains(INPUT_FILE)
    emails_found = {}

    for index, domain in enumerate(domains, start=1):
        logging.info(f"Processing {index}/{len(domains)}: {domain}")
        print(f"[{index}/{len(domains)}] Searching for emails in domain: {domain}")
        emails = get_emails(domain)
        emails_found[domain] = emails

        if emails:
            logging.info(f"Found {len(emails)} email(s) for {domain}")
            print(f"  Found {len(emails)} email(s)")
        else:
            logging.info(f"No emails found for {domain}")
            print("  No emails found")

        # Adjust delay based on rate limits
        time.sleep(1.2)  # Example delay

    save_emails(emails_found, OUTPUT_FILE)
    logging.info("Email scraping completed.")
    print(f"\nEmail scraping completed. Results saved to '{OUTPUT_FILE}'. Check '{LOG_FILE}' for logs.")

if __name__ == '__main__':
    main()