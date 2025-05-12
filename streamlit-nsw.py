import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from openpyxl import Workbook
import csv
import time
import os
import re

# Toggle name redaction
REDACT_NAMES = True

# Function to redact case title
def redact_case_title(title: str) -> str:
    """Redact names in case titles"""
    redacted = re.sub(r'(v\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', title)
    redacted = re.sub(r'([Ff]or\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', redacted)
    return redacted

# Streamlit UI setup
st.set_page_config(page_title="NSW Court Listings Scraper", layout="wide")
st.title("NSW Court Listings Scraper")
st.markdown("Enter a name to search for court listings:")

# User input for search term
search_term = st.text_input("Search Term (e.g., Smith):").strip()

# Styling for colored output
def colored_text(text, color):
    return f'<span style="color:{color}">{text}</span>'

if search_term:
    st.write(f"Searching for court listings for: **{search_term}**")

    # Setup Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open the target URL
    url = "https://onlineregistry.lawlink.nsw.gov.au/content/court-lists#/"

    driver.get(url)

    # Minimize browser window after opening
    driver.minimize_window()

    # Wait for page load
    time.sleep(5)

    # Find the search input and submit the term
    search_box = driver.find_element(By.ID, "searchInput")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results to load
    time.sleep(6)

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Locate the result table
    table = soup.find("table", class_="resultTable")
    results = []

    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            cell_text = [cell.get_text(strip=True) for cell in cells]
            if cell_text:
                if REDACT_NAMES and len(cell_text) >= 4:
                    cell_text[3] = redact_case_title(cell_text[3])
                results.append(cell_text)
    else:
        st.error("No resultTable found.")

    # Close the browser after scraping
    driver.quit()

    # Define headers
    headers = [
        'Date', 'Time', 'Case Number', 'Case Title', 'Type', 'Court',
        'Event', 'Presiding Officer', 'Location', 'Courtroom', 'Listing Number'
    ]

    # Display results in a more user-friendly format with coloured output
    if results:
        st.subheader(f"Court Listings for '{search_term}'")
        for row in results:
            st.markdown(f'<span style="color:white">Date:</span> <span style="color:green">{row[0]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Time:</span> <span style="color:green">{row[1]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Case Number:</span> <span style="color:green">{row[2]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Case Title:</span> <span style="color:green">{row[3]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Type:</span> <span style="color:green">{row[4]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Court:</span> <span style="color:green">{row[5]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Event:</span> <span style="color:green">{row[6]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Presiding Officer:</span> <span style="color:green">{row[7]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Location:</span> <span style="color:green">{row[8]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Courtroom:</span> <span style="color:green">{row[9]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">Listing Number:</span> <span style="color:green">{row[10]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="color:white">--------------------------</span>', unsafe_allow_html=True)

        # Export options
        st.subheader("Export Options")

        # CSV Export
        csv_filename = f"court_listings_{search_term.lower()}.csv"
        if st.button("Download CSV"):
            with open(csv_filename, mode="w", newline="", encoding="utf-utf8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(results)
            st.success(f"CSV exported to: {os.path.abspath(csv_filename)}")
            st.download_button(label="Download CSV", data=open(csv_filename, 'rb').read(), file_name=csv_filename)

        # Excel Export
        excel_filename = f"court_listings_{search_term.lower()}.xlsx"
        if st.button("Download Excel"):
            wb = Workbook()
            ws = wb.active
            ws.title = "Court Listings"
            ws.append(headers)
            for row in results:
                ws.append(row)
            wb.save(excel_filename)
            st.success(f"Excel exported to: {os.path.abspath(excel_filename)}")
            st.download_button(label="Download Excel", data=open(excel_filename, 'rb').read(), file_name=excel_filename)

    else:
        st.warning(f"No results found for '{search_term}'.")
else:
    st.info("Please enter a search term to get started.")
