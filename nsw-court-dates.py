from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tabulate import tabulate
from openpyxl import Workbook
import csv
import time
import os
import re

# Toggle name redaction
REDACT_NAMES = True

# Prompt user for search term
search_term = input("Enter a name to search for (e.g. Smith): ").strip()
if not search_term:
    print("❌ Search term cannot be empty.")
    exit(1)

# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the target URL
url = "https://onlineregistry.lawlink.nsw.gov.au/content/court-lists#/"
driver.get(url)

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

def redact_case_title(title: str) -> str:
    """Redact names in case titles"""
    redacted = re.sub(r'(v\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', title)
    redacted = re.sub(r'([Ff]or\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', redacted)
    return redacted

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
    print("No resultTable found.")

# Close browser
driver.quit()

# Define headers (based on observed structure — update if needed)
headers = [
    'Date', 'Time', 'Case Number', 'Case Title', 'Type', 'Court',
    'Event', 'Presiding Officer', 'Location', 'Courtroom', 'Listing Number'
]

# Pretty-print to CLI
if results:
    print(f"\n🧾 Court Listings for '{search_term}':\n")
    print(tabulate(results, headers=headers, tablefmt="fancy_grid"))

    # Export to CSV
    csv_filename = f"court_listings_{search_term.lower()}.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)
    print(f"\n✅ CSV exported to: {os.path.abspath(csv_filename)}")

    # Export to Excel
    excel_filename = f"court_listings_{search_term.lower()}.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Court Listings"
    ws.append(headers)
    for row in results:
        ws.append(row)
    wb.save(excel_filename)
    print(f"✅ Excel exported to: {os.path.abspath(excel_filename)}")
else:
    print(f"No results found for '{search_term}'.")
