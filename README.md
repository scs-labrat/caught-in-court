![Caught in Court](caught-in-court.png)
# CAUGHT IN COURT
At present this is only for QLD Magistrates court but the plan is to have full Australia wide coverage and build a searchable repo.

## 🏛️ QLD Court List Scraper & Search Platform

This project automatically downloads daily court law list PDFs for all Queensland locations every weekday at 9am (AEST), stores them in a structured archive, commits them to a GitHub repository, and enables full-text search across all files for name-based queries via a web UI or CLI.

## 📦 Features

- ✅ **Daily scraping** of court law lists (PDFs) via GitHub Actions
- 🗂️ Each court has its **own folder**, with files named by date
- 🔍 **Search for a name** across all PDFs (CLI and Streamlit UI)
- 🐳 **Docker support** for easy deployment
- ☁️ Hosted automation using **GitHub Actions**
- 💡 Clean and extendable codebase

---

## 🗂️ Folder Structure

```

court-scraper/
├── .github/workflows/daily-fetch.yml  # GitHub Actions pipeline
├── court\_scraper.py                   # Main scraper
├── search.py                          # CLI PDF search tool
├── app.py                             # Streamlit frontend
├── urls.json                          # All court URL mappings
├── requirements.txt                   # Dependencies
├── Dockerfile                         # Containerise the app
├── .dockerignore                      # Exclude cache, data
└── data/
└── \[COURT\_NAME]/YYYY-MM-DD.pdf    # Auto-saved law lists

````

---

## ⚙️ How It Works

### ⏰ GitHub Actions

The scraper is scheduled via GitHub Actions to run at **9am AEST, Monday to Friday** (11pm UTC). It:

- Downloads all PDFs from `urls.json`
- Saves them to `/data/[CourtName]/YYYY-MM-DD.pdf`
- Commits & pushes the changes if any are new

### 🔎 Name Search

- **CLI:**  
  ```bash
  python search.py "John Smith"
````

* **Streamlit Web App:**

  ```bash
  streamlit run app.py
  ```

---

## 🚀 Run with Docker

```bash
docker build -t court-search .
docker run -p 8501:8501 court-search
```

Visit [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📝 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR-USERNAME/court-scraper.git
cd court-scraper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📅 Add New Court URLs

Edit `urls.json` to include additional court PDF endpoints:

```json
{
  "Alpha": "https://www.courts.qld.gov.au/__external/CourtsLawList/Alpha_DailyLawList.pdf",
  "Atherton": "https://www.courts.qld.gov.au/__external/CourtsLawList/Atherton_DailyLawList.pdf"
}
```

---

## 🔐 Notes

* PDFs are stored in `data/` (which is `.gitignored` by default). If you want the actual PDFs in GitHub, remove `data/` from `.gitignore`.
* PyPDF2 is used for basic text extraction; results depend on how the court formats each PDF.

---

## 🙋‍♂️ Author

Built by [Smart Cyber Solutions – scs-labrat](https://github.com/scs-labrat) to enhance transparency and accessibility around public court data.

---

## 📄 License

MIT License. This project is intended for ethical, lawful use only.

