import sys
from pathlib import Path
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.charts import bar_chart, horizontal_bar_chart

st.set_page_config(page_title="Top & Bottom Performers")
st.title("Top & Bottom Performers")

try:
    df = load_superstore_data()
    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        # --- Filters for Top & Bottom N ---
        n_options = [5, 10, 20]
        selected_top_n = st.selectbox("Select number of TOP items to display:", n_options, index=1)
        selected_bottom_n = st.selectbox("Select number of BOTTOM items to display:", n_options, index=1)

        # --- TOP PERFORMERS ---
        st.subheader("TOP PERFORMERS")

        top_prod_sales = (
            df_filtered.groupby("Product Name")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_prod_sales, "Product Name", "Sales", f"Top {selected_top_n} Products by Sales"),
            use_container_width=True
        )

        top_prod_profit = (
            df_filtered.groupby("Product Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_prod_profit, "Product Name", "Profit", f"Top {selected_top_n} Products by Profit"),
            use_container_width=True
        )

        top_cust_sales = (
            df_filtered.groupby("Customer Name")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_cust_sales, "Customer Name", "Sales", f"Top {selected_top_n} Customers by Sales"),
            use_container_width=True
        )

        top_cust_profit = (
            df_filtered.groupby("Customer Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_cust_profit, "Customer Name", "Profit", f"Top {selected_top_n} Customers by Profit"),
            use_container_width=True
        )

        top_state_sales = (
            df_filtered.groupby("State")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_state_sales, "State", "Sales", f"Top {selected_top_n} States by Sales"),
            use_container_width=True
        )

        top_city_sales = (
            df_filtered.groupby("City")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(selected_top_n)
        )
        st.plotly_chart(
            bar_chart(top_city_sales, "City", "Sales", f"Top {selected_top_n} Cities by Sales"),
            use_container_width=True
        )

        # --- BOTTOM PERFORMERS ---
        st.subheader("BOTTOM PERFORMERS")

        bottom_prod_profit = (
            df_filtered.groupby("Product Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(selected_bottom_n)
        )
        st.plotly_chart(
            horizontal_bar_chart(bottom_prod_profit, "Product Name", "Profit", f"Bottom {selected_bottom_n} Products by Profit"),
            use_container_width=True
        )

        bottom_cust_profit = (
            df_filtered.groupby("Customer Name")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(selected_bottom_n)
        )
        st.plotly_chart(
            horizontal_bar_chart(bottom_cust_profit, "Customer Name", "Profit", f"Bottom {selected_bottom_n} Customers by Profit"),
            use_container_width=True
        )

        bottom_state_profit = (
            df_filtered.groupby("State")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(selected_bottom_n)
        )
        st.plotly_chart(
            horizontal_bar_chart(bottom_state_profit, "State", "Profit", f"Bottom {selected_bottom_n} States by Profit"),
            use_container_width=True
        )

        bottom_city_profit = (
            df_filtered.groupby("City")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(selected_bottom_n)
        )
        st.plotly_chart(
            horizontal_bar_chart(bottom_city_profit, "City", "Profit", f"Bottom {selected_bottom_n} Cities by Profit"),
            use_container_width=True
        )

        bottom_subcat_profit = (
            df_filtered.groupby("Sub-Category")["Profit"]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
            .head(selected_bottom_n)
        )
        st.plotly_chart(
            horizontal_bar_chart(bottom_subcat_profit, "Sub-Category", "Profit", f"Bottom {selected_bottom_n} Sub-Categories by Profit"),
            use_container_width=True
        )

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Top & Bottom Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())
    raise
