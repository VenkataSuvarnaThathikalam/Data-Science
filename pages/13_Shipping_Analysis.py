import sys
from pathlib import Path
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.charts import bar_chart

st.set_page_config(page_title="Shipping Analysis")
st.title("Shipping Analysis")

try:
    df = load_superstore_data()

    if "Order Date" in df.columns and "Ship Date" in df.columns:
        df["Shipping Days"] = (
            pd.to_datetime(df["Ship Date"]) - pd.to_datetime(df["Order Date"])
        ).dt.days

    required = {"Order ID", "Ship Mode", "Sales", "Profit", "Shipping Days", "Discount"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {sorted(missing)}")
        st.stop()

    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        shipping_kpis = (
            df_filtered.groupby("Ship Mode")
            .agg(
                Shipments=("Order ID", "nunique"),
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Shipping_Days_Avg=("Shipping Days", "mean"),
                Avg_Discount=("Discount", "mean"),
            )
            .reset_index()
        )

        shipping_kpis["Profit Margin %"] = (
            (shipping_kpis["Profit"] / shipping_kpis["Sales"] * 100)
            .replace([float("inf"), float("-inf")], 0)
            .fillna(0)
        )

        shipping_kpis = shipping_kpis.rename(
            columns={
                "Shipping_Days_Avg": "Avg Shipping Days",
                "Avg_Discount": "Avg Discount",
            }
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Shipments", int(shipping_kpis["Shipments"].sum()))
        col2.metric(
            "Most Used Mode",
            df_filtered["Ship Mode"].mode()[0] if not df_filtered["Ship Mode"].mode().empty else "N/A",
        )
        col3.metric("Avg Shipping Days", f"{df_filtered['Shipping Days'].mean():.1f}")
        col4.metric(
            "Fastest Mode",
            shipping_kpis.loc[shipping_kpis["Avg Shipping Days"].idxmin(), "Ship Mode"]
            if not shipping_kpis.empty else "N/A",
        )

        st.plotly_chart(
            bar_chart(df_filtered, "Ship Mode", "Order ID", "Orders by Ship Mode", aggfunc="nunique"),
            use_container_width=True,
        )
        st.plotly_chart(
            bar_chart(df_filtered, "Ship Mode", "Sales", "Sales by Ship Mode"),
            use_container_width=True,
        )
        st.plotly_chart(
            bar_chart(df_filtered, "Ship Mode", "Profit", "Profit by Ship Mode"),
            use_container_width=True,
        )

        st.subheader("Profit Margin by Ship Mode")
        st.plotly_chart(
            bar_chart(shipping_kpis, "Ship Mode", "Profit Margin %", "Profit Margin by Ship Mode"),
            use_container_width=True,
        )

        st.subheader("Discount by Ship Mode")
        st.plotly_chart(
            bar_chart(shipping_kpis, "Ship Mode", "Avg Discount", "Average Discount by Ship Mode"),
            use_container_width=True,
        )

        st.subheader("Shipping Performance")
        st.dataframe(
            shipping_kpis.rename(columns={"Shipments": "Orders"}), 
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Shipping Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())