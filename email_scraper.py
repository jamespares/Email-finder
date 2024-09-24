import requests
from bs4 import BeautifulSoup
import re
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_emails_with_selenium(url):
    try:
        # Set up Selenium WebDriver
        options = Options()
        options.headless = True  # Run in headless mode
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        # Fetch the page
        driver.get(url)
        
        # Extract text from the main page
        text = driver.find_element(By.TAG_NAME, 'body').text
        
        # Look for "Contact Us" or similar links and navigate to them
        contact_links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Contact')
        contact_links += driver.find_elements(By.PARTIAL_LINK_TEXT, 'About')
        contact_links += driver.find_elements(By.PARTIAL_LINK_TEXT, 'Support')
        
        for link in contact_links:
            try:
                link.send_keys(Keys.CONTROL + Keys.RETURN)  # Open link in a new tab
                time.sleep(2)  # Wait for the page to load
                driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
                text += driver.find_element(By.TAG_NAME, 'body').text  # Append the text from the new page
                driver.close()  # Close the new tab
                driver.switch_to.window(driver.window_handles[0])  # Switch back to the main tab
            except Exception as e:
                print(f"An error occurred while accessing contact link: {e}")
        
        # Close the driver
        driver.quit()
        
        return text
    except Exception as e:
        print(f"An error occurred with Selenium while accessing {url}: {e}")
        return ""

def scrape_emails(url):
    try:
        # Send a GET request to the website
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for request errors

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from the soup
        text = soup.get_text()

        # Translate the text to English
        translator = Translator()
        translated_text = translator.translate(text, dest='en').text

        # Use regex to find email addresses
        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', translated_text)

        # If no emails found, try using Selenium
        if not emails:
            print(f"No emails found with BeautifulSoup for {url}, trying Selenium...")
            text = scrape_emails_with_selenium(url)
            if text:
                translated_text = translator.translate(text, dest='en').text
                emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', translated_text)

        # Remove duplicates by converting the list to a set
        emails = list(set(emails))

        return emails

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing {url}: {e}")
        return []
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return []

def main():
    # Read the list of websites from the file
    with open('websites.txt', 'r') as file:
        lines = file.readlines()

    # Process each line to extract agency name and website
    agencies = [line.strip().split(',') for line in lines]

    # Open files to save the emails and logs
    with open('emails.txt', 'w') as email_file, open('log.txt', 'w') as log_file:
        # Scrape emails for each agency
        for country, agency, website in agencies:
            log_file.write(f"Scraping emails for {agency} ({country}) at {website}\n")
            print(f"Scraping emails for {agency} ({country}) at {website}")
            emails = scrape_emails(website)
            if emails:
                log_file.write(f"Found emails for {agency} ({country}): {emails}\n")
                print(f"Found emails for {agency} ({country}): {emails}")
                email_file.write(f"{agency} ({country}): {', '.join(emails)}\n")
            else:
                log_file.write(f"No emails found for {agency} ({country})\n")
                print(f"No emails found for {agency} ({country})")
                email_file.write(f"{agency} ({country}): No emails found\n")

if __name__ == "__main__":
    main()

