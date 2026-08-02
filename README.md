# 🔍 OpenRecon

A local-first Streamlit application designed to simplify **Open Source Intelligence (OSINT)** investigations by organizing search queries, investigation notes, bookmarks, and research resources in one place.

OpenRecon helps security researchers and analysts perform structured public-source investigations while keeping all data stored locally.

---

## ✨ Features

### 🕵️ Investigation Builder

Create investigations for:

- Full Name
- Username
- Email Address
- Phone Number
- Domain
- Website
- Company
- IP Address
- Alias
- CCTV Assets
- Indian Public Records
- Custom Keywords

---

### 🔎 Search Query Generation

Generate investigation-ready search queries for multiple search engines.

Supported search engines:

- Google
- Bing
- DuckDuckGo

Each query can be copied and opened directly in the browser.

---

### 📚 OSINT Toolkit

Includes categorized public resources for:

- Social Media
- Search Engines
- Domain Intelligence
- DNS & WHOIS
- Metadata
- Archives
- Public Records
- Image Search
- Maps
- Threat Intelligence

---

### 📝 Investigation Workspace

- Investigation Notes
- Investigation Checklist
- Local Bookmarks
- Research Tracking
- UTC Timestamped Notes

---

### 📄 Report Export

Export investigations as:

- PDF
- Markdown
- CSV

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Streamlit | User Interface |
| Pandas | Data Handling |
| FPDF2 | PDF Report Export |
| JSON | Local Data Storage |

---

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/Prajwal-Sharmaa/OpenRecon.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

Run tests

```bash
python -m unittest discover -s tests
```

---

## 💾 Data Storage

OpenRecon stores investigations, notes, bookmarks and user preferences locally inside the `.osint_data/` directory.

No investigation data is uploaded automatically to external servers.

---

## 🔒 Ethical Use

OpenRecon is intended for **authorized security research and public-source investigations** only.

The application:

- Generates search queries
- Organizes investigation data
- Stores notes locally
- Does not scrape search engines
- Does not bypass authentication
- Does not automate access to private information

Users are responsible for ensuring that all investigations comply with applicable laws and organizational policies.

---

## 📌 Future Improvements

- Additional OSINT resources
- Better report customization
- Investigation timeline
- Advanced filtering
- Improved dashboard

---

## 📄 License

This project is intended for educational purposes and authorized security research.
