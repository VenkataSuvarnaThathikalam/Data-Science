import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_subcategory_kpis
from utils.charts import bar_chart

st.set_page_config(page_title="Sub-Category Analysis")

st.title("Sub-Category Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        st.subheader("Sub-Category Performance")

        # --- KPI Cards ---
        best_subcategory = df_filtered.groupby("Sub-Category")["Sales"].sum().idxmax()
        worst_subcategory = df_filtered.groupby("Sub-Category")["Sales"].sum().idxmin()
        highest_sales_subcategory = df_filtered.groupby("Sub-Category")["Sales"].sum().idxmax()
        highest_loss_subcategory = df_filtered.groupby("Sub-Category")["Profit"].sum().idxmin()

        cols = st.columns(4)
        cols[0].metric("Best Sub-Category", best_subcategory)
        cols[1].metric("Worst Sub-Category", worst_subcategory)
        cols[2].metric("Highest Sales Sub-Category", highest_sales_subcategory)
        cols[3].metric("Highest Loss Sub-Category", highest_loss_subcategory)

        # --- Charts ---
        st.plotly_chart(
            bar_chart(df_filtered, "Sub-Category", "Sales", "Top 10 Sub-Categories by Sales", top_n=10),
            use_container_width=True
        )

        st.plotly_chart(
            bar_chart(df_filtered, "Sub-Category", "Profit", "Top 10 Sub-Categories by Profit", top_n=10),
            use_container_width=True
        )

        st.subheader("Quantity by Sub-Category")
        st.plotly_chart(
            bar_chart(df_filtered, "Sub-Category", "Quantity", "Quantity by Sub-Category"),
            use_container_width=True
        )

        st.subheader("Profit Margin by Sub-Category")
        subcategory_kpis = get_subcategory_kpis(df_filtered)
        st.plotly_chart(
            bar_chart(subcategory_kpis, "Sub-Category", "Profit Margin %", "Profit Margin by Sub-Category"),
            use_container_width=True
        )

        st.subheader("Discount by Sub-Category")
        avg_discount = df_filtered.groupby("Sub-Category")["Discount"].mean().reset_index()
        st.plotly_chart(
            bar_chart(avg_discount, "Sub-Category", "Discount", "Average Discount by Sub-Category"),
            use_container_width=True
        )

        # --- Summary Table ---
        st.subheader("Sub-Category Summary")
        st.dataframe(
            subcategory_kpis[["Sub-Category", "Sales", "Profit", "Quantity", "Avg Discount", "Profit Margin %"]],
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")
