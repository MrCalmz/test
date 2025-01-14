# Install necessary packages
# pip install streamlit selenium beautifulsoup4

import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from threading import Thread

# Global variables for WebDriver and processed messages
BASE_URL = "https://10minutemail.net/"
driver = None
processed_messages = set()

def initialize_driver():
    """Initialize the Selenium WebDriver."""
    global driver
    if driver is None:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def fetch_email():
    """Fetch the temporary email address."""
    driver.get(BASE_URL)
    email_element = driver.find_element(By.ID, "fe_text")
    email = email_element.get_attribute("value")
    return email

def fetch_inbox():
    """Fetch the inbox content."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    mailbox_table = soup.find("table", {"id": "maillist"})
    
    if mailbox_table:
        rows = mailbox_table.find_all("tr")[1:]  # Skip the header row
        messages = []
        for row in rows:
            cols = row.find_all("td")
            link = row.find("a")["href"]
            message_id = link.split("=")[-1]
            message = {
                "id": message_id,
                "from": cols[0].text.strip(),
                "subject": cols[1].text.strip(),
                "date": cols[2].text.strip(),
                "link": link,
            }
            if message_id not in processed_messages:
                messages.append(message)
        return messages
    else:
        return []

def fetch_message_body(link):
    """Fetch the message body by navigating to its page and extract content after 'Comments:'."""
    message_url = BASE_URL + link
    driver.get(message_url)
    time.sleep(2)  # Allow the page to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    body = soup.find("div", {"id": "readmail"}).text.strip()
    
    if "Comments:" in body:
        body = body.split("Comments:")[-1].strip()
    return body

def refresh_inbox():
    """Refresh the inbox periodically."""
    inbox = fetch_inbox()
    if inbox:
        for msg in inbox:
            st.write(f"From: {msg['from']}")
            st.write(f"Subject: {msg['subject']}")
            st.write(f"Date: {msg['date']}")
            st.write("Fetching message body...")
            body = fetch_message_body(msg["link"])
            st.write(f"Message Body:\n{body}\n")
            processed_messages.add(msg["id"])  # Mark message as processed
    else:
        st.write("No new messages.")

def main():
    """Main Streamlit app."""
    st.title("10 Minute Mail Inbox")
    
    # Initialize WebDriver
    initialize_driver()
    
    # Session state for email
    if "email" not in st.session_state:
        st.session_state.email = fetch_email()
    
    st.write(f"Your temporary email: {st.session_state.email}")
    
    # Refresh inbox button
    if st.button("Refresh Inbox"):
        refresh_inbox()
    
    # Reset email button
    if st.button("Get New Email"):
        global processed_messages
        processed_messages.clear()
        st.session_state.email = fetch_email()
        st.write(f"New temporary email: {st.session_state.email}")

    # Cleanup on app exit
    if st.button("Quit"):
        st.write("Quitting the driver...")
        if driver:
            driver.quit()
            st.stop()

if __name__ == "__main__":
    main()
