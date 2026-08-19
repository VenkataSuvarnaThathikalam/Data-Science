import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import traceback
import streamlit as st

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_loss_analysis
from utils.charts import horizontal_bar_chart

st.set_page_config(page_title="Loss Analysis")
st.title("Loss Analysis")

try:
    df = load_superstore_data()
    st.write("Debug loaded shape:", df.shape)
    st.write("Debug columns:", list(df.columns))

    required = {"Order ID", "Order Date", "Product Name", "Category", "Sub-Category", "Customer Name", "Sales", "Profit", "Discount", "Region", "State"}
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
        loss_df = get_loss_analysis(df_filtered)

        if loss_df.empty:
            st.success("No loss-making orders found!")
            st.stop()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Loss", f"${abs(loss_df['Profit'].sum()):,.0f}")
        col2.metric("Loss Orders", len(loss_df))
        col3.metric("Loss Products", loss_df["Product Name"].nunique())
        col4.metric("Loss Customers", loss_df["Customer Name"].nunique())

        # Loss by Category
        loss_by_cat = (
            loss_df.groupby("Category")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_by_cat, "Category", "Profit", "Loss by Category"),
            use_container_width=True
        )

        # Loss by Sub-Category
        loss_by_subcat = (
            loss_df.groupby("Sub-Category")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(10)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_by_subcat, "Sub-Category", "Profit", "Top 10 Loss-Making Sub-Categories"),
            use_container_width=True
        )

        # Loss by Region
        loss_by_region = (
            loss_df.groupby("Region")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_by_region, "Region", "Profit", "Loss by Region"),
            use_container_width=True
        )

        # Loss by State (Top 10)
        loss_by_state = (
            loss_df.groupby("State")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(10)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_by_state, "State", "Profit", "Top 10 Loss-Making States"),
            use_container_width=True
        )

        # Top Loss-Making Products
        loss_products = (
            loss_df.groupby("Product Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(10)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_products, "Product Name", "Profit", "Top 10 Loss-Making Products"),
            use_container_width=True
        )

        # Top Loss-Making Customers
        loss_customers = (
            loss_df.groupby("Customer Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(10)
        )
        st.plotly_chart(
            horizontal_bar_chart(loss_customers, "Customer Name", "Profit", "Top 10 Loss-Making Customers"),
            use_container_width=True
        )

        # Loss Details Table
        st.subheader("Loss Details (All Loss Orders)")
        st.dataframe(
            loss_df[["Order ID", "Order Date", "Product Name", "Category", "Customer Name", "Sales", "Profit", "Discount"]]
            .sort_values("Profit", ascending=True),
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Loss Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())
    raise