# BasketCraft Dashboard — Minimal Streamlit Scaffold

**Date:** 2026-04-29  
**Status:** Approved

## Overview

Bootstrap an empty Streamlit dashboard for the BasketCraft project. The goal is a runnable app with a single title, a pinned dependency file, and a clean foundation to build on.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit entry point — renders the app title |
| `requirements.txt` | Pins `streamlit` for reproducible installs |

## Architecture

Single-file app. No pages, no sidebar, no data yet. `app.py` calls `st.title("BasketCraft Dashboard")` and nothing else.

## Dependencies

- `streamlit` (latest stable) installed via `pip install -r requirements.txt`
- No other runtime dependencies at this stage

## Running

```bash
streamlit run app.py
```

## Future considerations

- `.env` is already in the repo; `python-dotenv` can be added when secrets are needed
- Pages can be added under a `pages/` directory as the dashboard grows
