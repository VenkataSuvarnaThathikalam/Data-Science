import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.page_helpers import load_superstore_data
from utils.filters import sidebar_filters, apply_filters
from utils.charts import bar_chart

st.set_page_config(page_title="Regional Analysis")

st.title("Regional Analysis")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        summary = df_filtered.groupby('Region').agg(
            Sales=('Sales', 'sum'),
            Profit=('Profit', 'sum'),
            Quantity=('Quantity', 'sum'),
            Orders=('Order ID', 'nunique'),
            Customers=('Customer ID', 'nunique')
        )
        summary['Avg Order Value'] = summary['Sales'] / summary['Orders']
        summary['Profit Margin %'] = (summary['Profit'] / summary['Sales']) * 100

        st.write("Regional comparison is available via the charts below.")

        st.plotly_chart(bar_chart(df_filtered, 'Region', 'Sales', 'Sales by Region'), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, 'Region', 'Profit', 'Profit by Region'), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, 'Region', 'Order ID', 'Orders by Region', aggfunc='count'), use_container_width=True)
        st.plotly_chart(bar_chart(df_filtered, 'Region', 'Quantity', 'Quantity by Region'), use_container_width=True)

        st.plotly_chart(bar_chart(
            summary.reset_index(),
            'Region',
            'Profit Margin %',
            'Profit Margin by Region'
        ), use_container_width=True)

        st.data_editor(summary, disabled=True)

except FileNotFoundError:
    st.error("Dataset file not found. Add `data/Sample - Superstore.csv`.")
    