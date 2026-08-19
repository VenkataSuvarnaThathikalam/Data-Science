import sys
from pathlib import Path
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from utils.page_helpers import load_superstore_data, empty_state
from utils.filters import sidebar_filters, apply_filters
from utils.kpis import get_growth_metrics
from utils.charts import line_chart, multi_line_chart

st.set_page_config(page_title="Growth Analysis")
st.title("Sales Growth Analysis")

try:
    df = load_superstore_data()

    filters = sidebar_filters(df)
    df_filtered = apply_filters(df, filters)

    if df_filtered.empty:
        empty_state()
    else:
        growth_df = get_growth_metrics(df_filtered)

        if growth_df.empty:
            st.warning("No growth data available for the selected filters.")
            st.stop()

        # Normalize date columns to real timestamps to avoid PeriodIndex resample errors
        if "YearMonth" in growth_df.columns:
            growth_df["YearMonth"] = pd.to_datetime(growth_df["YearMonth"].astype(str))

        # Monthly growth
        monthly = growth_df.copy()
        monthly["YearMonth"] = pd.to_datetime(monthly["YearMonth"])
        monthly["Sales_Growth_%"] = monthly["Sales"].pct_change() * 100
        monthly["Profit_Growth_%"] = monthly["Profit"].pct_change() * 100

        # Quarterly growth
        df_q = df_filtered.copy()
        df_q["Order Date"] = pd.to_datetime(df_q["Order Date"])
        df_q["Quarter"] = df_q["Order Date"].dt.to_period("Q").dt.to_timestamp()
        quarterly = (
            df_q.groupby("Quarter")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
            .reset_index()
        )
        quarterly["Sales_Growth_%"] = quarterly["Sales"].pct_change() * 100
        quarterly["Profit_Growth_%"] = quarterly["Profit"].pct_change() * 100

        # Yearly growth
        df_y = df_filtered.copy()
        df_y["Order Date"] = pd.to_datetime(df_y["Order Date"])
        df_y["Year"] = pd.to_datetime(df_y["Order Date"].dt.strftime("%Y-01-01"))
        yearly = (
            df_y.groupby("Year")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
            .reset_index()
        )
        yearly["Sales_Growth_%"] = yearly["Sales"].pct_change() * 100
        yearly["Profit_Growth_%"] = yearly["Profit"].pct_change() * 100

        current_month = monthly.iloc[-1] if not monthly.empty else None
        current_quarter = quarterly.iloc[-1] if not quarterly.empty else None
        current_year = yearly.iloc[-1] if not yearly.empty else None

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "Month-over-Month Growth %",
            f"{current_month['Sales_Growth_%']:.2f}%" if current_month is not None and pd.notna(current_month["Sales_Growth_%"]) else "N/A",
        )
        col2.metric(
            "Quarter-over-Quarter Growth %",
            f"{current_quarter['Sales_Growth_%']:.2f}%" if current_quarter is not None and pd.notna(current_quarter["Sales_Growth_%"]) else "N/A",
        )
        col3.metric(
            "Year-over-Year Growth %",
            f"{current_year['Sales_Growth_%']:.2f}%" if current_year is not None and pd.notna(current_year["Sales_Growth_%"]) else "N/A",
        )
        col4.metric(
            "Profit Growth %",
            f"{current_year['Profit_Growth_%']:.2f}%" if current_year is not None and pd.notna(current_year["Profit_Growth_%"]) else "N/A",
        )

        st.subheader("Monthly Growth %")
        st.plotly_chart(
            line_chart(monthly, "YearMonth", "Sales_Growth_%", "Monthly Sales Growth %", freq="MS"),
            use_container_width=True,
        )

        st.subheader("Quarterly Growth %")
        st.plotly_chart(
            line_chart(quarterly, "Quarter", "Sales_Growth_%", "Quarterly Sales Growth %", freq="QS"),
            use_container_width=True,
        )

        st.subheader("Yearly Growth %")
        st.plotly_chart(
            line_chart(yearly, "Year", "Sales_Growth_%", "Yearly Sales Growth %", freq="YS"),
            use_container_width=True,
        )

        st.subheader("Sales Growth vs Profit Growth")
        growth_comparison = yearly[["Year", "Sales_Growth_%", "Profit_Growth_%"]].copy()
        st.plotly_chart(
            multi_line_chart(
                growth_comparison,
                "Year",
                ["Sales_Growth_%", "Profit_Growth_%"],
                "Sales Growth vs Profit Growth",
            ),
            use_container_width=True,
        )

        st.subheader("Growth Summary")
        st.dataframe(
            yearly.rename(columns={"Sales_Growth_%": "Sales Growth %", "Profit_Growth_%": "Profit Growth %"}),
            use_container_width=True,
            hide_index=True,
        )

except FileNotFoundError as e:
    st.error(f"Dataset file not found: {e}")
    st.code(str(e))
except Exception as e:
    st.error(f"Error in Growth Analysis: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())