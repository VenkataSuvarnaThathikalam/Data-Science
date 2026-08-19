import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Education Analysis")
st.caption("Analyze loan demand, income levels, and default behavior by education group.")

try:
    df = load_home_credit_data()
    required = ["NAME_EDUCATION_TYPE", "TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["CREDIT_TO_INCOME_RATIO"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)

    st.sidebar.subheader("Filters")
    education_options = sorted(df["NAME_EDUCATION_TYPE"].dropna().unique().tolist())
    selected_education = st.sidebar.multiselect("Education", education_options, default=education_options)
    filtered_df = df[df["NAME_EDUCATION_TYPE"].isin(selected_education)].copy()

    edu_summary = filtered_df.groupby("NAME_EDUCATION_TYPE").agg(
        Customers=("TARGET", "count"),
        Defaults=("TARGET", "sum"),
        Avg_Income=("AMT_INCOME_TOTAL", "mean"),
        Avg_Credit=("AMT_CREDIT", "mean"),
        Avg_Annuity=("AMT_ANNUITY", "mean"),
        Avg_CTI=("CREDIT_TO_INCOME_RATIO", "mean"),
    ).reset_index()
    edu_summary["Default Rate"] = (edu_summary["Defaults"] / edu_summary["Customers"] * 100).round(2)

    st.subheader("📊 Key charts")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Most Common Education", edu_summary.sort_values("Customers", ascending=False)["NAME_EDUCATION_TYPE"].iloc[0])
    c2.metric("Highest Income Education Group", edu_summary.sort_values("Avg_Income", ascending=False)["NAME_EDUCATION_TYPE"].iloc[0])
    c3.metric("Lowest Default Education Group", edu_summary.sort_values("Default Rate", ascending=True)["NAME_EDUCATION_TYPE"].iloc[0])
    c4.metric("Highest Default Education Group", edu_summary.sort_values("Default Rate", ascending=False)["NAME_EDUCATION_TYPE"].iloc[0])

    st.subheader("📈 Visualizations")

    c1, c2 = st.columns(2)
    with c1:
        fig_customers = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Customers", title="Customers by Education", text="Customers", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_customers, use_container_width=True)
    with c2:
        fig_default = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Default Rate", title="Default Rate by Education", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_default, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_income = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Avg_Income", title="Income by Education", text="Avg_Income", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_income, use_container_width=True)
    with c4:
        fig_credit = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Avg_Credit", title="Credit by Education", text="Avg_Credit", color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_credit, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        fig_annuity = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Avg_Annuity", title="Annuity by Education", text="Avg_Annuity", color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_annuity, use_container_width=True)
    with c6:
        fig_cti = px.bar(edu_summary, x="NAME_EDUCATION_TYPE", y="Avg_CTI", title="Credit-to-Income Ratio by Education", text="Avg_CTI", color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig_cti, use_container_width=True)

    st.subheader("Education Comparison Table")
    table = edu_summary[["NAME_EDUCATION_TYPE", "Customers", "Defaults", "Default Rate", "Avg_Income", "Avg_Credit"]].copy()
    table["Avg_Income"] = table["Avg_Income"].map("${:,.0f}".format)
    table["Avg_Credit"] = table["Avg_Credit"].map("${:,.0f}".format)
    table["Default Rate"] = table["Default Rate"].map("{:.2f}%".format)
    st.dataframe(table, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)