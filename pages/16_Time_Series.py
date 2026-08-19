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
from utils.charts import line_chart, multi_line_chart, bar_chart

st.set_page_config(page_title="Time Series Analysis")
st.title("Time Series Analysis")

try:
    df = load_superstore_data()

    required = {"Order Date", "Order ID", "Sales", "Profit", "Quantity"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {sorted(missing)}")
        st.stop()

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"])

    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        time_freq = st.radio(
            "Select time granularity:",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
            horizontal=True,
        )

        freq_map = {
            "Daily": "D",
            "Weekly": "W",
            "Monthly": "ME",
            "Quarterly": "QE",
            "Yearly": "YE",
        }
        freq = freq_map[time_freq]

        # Monthly summary
        monthly = (
            df_filtered.set_index("Order Date")
            .resample("ME")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum"),
                Orders=("Order ID", "nunique"),
            )
            .reset_index()
        )
        monthly["Sales_Growth_%"] = monthly["Sales"].pct_change() * 100
        monthly["Profit_Growth_%"] = monthly["Profit"].pct_change() * 100

        # Quarterly summary
        quarterly = (
            df_filtered.set_index("Order Date")
            .resample("QE")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum"),
                Orders=("Order ID", "nunique"),
            )
            .reset_index()
        )
        quarterly["Sales_Growth_%"] = quarterly["Sales"].pct_change() * 100
        quarterly["Profit_Growth_%"] = quarterly["Profit"].pct_change() * 100

        # Yearly summary
        yearly = (
            df_filtered.set_index("Order Date")
            .resample("YE")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum"),
                Orders=("Order ID", "nunique"),
            )
            .reset_index()
        )
        yearly["Sales_Growth_%"] = yearly["Sales"].pct_change() * 100
        yearly["Profit_Growth_%"] = yearly["Profit"].pct_change() * 100

        current_month = monthly.iloc[-1] if not monthly.empty else None
        prev_month = monthly.iloc[-2] if len(monthly) > 1 else None
        current_year = yearly.iloc[-1] if not yearly.empty else None
        prev_year = yearly.iloc[-2] if len(yearly) > 1 else None

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(
            "Current Month Sales",
            f"${current_month['Sales']:,.0f}" if current_month is not None else "N/A",
        )
        col2.metric(
            "Previous Month Sales",
            f"${prev_month['Sales']:,.0f}" if prev_month is not None else "N/A",
        )
        col3.metric(
            "MoM Growth %",
            f"{current_month['Sales_Growth_%']:.2f}%" if current_month is not None and pd.notna(current_month['Sales_Growth_%']) else "N/A",
        )
        col4.metric(
            "Current Year Sales",
            f"${current_year['Sales']:,.0f}" if current_year is not None else "N/A",
        )
        col5.metric(
            "YoY Growth %",
            f"{current_year['Sales_Growth_%']:.2f}%" if current_year is not None and pd.notna(current_year['Sales_Growth_%']) else "N/A",
        )

        # Main time series charts
        st.subheader(f"Sales Trend ({time_freq})")
        st.plotly_chart(
            line_chart(df_filtered, "Order Date", "Sales", f"Sales Trend ({time_freq})", freq=freq),
            use_container_width=True,
        )

        st.subheader(f"Profit Trend ({time_freq})")
        st.plotly_chart(
            line_chart(df_filtered, "Order Date", "Profit", f"Profit Trend ({time_freq})", freq=freq),
            use_container_width=True,
        )

        st.subheader(f"Order Trend ({time_freq})")
        order_trend = (
            df_filtered.groupby(pd.Grouper(key="Order Date", freq=freq))["Order ID"]
            .nunique()
            .reset_index()
        )
        order_trend.columns = ["Order Date", "Orders"]
        st.plotly_chart(
            bar_chart(order_trend, "Order Date", "Orders", f"Order Trend ({time_freq})"),
            use_container_width=True,
        )

        st.subheader(f"Quantity Trend ({time_freq})")
        st.plotly_chart(
            line_chart(df_filtered, "Order Date", "Quantity", f"Quantity Trend ({time_freq})", freq=freq),
            use_container_width=True,
        )

        # Growth charts
        st.subheader("Quarterly Sales Growth %")
        st.plotly_chart(
            line_chart(quarterly, "Order Date", "Sales_Growth_%", "Quarterly Sales Growth %"),
            use_container_width=True,
        )

        st.subheader("Yearly Sales Growth %")
        st.plotly_chart(
            line_chart(yearly, "Order Date", "Sales_Growth_%", "Yearly Sales Growth %"),
            use_container_width=True,
        )

        st.subheader("Sales Growth vs Profit Growth")
        growth_comparison = yearly[["Order Date", "Sales_Growth_%", "Profit_Growth_%"]].copy()
        st.plotly_chart(
            multi_line_chart(
                growth_comparison,
                "Order Date",
                ["Sales_Growth_%", "Profit_Growth_%"],
                "Sales Growth vs Profit Growth",
            ),
            use_container_width=True,
        )

        st.subheader("Time Period KPIs")
        summary = (
            df_filtered.groupby(pd.Grouper(key="Order Date", freq=freq))
            .agg({"Sales": "sum", "Profit": "sum", "Quantity": "sum", "Order ID": "nunique"})
            .rename(columns={"Order ID": "Orders"})
            .reset_index()
        )
        summary.columns = ["Period", "Sales", "Profit", "Quantity", "Orders"]
        st.dataframe(summary, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Time Series Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())