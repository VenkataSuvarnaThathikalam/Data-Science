import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.page_helpers import load_superstore_data
from utils.filters import sidebar_filters, apply_filters
from utils.charts import bar_chart

st.set_page_config(page_title="State Analysis")

st.title("State Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    state_filter = st.sidebar.multiselect(
        "State",
        options=sorted(df['State'].dropna().unique()),
        default=sorted(df['State'].dropna().unique())
    )
    df_filtered = apply_filters(df, filters)
    df_filtered = df_filtered[df_filtered['State'].isin(state_filter)]

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        total_sales = df_filtered['Sales'].sum()
        total_profit = df_filtered['Profit'].sum()
        total_orders = df_filtered['Order ID'].nunique()
        total_quantity = df_filtered['Quantity'].sum()
        profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

        cols = st.columns(5)
        cols[0].metric("Total Sales", f"${total_sales:,.0f}")
        cols[1].metric("Total Profit", f"${total_profit:,.0f}")
        cols[2].metric("Total Orders", f"{total_orders:,}")
        cols[3].metric("Total Quantity", f"{total_quantity:,}")
        cols[4].metric("Profit Margin %", f"{profit_margin:.2f}%")

        state_summary = df_filtered.groupby('State').agg(
            Sales=('Sales', 'sum'),
            Profit=('Profit', 'sum'),
            Quantity=('Quantity', 'sum'),
            Orders=('Order ID', 'nunique'),
            Customers=('Customer ID', 'nunique')
        ).reset_index()
        state_summary['Profit Margin %'] = (state_summary['Profit'] / state_summary['Sales']) * 100

        st.dataframe(state_summary)

        st.plotly_chart(bar_chart(df_filtered, 'State', 'Sales', 'Top 10 States by Sales', top_n=10), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, 'State', 'Profit', 'Top 10 States by Profit', top_n=10), use_container_width=True)

        loss_data = df_filtered[df_filtered['Profit'] < 0]
        if not loss_data.empty:
            st.plotly_chart(bar_chart(loss_data, 'State', 'Profit', 'Bottom 10 States by Profit', top_n=10), use_container_width=True)

        st.plotly_chart(bar_chart(df_filtered, 'State', 'Order ID', 'Orders by State', aggfunc='count'), use_container_width=True)
        st.plotly_chart(bar_chart(state_summary, 'State', 'Profit Margin %', 'Profit Margin by State'), use_container_width=True)

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")