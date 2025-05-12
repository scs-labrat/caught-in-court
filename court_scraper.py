import os
import requests
import json
from datetime import datetime
import subprocess

# Load court URLs
with open('urls.json') as f:
    court_urls = json.load(f)

today = datetime.now().strftime('%Y-%m-%d')

for court, url in court_urls.items():
    court_dir = os.path.join('data', court)
    os.makedirs(court_dir, exist_ok=True)
    filename = os.path.join(court_dir, f"{today}.pdf")
    
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded {court}")
    except Exception as e:
        print(f"❌ Failed for {court}: {e}")
