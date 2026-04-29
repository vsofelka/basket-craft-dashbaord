import streamlit as st
import plotly.express as px
import db

st.title("BasketCraft Dashboard")

# ── Headline metrics ──────────────────────────────────────────────────────────
try:
    metrics_df = db.get_headline_metrics()
except Exception as e:
    st.error(f"Could not load metrics: {e}")
    metrics_df = None

if metrics_df is not None and len(metrics_df) >= 1:
    cur = metrics_df.iloc[0]
    aov_cur = cur["TOTAL_REVENUE"] / cur["TOTAL_ORDERS"] if cur["TOTAL_ORDERS"] else 0

    if len(metrics_df) >= 2:
        prv = metrics_df.iloc[1]
        aov_prv = prv["TOTAL_REVENUE"] / prv["TOTAL_ORDERS"] if prv["TOTAL_ORDERS"] else 0
        d_rev   = float(cur["TOTAL_REVENUE"] - prv["TOTAL_REVENUE"])
        d_ord   = int(cur["TOTAL_ORDERS"]   - prv["TOTAL_ORDERS"])
        d_aov   = float(aov_cur - aov_prv)
        d_items = int(cur["TOTAL_ITEMS"]    - prv["TOTAL_ITEMS"])
    else:
        d_rev = d_ord = d_aov = d_items = None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue",    f"${cur['TOTAL_REVENUE']:,.0f}", delta=f"${d_rev:,.0f}"   if d_rev   is not None else None)
    c2.metric("Total Orders",     f"{cur['TOTAL_ORDERS']:,}",      delta=f"{d_ord:,}"        if d_ord   is not None else None)
    c3.metric("Avg Order Value",  f"${aov_cur:,.2f}",              delta=f"${d_aov:,.2f}"    if d_aov   is not None else None)
    c4.metric("Total Items Sold", f"{cur['TOTAL_ITEMS']:,}",       delta=f"{d_items:,}"      if d_items is not None else None)

st.divider()

# ── Product revenue last quarter ──────────────────────────────────────────────
st.subheader("Which products drove the most revenue last quarter?")
try:
    prod_df = db.get_product_revenue_last_quarter()
    if not prod_df.empty:
        prod_df["MONTH"] = prod_df["MONTH"].astype(str).str[:7]
        fig = px.bar(
            prod_df, x="MONTH", y="REVENUE", color="PRODUCT_NAME", barmode="group",
            labels={"REVENUE": "Revenue ($)", "MONTH": "Month", "PRODUCT_NAME": "Product"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for last quarter.")
except Exception as e:
    st.error(f"Could not load product revenue: {e}")

st.divider()

# ── Bundle analysis ───────────────────────────────────────────────────────────
st.subheader("Which products get bought together most often?")
try:
    bundle_df = db.get_bundle_pairs()
    if not bundle_df.empty:
        st.dataframe(
            bundle_df.rename(columns={
                "PRODUCT_A": "Product A",
                "PRODUCT_B": "Product B",
                "CO_PURCHASE_COUNT": "Times Bought Together",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No co-purchase data found.")
except Exception as e:
    st.error(f"Could not load bundle data: {e}")

st.divider()

# ── Refund rates ──────────────────────────────────────────────────────────────
st.subheader("Which products have the highest refund rates?")
try:
    refund_df = db.get_refund_rates()
    if not refund_df.empty:
        st.dataframe(
            refund_df.rename(columns={
                "PRODUCT_NAME":    "Product",
                "TOTAL_ORDERS":    "Total Orders",
                "REFUND_COUNT":    "Refunds",
                "REFUND_RATE_PCT": "Refund Rate %",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No refund data found.")
except Exception as e:
    st.error(f"Could not load refund data: {e}")

st.divider()

# ── New vs returning customers ────────────────────────────────────────────────
st.subheader("Do new customers buy different products than returning ones?")
try:
    nvr_df = db.get_new_vs_returning()
    if not nvr_df.empty:
        col_new, col_ret = st.columns(2)
        new_df = nvr_df[nvr_df["CUSTOMER_TYPE"] == "New"]
        ret_df = nvr_df[nvr_df["CUSTOMER_TYPE"] == "Returning"]

        with col_new:
            st.markdown("**New Customers**")
            fig_new = px.bar(
                new_df, x="REVENUE", y="PRODUCT_NAME", orientation="h",
                labels={"REVENUE": "Revenue ($)", "PRODUCT_NAME": ""},
            )
            fig_new.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_new, use_container_width=True)

        with col_ret:
            st.markdown("**Returning Customers**")
            fig_ret = px.bar(
                ret_df, x="REVENUE", y="PRODUCT_NAME", orientation="h",
                labels={"REVENUE": "Revenue ($)", "PRODUCT_NAME": ""},
            )
            fig_ret.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_ret, use_container_width=True)
    else:
        st.info("No customer data found.")
except Exception as e:
    st.error(f"Could not load customer data: {e}")
