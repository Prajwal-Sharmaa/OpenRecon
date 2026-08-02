# Deployment

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`

## Install and run

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app listens on Streamlit's default local port and stores its data in `.osint_data/` next to the project.

## Run the tests

```bash
python -m unittest discover -s tests
```

## Data

- Investigations, notes, bookmarks, and settings are stored as JSON in `.osint_data/`.
- The folder is created automatically on first run and is excluded from version control.
- Treat the contents as potentially sensitive local data.

## Known limitations

- PDF export requires `fpdf2` (included in `requirements.txt`).
- JSON storage is fine for small case counts; a larger project would want a real database.
- Search engine support is limited to Google, Bing, and DuckDuckGo.
- No authentication, multi-user support, or remote hosting is provided.
