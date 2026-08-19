import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_category_kpis
from utils.charts import bar_chart, pie_chart, scatter_chart

st.set_page_config(page_title="Category Analysis")

st.title("Category Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        total_sales = df_filtered.groupby("Category")["Sales"].sum().sum()
        total_profit = df_filtered.groupby("Category")["Profit"].sum().sum()
        total_quantity = df_filtered["Quantity"].sum()
        total_orders = df_filtered["Order ID"].nunique()
        profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

        cols = st.columns(5)
        cols[0].metric("Category Sales", f"${total_sales:,.0f}")
        cols[1].metric("Category Profit", f"${total_profit:,.0f}")
        cols[2].metric("Quantity Sold", f"{total_quantity:,}")
        cols[3].metric("Orders", f"{total_orders:,}")
        cols[4].metric("Profit Margin %", f"{profit_margin:.2f}%")

        st.subheader("Sales by Category")
        st.plotly_chart(bar_chart(df_filtered, "Category", "Sales", "Sales by Category"), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, "Category", "Profit", "Profit by Category"), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, "Category", "Quantity", "Quantity by Category"), use_container_width=True)
        st.plotly_chart(pie_chart(df_filtered, "Sales", "Category", "Sales Distribution by Category"), use_container_width=True)

        st.subheader("Orders by Category")
        st.plotly_chart(bar_chart(df_filtered, "Category", "Order ID", "Orders by Category", aggfunc="count"), use_container_width=True)

        st.subheader("Average Discount by Category")
        avg_discount = df_filtered.groupby("Category")["Discount"].mean().reset_index()
        st.plotly_chart(bar_chart(avg_discount, "Category", "Discount", "Average Discount by Category"), use_container_width=True)

        st.subheader("Sales vs Profit by Category")
        st.plotly_chart(scatter_chart(df_filtered, "Sales", "Profit", "Category", "Sales vs Profit by Category"), use_container_width=True)

        st.subheader("Category Performance Summary")
        category_kpis = get_category_kpis(df_filtered)
        st.dataframe(
            category_kpis[["Category", "Sales", "Profit", "Quantity", "Orders", "Profit Margin %"]].rename(
                columns={"Profit Margin %": "Margin %"}
            ),
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")