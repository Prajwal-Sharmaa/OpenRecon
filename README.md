# OSINT Investigation Suite

A local-first Streamlit application for defensive, public-source research. It helps build search queries for an authorized target, track investigation notes, save useful resources, and export a research-planning summary.

## Features

- Investigation Builder for full name, username, email, phone, domain, website, company, IP address, alias, CCTV assets, Indian public records, and keyword targets.
- Curated, field-specific search queries across 19 research categories.
- Google, Bing, and DuckDuckGo launch links with per-query copy-to-clipboard.
- Local bookmarks for dorks, tools, and investigations.
- Analyst notes (UTC timestamped) and an investigation review checklist.
- Searchable toolkit directory of official public-source resources, with field-specific recommendations.
- CSV, Markdown, and PDF report export.
- All data is stored locally in `.osint_data/`.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run the regression checks with:

```powershell
python -m unittest discover -s tests
```

PDF export requires `fpdf2`, which is already listed in `requirements.txt`.

## Data storage

Investigations, notes, bookmarks, and preferences are stored as JSON in `.osint_data/` next to the project. This folder is excluded from version control and should be treated as potentially sensitive local data.

## Safety boundary

The application generates browser launch links for analyst-reviewed public search queries. It does not scrape search engines, bypass logins or CAPTCHAs, run third-party tools, collect credentials, or automate access to private data. Use it only for lawful, authorized defensive investigations.
