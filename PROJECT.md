# Project Overview

## What this is

OSINT Investigation Suite is a local Streamlit application for defensive public-source research planning. An analyst creates a case for an authorized target, generates reviewable search queries, records notes and bookmarks, and exports a research-planning summary.

The application is intentionally narrow: it plans and launches searches, it does not scrape, collect data, or reach into non-public sources.

## Architecture

```
app.py                 Streamlit entry point and page/UI logic
osint_suite/
  catalog.py           dork generation and the toolkit directory loader
  models.py            dataclasses for investigations, dorks, tools, bookmarks
  storage.py           JSON persistence with atomic writes
  styles.py            custom CSS theme
  validation.py        input validation and HTML escaping
  data/toolkit.json    curated toolkit reference data
tests/
  test_catalog.py      regression checks for the dork engine and validation
```

State flows are simple: the UI reads records through `LocalStore`, mutates them in memory, and writes them back atomically to JSON files in `.osint_data/`. Generated queries are cached with Streamlit's `@st.cache_data`.

## Key decisions

- **Local-first.** No server, no accounts, no telemetry. Data lives in `.osint_data/` next to the project.
- **Curated catalogs.** Dork categories and toolkit entries are declared in data/code, not scraped at runtime.
- **Analyst in control.** Every generated query is a suggestion. The app only opens a browser link when the analyst clicks one.
- **Thin validation.** Input checks (email, IP, domain shape, length limits) happen client-side; there is no network lookup.

## Project layout notes

- `app.py` holds the Streamlit pages. UI strings are written directly in the page functions.
- `osint_suite/catalog.py` is the only module that imports Streamlit besides `app.py` (for caching).
- The test suite is deliberately small: it pins down the dork engine and validation behavior so catalog changes stay safe.

## Testing

```bash
python -m unittest discover -s tests
```

## Deployment

See `DEPLOYMENT.md`.
