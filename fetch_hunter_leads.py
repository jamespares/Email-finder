import requests
import os
from dotenv import load_dotenv
import logging
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
API_KEY = os.getenv('HUNTER_API_KEY')

# Define the API endpoint
LEAD_LIST_URL = f"https://api.hunter.io/v2/leads?api_key={API_KEY}"

# Output file path
OUTPUT_FILE = 'hunter_leads.csv'
LOG_FILE = 'fetch_hunter_leads.log'

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def fetch_leads():
    try:
        response = requests.get(LEAD_LIST_URL)
        response.raise_for_status()
        leads = response.json().get('data', {}).get('leads', [])
        return leads
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request exception: {req_err}")
    return []

def save_leads_to_csv(leads, file_path):
    df = pd.DataFrame(leads)
    df.to_csv(file_path, index=False)
    logging.info(f"Saved leads to {file_path}")

def main():
    logging.info("Fetching leads from Hunter.io")
    leads = fetch_leads()
    if leads:
        logging.info(f"Fetched {len(leads)} leads")
        save_leads_to_csv(leads, OUTPUT_FILE)
        print(f"Leads fetched and saved to '{OUTPUT_FILE}'. Check '{LOG_FILE}' for logs.")
    else:
        logging.info("No leads found or failed to fetch leads")
        print("No leads found or failed to fetch leads. Check the log file for details.")

if __name__ == '__main__':
    main()