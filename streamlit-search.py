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
import io
import base64
import PyPDF2

# --- Styling ---
custom_css = """
    <style>
    html, body, [class*="css"] {
        background-color: #0c0c0c;
        color: #f5f5f5;
        font-family: 'Fira Code', monospace;
    }
    .stTextInput > div > div > input {
        background-color: #1c1c1c;
        color: #f5f5f5;
    }
    .stButton button {
        background-color: #d72638;
        color: white;
        border-radius: 8px;
    }
    .stDownloadButton button {
        background-color: #277da1;
        color: white;
        border-radius: 8px;
    }
    .reportview-container .markdown-text-container {
        font-size: 16px;
    }
    </style>
"""

# --- Page Config ---
st.set_page_config(page_title="Court Listings Scraper", layout="wide")

# --- Apply Custom CSS ---
st.markdown(custom_css, unsafe_allow_html=True)

# --- Main Title ---
st.title("⚖️ Court Listings Scraper")

# --- Region Selection ---
region = st.radio(
    "Select Region:",
    options=["NSW", "QLD"],
    horizontal=True
)

# --- NSW Functionality ---
if region == "NSW":
    st.markdown("### NSW Court Listings Search")

    # Toggle name redaction
    REDACT_NAMES = True

    # Function to redact case title
    def redact_case_title(title: str) -> str:
        """Redact names in case titles"""
        redacted = re.sub(r'(v\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', title)
        redacted = re.sub(r'([Ff]or\s+)([A-Z][A-Za-z\-\' ]+)', r'\1[REDACTED]', redacted)
        return redacted

    # User input for search term
    search_term = st.text_input("Search Term (e.g., Smith):").strip()

    # Styling for colored output
    def colored_text(text, color):
        return f'<span style="color:{color}">{text}</span>'

    if search_term:
        st.write(f"Searching for court listings for: **{search_term}**")

        # Setup Chrome WebDriver
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            st.error(f"Error initializing Chrome WebDriver: {e}.  Ensure Chrome is installed correctly.")
            driver = None # Set to None so the rest of the script doesn't attempt to use it.
            results = None


        if driver:
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
                if st.button("Download CSV", key="nsw_csv"):
                    with open(csv_filename, mode="w", newline="", encoding="utf-utf8") as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(results)
                    st.success(f"CSV exported to: {os.path.abspath(csv_filename)}")
                    st.download_button(label="Download CSV", data=open(csv_filename, 'rb').read(), file_name=csv_filename, key="nsw_csv_download")

                # Excel Export
                excel_filename = f"court_listings_{search_term.lower()}.xlsx"
                if st.button("Download Excel", key="nsw_excel"):
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Court Listings"
                    ws.append(headers)
                    for row in results:
                        ws.append(row)
                    wb.save(excel_filename)
                    st.success(f"Excel exported to: {os.path.abspath(excel_filename)}")
                    st.download_button(label="Download Excel", data=open(excel_filename, 'rb').read(), file_name=excel_filename, key="nsw_excel_download")

            else:
                st.warning(f"No results found for '{search_term}'.")
        else:
            st.stop() # Stop execution if WebDriver failed.

    else:
        st.info("Please enter a search term to get started.")



# --- QLD Functionality ---
elif region == "QLD":
    st.markdown("### QLD Court Listings Search")
    st.markdown("#### 🔍 Enter a name to scan across downloaded court PDFs")
    name = st.text_input("Name to search", placeholder="e.g. John Smith")

    @st.cache_data(show_spinner=False)
    def search_name(name, root='data'):
        hits = []
        for court in os.listdir(root):
            court_path = os.path.join(root, court)
            if not os.path.isdir(court_path):
                continue
            for file in os.listdir(court_path):
                if file.endswith('.pdf'):
                    file_path = os.path.join(court_path, file)
                    try:
                        with open(file_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            for i, page in enumerate(reader.pages):
                                text = page.extract_text() or ""
                                if name.lower() in text.lower():
                                    hits.append((court, file, i + 1))
                    except Exception as e:
                        st.error(f"❌ Error reading {file_path}: {e}")
        return hits

    def extract_pages(pdf_path, page_numbers):
        output = PyPDF2.PdfWriter()
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in page_numbers:
                try:
                    output.add_page(reader.pages[page_num - 1])
                except IndexError:
                    st.warning(f"⚠️ Page {page_num} not found in {pdf_path}")
        buffer = io.BytesIO()
        output.write(buffer)
        buffer.seek(0)
        return buffer

    def display_pdf_link(file_bytes, filename="preview.pdf"):
        base64_pdf = base64.b64encode(file_bytes.read()).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank">📄 Open preview in new tab</a>'
        st.markdown(href, unsafe_allow_html=True)

    # -- Search logic
    if name:
        with st.spinner("🕵️‍♂️ Searching... please wait."):
            results = search_name(name)

        if results:
            st.success(f"✅ Found {name} in {len(results)} page(s):")

            grouped = {}
            for court, file, page in results:
                key = (court, file)
                grouped.setdefault(key, []).append(page)

            for (court, file), pages in grouped.items():
                st.markdown("---")
                st.markdown(f"#### 📂 {court} — {file}")
                st.markdown(f"**🧾 Matching Pages:** {', '.join(map(str, pages))}")

                pdf_path = os.path.join('data', court, file)
                combined_pdf = extract_pages(pdf_path, pages)

                st.download_button(
                    label="⬇️ Download matched pages",
                    data=combined_pdf,
                    file_name=f"{court}_{file.replace('.pdf', '')}_matches.pdf",
                    mime="application/pdf",
                    key=f"{court}_{file}" # unique key
                )

                combined_pdf.seek(0)
                display_pdf_link(combined_pdf)

        else:
            st.warning(f"🚫 No matches found for {name}.")
    else:
        st.info("👈 Enter a name above to start searching.")