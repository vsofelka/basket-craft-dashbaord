# BasketCraft — Merchandising Dashboard

**Live app:** _URL to be added once Streamlit Cloud account is active_

## Overview

A Streamlit dashboard built for Maya, Head of Merchandising at BasketCraft. Connects to Snowflake and answers four core merchandising questions:

- Which products drove the most revenue each month last quarter?
- Which products get bought together most often — should we create bundles?
- Which products have the highest refund rates?
- Do new customers buy different products than returning ones?

## Dashboard Sections

| Section | What it shows |
|---|---|
| KPI Scorecards | Total Revenue, Orders, AOV, Items Sold — each with MoM delta |
| Revenue Trend | Monthly revenue line chart |
| Top Products | Horizontal bar chart, top 10 by revenue |
| Bundle Finder | Pick a product, see co-purchase rankings + CSV export |

All sections respect the sidebar date range filter. Queries are cached for 10 minutes.

## Running Locally

1. Clone the repo and enter the directory:
   ```bash
   git clone https://github.com/vsofelka/basket-craft-dashbaord
   cd basket-craft-dashbaord
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Create a `.env` file in the project root with your Snowflake credentials:
   ```
   SNOWFLAKE_ACCOUNT=your-account
   SNOWFLAKE_USER=your-user
   SNOWFLAKE_PASSWORD=your-password
   SNOWFLAKE_ROLE=your-role
   SNOWFLAKE_WAREHOUSE=your-warehouse
   SNOWFLAKE_DATABASE=your-database
   SNOWFLAKE_SCHEMA=your-schema
   ```

4. Run the dashboard:
   ```bash
   python -m streamlit run app.py
   ```

   Then open [http://localhost:8501](http://localhost:8501).

## Stack

- Python · Streamlit · Plotly · Snowflake · pandas
