# BasketCraft Dashboard — Minimal Streamlit Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a minimal Streamlit app that renders a single "BasketCraft Dashboard" title and can be run locally.

**Architecture:** Single `app.py` entry point backed by a `requirements.txt`. No pages, no sidebar, no data — just a runnable foundation. A lightweight smoke test uses Streamlit's built-in `AppTest` harness to verify the title renders without a browser.

**Tech Stack:** Python 3, Streamlit (latest stable), pytest

---

### Task 1: Pin dependencies and install Streamlit

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

- [ ] **Step 1: Create `requirements.txt`**

```
streamlit
```

- [ ] **Step 2: Create `requirements-dev.txt`**

```
-r requirements.txt
pytest
```

- [ ] **Step 3: Install into the active Python environment**

Run:
```bash
pip install -r requirements-dev.txt
```

Expected: packages install without errors. Verify with:
```bash
python -m streamlit --version
```
Expected output: something like `Streamlit, version 1.x.x`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt requirements-dev.txt
git commit -m "chore: add Streamlit and pytest dependencies"
```

---

### Task 2: Write the failing smoke test

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_app.py`

- [ ] **Step 1: Create the tests package**

Create `tests/__init__.py` as an empty file.

- [ ] **Step 2: Write the failing test**

Create `tests/test_app.py`:

```python
import pathlib
from streamlit.testing.v1 import AppTest

APP_PATH = pathlib.Path(__file__).parent.parent.resolve() / "app.py"


def test_title_renders():
    at = AppTest.from_file(str(APP_PATH)).run()
    assert at.title[0].value == "BasketCraft Dashboard"
```

- [ ] **Step 3: Run the test — verify it fails**

Run:
```bash
pytest tests/test_app.py::test_title_renders -v
```

Expected: FAIL — `FileNotFoundError` or similar because `app.py` does not exist yet.

- [ ] **Step 4: Commit the failing test**

```bash
git add tests/__init__.py tests/test_app.py
git commit -m "test: add smoke test for dashboard title"
```

---

### Task 3: Implement `app.py` and make the test pass

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create `app.py`**

```python
import streamlit as st

st.title("BasketCraft Dashboard")
```

- [ ] **Step 2: Run the test — verify it passes**

Run:
```bash
pytest tests/test_app.py::test_title_renders -v
```

Expected output:
```
PASSED tests/test_app.py::test_title_renders
```

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add minimal BasketCraft Dashboard Streamlit app"
```

---

### Task 4: Run the app in the browser

- [ ] **Step 1: Launch Streamlit**

Run:
```bash
streamlit run app.py
```

Expected: browser opens automatically (or navigate to `http://localhost:8501`). The page should display the heading **"BasketCraft Dashboard"** and nothing else.

- [ ] **Step 2: Confirm and stop**

Once confirmed, press `Ctrl+C` in the terminal to stop the server.
