from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

import db

st.set_page_config(page_title="BasketCraft — Merchandising Dashboard", layout="wide")
st.title("BasketCraft — Merchandising Dashboard")

# ── Sidebar: date range ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Date Range")
    default_end = date(2026, 3, 19)
    default_start = default_end - timedelta(days=364)
    start = st.date_input("Start", value=default_start, min_value=date(2023, 3, 19), max_value=default_end)
    end   = st.date_input("End",   value=default_end,   min_value=date(2023, 3, 19), max_value=default_end)
    if start > end:
        st.error("Start must be before End.")
        st.stop()

# ── KPI scorecards ────────────────────────────────────────────────────────────
try:
    m = db.get_headline_metrics(start, end)

    def _delta(cur, prv):
        if prv and prv != 0:
            return f"{(cur - prv) / abs(prv) * 100:+.1f}%"
        return None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue",    f"${m['revenue'][0]:,.0f}", _delta(*m['revenue']))
    c2.metric("Total Orders",     f"{m['orders'][0]:,}",      _delta(*m['orders']))
    c3.metric("Avg Order Value",  f"${m['aov'][0]:,.2f}",     _delta(*m['aov']))
    c4.metric("Total Items Sold", f"{m['items'][0]:,}",       _delta(*m['items']))
except Exception as e:
    st.error(f"Could not load metrics: {e}")

st.divider()

# ── Revenue trend ─────────────────────────────────────────────────────────────
st.subheader("Revenue Trend")
try:
    trend_df = db.get_revenue_trend(start, end)
    if not trend_df.empty:
        trend_df["MONTH"] = pd.to_datetime(trend_df["MONTH"])
        fig = px.line(
            trend_df, x="MONTH", y="REVENUE",
            labels={"REVENUE": "Revenue ($)", "MONTH": ""},
        )
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected period.")
except Exception as e:
    st.error(f"Could not load trend: {e}")

st.divider()

# ── Top products by revenue ───────────────────────────────────────────────────
st.subheader("Top Products by Revenue")
try:
    prod_df = db.get_top_products(start, end)
    if not prod_df.empty:
        fig = px.bar(
            prod_df.sort_values("REVENUE"),
            x="REVENUE", y="PRODUCT_NAME", orientation="h",
            labels={"REVENUE": "Revenue ($)", "PRODUCT_NAME": ""},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product data for the selected period.")
except Exception as e:
    st.error(f"Could not load top products: {e}")

st.divider()

# ── Bundle finder ─────────────────────────────────────────────────────────────
st.subheader("Bundle Finder: Bought With…")
try:
    product_names = db.get_product_names()
    selected = st.selectbox("Pick a product", product_names)
    if selected:
        bundle_df = db.get_bundle_pairs(selected, start, end)
        if not bundle_df.empty:
            fig = px.bar(
                bundle_df.sort_values("ORDER_COUNT"),
                x="ORDER_COUNT", y="ALSO_BOUGHT", orientation="h",
                labels={"ORDER_COUNT": "# of Orders", "ALSO_BOUGHT": ""},
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(
                bundle_df.rename(columns={"ALSO_BOUGHT": "Also Bought", "ORDER_COUNT": "# of Orders"}),
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "⬇ Download CSV",
                bundle_df.to_csv(index=False),
                "bundle_pairs.csv",
                "text/csv",
            )
        else:
            st.info("No co-purchase data for the selected product and period.")
except Exception as e:
    st.error(f"Could not load bundle data: {e}")
