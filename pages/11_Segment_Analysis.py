import sys
from pathlib import Path
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_segment_kpis
from utils.charts import bar_chart

st.set_page_config(page_title="Customer Segment Analysis")
st.title("Customer Segment Analysis")

try:
    df = load_superstore_data()

    required = {"Segment", "Sales", "Profit", "Order ID", "Quantity", "Customer ID", "Discount"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {sorted(missing)}")
        st.stop()

    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        st.subheader("Segment Performance")

        segment_kpis = get_segment_kpis(df_filtered)

        if segment_kpis.empty:
            st.warning("No segment data available after filtering.")
            st.stop()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sales by Segment", f"${segment_kpis['Sales'].sum():,.0f}")
        col2.metric("Profit by Segment", f"${segment_kpis['Profit'].sum():,.0f}")
        col3.metric("Customers by Segment", f"{segment_kpis['Customers'].sum():,}")
        col4.metric("Orders by Segment", f"{segment_kpis['Orders'].sum():,}")

        st.plotly_chart(
            bar_chart(df_filtered, "Segment", "Sales", "Sales by Segment"),
            use_container_width=True
        )
        st.plotly_chart(
            bar_chart(df_filtered, "Segment", "Profit", "Profit by Segment"),
            use_container_width=True
        )
        st.plotly_chart(
            bar_chart(df_filtered, "Segment", "Quantity", "Quantity by Segment"),
            use_container_width=True
        )
        st.plotly_chart(
            bar_chart(df_filtered, "Segment", "Order ID", "Orders by Segment", aggfunc="nunique"),
            use_container_width=True
        )

        st.subheader("Profit Margin by Segment")
        st.plotly_chart(
            bar_chart(segment_kpis, "Segment", "Profit Margin %", "Profit Margin by Segment"),
            use_container_width=True
        )

        st.subheader("Discount by Segment")
        st.plotly_chart(
            bar_chart(segment_kpis, "Segment", "Avg Discount", "Average Discount by Segment"),
            use_container_width=True
        )

        st.subheader("Segment Summary")
        display_cols = ["Segment", "Sales", "Profit", "Quantity", "Orders", "Customers", "Avg Discount", "Profit Margin %"]
        display_df = segment_kpis[display_cols].copy()
        display_df = display_df.rename(columns={"Profit Margin %": "Margin %"})
        st.dataframe(display_df, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Segment Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())