import os
from datetime import date, timedelta

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _to_date(col: str = "CREATED_AT") -> str:
    return f"TO_DATE(TO_TIMESTAMP_NTZ({col}, 9))"


def _connect():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )


def _query(sql: str) -> pd.DataFrame:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


def _prior_period(start: date, end: date) -> tuple:
    days = (end - start).days + 1
    prior_end = start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=days - 1)
    return prior_start, prior_end


def _period_metrics(start: date, end: date) -> tuple:
    df = _query(f"""
        SELECT
            COALESCE(SUM(PRICE_USD), 0)        AS REVENUE,
            COUNT(DISTINCT ORDER_ID)            AS ORDERS,
            COALESCE(SUM(ITEMS_PURCHASED), 0)  AS ITEMS
        FROM ORDERS
        WHERE {_to_date()} BETWEEN '{start}' AND '{end}'
    """)
    r = df.iloc[0]
    rev = float(r["REVENUE"])
    ord_ = int(r["ORDERS"])
    items = int(r["ITEMS"])
    aov = rev / ord_ if ord_ else 0.0
    return rev, ord_, aov, items


@st.cache_data(ttl=600)
def get_headline_metrics(start: date, end: date) -> dict:
    """Returns {metric: (current_val, prior_val)} for Revenue, Orders, AOV, Items."""
    prior_start, prior_end = _prior_period(start, end)
    cur = _period_metrics(start, end)
    prv = _period_metrics(prior_start, prior_end)
    return {
        "revenue": (cur[0], prv[0]),
        "orders":  (cur[1], prv[1]),
        "aov":     (cur[2], prv[2]),
        "items":   (cur[3], prv[3]),
    }


@st.cache_data(ttl=600)
def get_revenue_trend(start: date, end: date) -> pd.DataFrame:
    return _query(f"""
        SELECT
            DATE_TRUNC('month', {_to_date()})::DATE  AS MONTH,
            SUM(PRICE_USD)                            AS REVENUE
        FROM ORDERS
        WHERE {_to_date()} BETWEEN '{start}' AND '{end}'
        GROUP BY 1
        ORDER BY 1
    """)


@st.cache_data(ttl=600)
def get_top_products(start: date, end: date) -> pd.DataFrame:
    return _query(f"""
        SELECT
            p.PRODUCT_NAME,
            SUM(oi.PRICE_USD)  AS REVENUE
        FROM ORDER_ITEMS oi
        JOIN PRODUCTS p ON oi.PRODUCT_ID = p.PRODUCT_ID
        WHERE {_to_date('oi.CREATED_AT')} BETWEEN '{start}' AND '{end}'
        GROUP BY p.PRODUCT_NAME
        ORDER BY REVENUE DESC
        LIMIT 10
    """)


@st.cache_data(ttl=600)
def get_product_names() -> list:
    df = _query("SELECT PRODUCT_NAME FROM PRODUCTS ORDER BY PRODUCT_NAME")
    return df["PRODUCT_NAME"].tolist()


@st.cache_data(ttl=600)
def get_bundle_pairs(product_name: str, start: date, end: date) -> pd.DataFrame:
    safe = product_name.replace("'", "''")
    return _query(f"""
        SELECT
            p2.PRODUCT_NAME            AS ALSO_BOUGHT,
            COUNT(DISTINCT a.ORDER_ID) AS ORDER_COUNT
        FROM ORDER_ITEMS a
        JOIN PRODUCTS p1 ON a.PRODUCT_ID = p1.PRODUCT_ID
        JOIN ORDER_ITEMS b
          ON a.ORDER_ID    = b.ORDER_ID
         AND a.PRODUCT_ID != b.PRODUCT_ID
        JOIN PRODUCTS p2 ON b.PRODUCT_ID = p2.PRODUCT_ID
        WHERE p1.PRODUCT_NAME = '{safe}'
          AND {_to_date('a.CREATED_AT')} BETWEEN '{start}' AND '{end}'
        GROUP BY p2.PRODUCT_NAME
        ORDER BY ORDER_COUNT DESC
    """)
