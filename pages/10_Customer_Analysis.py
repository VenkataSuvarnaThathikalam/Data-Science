import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.charts import bar_chart

st.set_page_config(page_title="Customer Analysis")
st.title("Customer Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        customer_summary = (
            df_filtered.groupby("Customer Name")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum"),
                Orders=("Order ID", "nunique")
            )
            .reset_index()
        )

        customer_summary["Avg Order Value"] = (
            customer_summary["Sales"] / customer_summary["Orders"]
        )
        customer_summary["Profit Margin %"] = (
            customer_summary["Profit"] / customer_summary["Sales"] * 100
        ).fillna(0)

        total_customers = df_filtered["Customer Name"].nunique()
        avg_sales_per_customer = customer_summary["Sales"].mean()
        avg_profit_per_customer = customer_summary["Profit"].mean()
        top_customer = customer_summary.sort_values("Sales", ascending=False).iloc[0]["Customer Name"] if not customer_summary.empty else "N/A"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", f"{total_customers:,}")
        col2.metric("Average Sales per Customer", f"${avg_sales_per_customer:,.2f}")
        col3.metric("Average Profit per Customer", f"${avg_profit_per_customer:,.2f}")
        col4.metric("Top Customer", top_customer)

        st.subheader("Top 10 Customers by Sales")
        st.plotly_chart(
            bar_chart(customer_summary, "Customer Name", "Sales", "Top 10 Customers by Sales", top_n=10),
            use_container_width=True
        )

        st.subheader("Top 10 Customers by Profit")
        st.plotly_chart(
            bar_chart(customer_summary, "Customer Name", "Profit", "Top 10 Customers by Profit", top_n=10),
            use_container_width=True
        )

        st.subheader("Customer Order Frequency")
        st.plotly_chart(
            bar_chart(customer_summary, "Customer Name", "Orders", "Top 10 Customers by Order Frequency", top_n=10),
            use_container_width=True
        )

        st.subheader("Customer Sales Distribution")
        st.plotly_chart(
            bar_chart(customer_summary, "Customer Name", "Sales", "Customer Sales Distribution", top_n=10),
            use_container_width=True
        )

        st.subheader("Customer Profit Distribution")
        st.plotly_chart(
            bar_chart(customer_summary, "Customer Name", "Profit", "Customer Profit Distribution", top_n=10),
            use_container_width=True
        )

        st.subheader("Customer Summary")
        st.dataframe(
            customer_summary[
                ["Customer Name", "Sales", "Profit", "Quantity", "Orders", "Avg Order Value", "Profit Margin %"]
            ].sort_values("Sales", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")
except Exception as e:
    st.error(f"Error: {type(e).__name__}: {e}")