import os

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


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


@st.cache_data(ttl=600)
def get_headline_metrics() -> pd.DataFrame:
    """Current and prior month: total revenue, orders, items sold."""
    return _query("""
        SELECT
            DATE_TRUNC('month', ORDER_DATE)                                    AS MONTH,
            SUM(CASE WHEN NOT IS_REFUND THEN REVENUE  ELSE 0 END)             AS TOTAL_REVENUE,
            COUNT(DISTINCT CASE WHEN NOT IS_REFUND THEN ORDER_ID END)         AS TOTAL_ORDERS,
            SUM(CASE WHEN NOT IS_REFUND THEN QUANTITY ELSE 0 END)             AS TOTAL_ITEMS
        FROM REVENUE
        WHERE DATE_TRUNC('month', ORDER_DATE) IN (
            DATE_TRUNC('month', CURRENT_DATE()),
            DATE_TRUNC('month', DATEADD('month', -1, CURRENT_DATE()))
        )
        GROUP BY 1
        ORDER BY 1 DESC
    """)


@st.cache_data(ttl=600)
def get_product_revenue_last_quarter() -> pd.DataFrame:
    """Top 10 products by revenue across each month of the prior quarter."""
    return _query("""
        WITH top_products AS (
            SELECT PRODUCT_NAME
            FROM REVENUE
            WHERE ORDER_DATE >= DATE_TRUNC('quarter', DATEADD('quarter', -1, CURRENT_DATE()))
              AND ORDER_DATE <  DATE_TRUNC('quarter', CURRENT_DATE())
              AND NOT IS_REFUND
            GROUP BY PRODUCT_NAME
            ORDER BY SUM(REVENUE) DESC
            LIMIT 10
        )
        SELECT
            r.PRODUCT_NAME,
            DATE_TRUNC('month', r.ORDER_DATE) AS MONTH,
            SUM(r.REVENUE)                    AS REVENUE
        FROM REVENUE r
        JOIN top_products t ON r.PRODUCT_NAME = t.PRODUCT_NAME
        WHERE r.ORDER_DATE >= DATE_TRUNC('quarter', DATEADD('quarter', -1, CURRENT_DATE()))
          AND r.ORDER_DATE <  DATE_TRUNC('quarter', CURRENT_DATE())
          AND NOT r.IS_REFUND
        GROUP BY 1, 2
        ORDER BY 2, 3 DESC
    """)


@st.cache_data(ttl=600)
def get_bundle_pairs() -> pd.DataFrame:
    """Top 20 product pairs that appear in the same order."""
    return _query("""
        SELECT
            a.PRODUCT_NAME AS PRODUCT_A,
            b.PRODUCT_NAME AS PRODUCT_B,
            COUNT(*)       AS CO_PURCHASE_COUNT
        FROM REVENUE a
        JOIN REVENUE b
          ON a.ORDER_ID      = b.ORDER_ID
         AND a.PRODUCT_NAME  < b.PRODUCT_NAME
        WHERE NOT a.IS_REFUND
          AND NOT b.IS_REFUND
        GROUP BY 1, 2
        ORDER BY 3 DESC
        LIMIT 20
    """)


@st.cache_data(ttl=600)
def get_refund_rates() -> pd.DataFrame:
    """Top 10 products by refund rate."""
    return _query("""
        SELECT
            PRODUCT_NAME,
            COUNT(DISTINCT CASE WHEN NOT IS_REFUND THEN ORDER_ID END) AS TOTAL_ORDERS,
            COUNT(DISTINCT CASE WHEN     IS_REFUND THEN ORDER_ID END) AS REFUND_COUNT,
            ROUND(
                COUNT(DISTINCT CASE WHEN IS_REFUND THEN ORDER_ID END) * 100.0 /
                NULLIF(COUNT(DISTINCT ORDER_ID), 0),
            2) AS REFUND_RATE_PCT
        FROM REVENUE
        GROUP BY PRODUCT_NAME
        HAVING COUNT(DISTINCT CASE WHEN NOT IS_REFUND THEN ORDER_ID END) > 0
        ORDER BY REFUND_RATE_PCT DESC
        LIMIT 10
    """)


@st.cache_data(ttl=600)
def get_new_vs_returning() -> pd.DataFrame:
    """Top 10 products by revenue for new vs returning customers."""
    return _query("""
        WITH first_purchase AS (
            SELECT CUSTOMER_ID, MIN(ORDER_DATE) AS first_date
            FROM REVENUE
            WHERE NOT IS_REFUND
            GROUP BY CUSTOMER_ID
        ),
        tagged AS (
            SELECT
                r.PRODUCT_NAME,
                r.REVENUE,
                CASE WHEN r.ORDER_DATE = f.first_date THEN 'New' ELSE 'Returning' END AS CUSTOMER_TYPE
            FROM REVENUE r
            JOIN first_purchase f ON r.CUSTOMER_ID = f.CUSTOMER_ID
            WHERE NOT r.IS_REFUND
        ),
        aggregated AS (
            SELECT CUSTOMER_TYPE, PRODUCT_NAME, SUM(REVENUE) AS REVENUE
            FROM tagged
            GROUP BY CUSTOMER_TYPE, PRODUCT_NAME
        ),
        ranked AS (
            SELECT
                CUSTOMER_TYPE,
                PRODUCT_NAME,
                REVENUE,
                ROW_NUMBER() OVER (PARTITION BY CUSTOMER_TYPE ORDER BY REVENUE DESC) AS rn
            FROM aggregated
        )
        SELECT CUSTOMER_TYPE, PRODUCT_NAME, REVENUE
        FROM ranked
        WHERE rn <= 10
        ORDER BY CUSTOMER_TYPE, REVENUE DESC
    """)
