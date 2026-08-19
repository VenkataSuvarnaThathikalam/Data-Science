import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import traceback
import streamlit as st

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_discount_analysis
from utils.charts import bar_chart, scatter_chart, histogram

st.set_page_config(page_title="Discount Analysis")
st.title("Discount Analysis")

try:
    df = load_superstore_data()
    st.write("Debug loaded shape:", df.shape)
    st.write("Debug columns:", list(df.columns))

    required = {"Discount", "Sales", "Profit", "Category", "Sub-Category"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {sorted(missing)}")
        st.stop()

    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)
    st.write("Debug filtered shape:", df_filtered.shape)

    if df_filtered.empty:
        empty_state()
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Discount", f"{df_filtered['Discount'].mean() * 100:.2f}%")
        col2.metric("Max Discount", f"{df_filtered['Discount'].max() * 100:.2f}%")
        col3.metric("Sales w/ Discount", f"${df_filtered[df_filtered['Discount'] > 0]['Sales'].sum():,.0f}")
        col4.metric("Profit w/ Discount", f"${df_filtered[df_filtered['Discount'] > 0]['Profit'].sum():,.0f}")

        st.plotly_chart(
            scatter_chart(df_filtered, "Discount", "Sales", "Category", "Discount vs Sales"),
            use_container_width=True
        )

        st.plotly_chart(
            scatter_chart(df_filtered, "Discount", "Profit", "Category", "Discount vs Profit"),
            use_container_width=True
        )

        col1, col2 = st.columns(2)
        with col1:
            avg_discount_cat = df_filtered.groupby("Category")["Discount"].mean().reset_index()
            avg_discount_cat.columns = ["Category", "Discount"]
            st.plotly_chart(
                bar_chart(avg_discount_cat, "Category", "Discount", "Avg Discount by Category"),
                use_container_width=True
            )
        with col2:
            avg_discount_subcat = (
                df_filtered.groupby("Sub-Category")["Discount"]
                .mean()
                .reset_index()
                .sort_values("Discount", ascending=False)
                .head(10)
            )
            avg_discount_subcat.columns = ["Sub-Category", "Discount"]
            st.plotly_chart(
                bar_chart(avg_discount_subcat, "Sub-Category", "Discount", "Top 10 Sub-Categories by Avg Discount"),
                use_container_width=True
            )

        st.plotly_chart(
            histogram(df_filtered, "Discount", "Discount Distribution"),
            use_container_width=True
        )

        st.subheader("Profit by Discount Range")
        discount_analysis = get_discount_analysis(df_filtered)
        st.dataframe(
            discount_analysis.rename(columns={"Discount_Range": "Discount Range", "Order ID": "Orders"}),
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Discount Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())
    raise