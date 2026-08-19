import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_product_kpis
from utils.charts import bar_chart, horizontal_bar_chart, scatter_chart

st.set_page_config(page_title="Product Analysis")

st.title("Product Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        # --- KPI Cards ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Products", df_filtered["Product Name"].nunique())
        col2.metric("Highest Seller", df_filtered.groupby("Product Name")["Sales"].sum().idxmax())
        col3.metric("Most Profitable", df_filtered.groupby("Product Name")["Profit"].sum().idxmax())
        loss_product = (
            df_filtered[df_filtered["Profit"] < 0]
            .groupby("Product Name")["Profit"].sum()
            .idxmin()
            if (df_filtered["Profit"] < 0).any()
            else "None"
        )
        col4.metric("Highest Loss Product", loss_product)

        # --- Top Products by Sales ---
        st.plotly_chart(
            bar_chart(df_filtered, "Product Name", "Sales", "Top 10 Products by Sales", top_n=10),
            use_container_width=True
        )

        # --- Top Products by Profit ---
        st.plotly_chart(
            bar_chart(df_filtered, "Product Name", "Profit", "Top 10 Products by Profit", top_n=10),
            use_container_width=True
        )

        # --- Top Products by Quantity ---
        st.subheader("Top Products by Quantity")
        st.plotly_chart(
            bar_chart(df_filtered, "Product Name", "Quantity", "Top 10 Products by Quantity", top_n=10),
            use_container_width=True
        )

        # --- Bottom Products by Profit ---
        loss_data = df_filtered[df_filtered["Profit"] < 0]
        if not loss_data.empty:
            st.plotly_chart(
                horizontal_bar_chart(df_filtered, "Product Name", "Profit", "Bottom 10 Products by Profit", top_n=10),
                use_container_width=True
            )

        # --- Product Sales vs Profit (FIXED) ---
        st.subheader("Product Sales vs Profit")
        product_summary = df_filtered.groupby("Product Name").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        st.plotly_chart(
            scatter_chart(product_summary, "Sales", "Profit", "Product Name", "Product Sales vs Profit"),
            use_container_width=True
        )

        # --- Product Summary Table ---
        st.subheader("Product Summary")
        product_kpis = get_product_kpis(df_filtered)
        st.dataframe(
            product_kpis[["Product Name", "Category", "Sub-Category", "Sales", "Profit", "Quantity", "Avg Discount", "Profit Margin %"]],
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")
