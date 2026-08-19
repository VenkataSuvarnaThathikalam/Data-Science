from pathlib import Path
import sys
import pandas as pd
import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from data_loader import load_data
    from filters import sidebar_filters, apply_filters
    from kpis import calc_kpis
else:
    from .data_loader import load_data
    from .filters import sidebar_filters, apply_filters
    from .kpis import calc_kpis


@st.cache_data
def load_home_credit_data() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parent.parent
    candidate_paths = [
        project_root / "data" / "application_train.csv",
        Path(r"C:\Users\tsuva\OneDrive\Desktop\Home Credit Default Risk-Application_train dashboard\data\application_train.csv"),
    ]

    for csv_path in candidate_paths:
        if csv_path.exists():
            df = load_data(csv_path)
            return df

    raise FileNotFoundError(
        "application_train.csv not found. Check the project data folder or the legacy path."
    )


def get_filtered_data() -> pd.DataFrame:
    df = load_home_credit_data()
    filters = sidebar_filters(df)
    return apply_filters(df, filters)


def display_metrics(df: pd.DataFrame, metrics: dict):
    cols = st.columns(4)
    cols[0].metric("Total Applications", f"{metrics['total_applications']:,}")
    cols[1].metric("Total Defaults", f"{metrics['total_defaults']:,}")
    cols[2].metric("Total Non-Defaults", f"{metrics['total_non_defaults']:,}")
    cols[3].metric("Default Rate %", f"{metrics['default_rate']:.2f}%")

    cols2 = st.columns(4)
    cols2[0].metric("Total Credit Amount", f"${metrics['total_credit']:,.0f}")
    cols2[1].metric("Average Credit", f"${metrics['avg_credit']:,.0f}")
    cols2[2].metric("Average Income", f"${metrics['avg_income']:,.0f}")
    cols2[3].metric("Average Annuity", f"${metrics['avg_annuity']:,.0f}")


def empty_state():
    st.warning("⚠️ No data is available for the selected filters. Adjust the filters and try again.")