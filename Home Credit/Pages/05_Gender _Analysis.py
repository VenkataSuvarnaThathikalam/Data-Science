import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Gender Analysis")
st.caption("Compare loan characteristics and credit risk between male and female applicants.")

try:
    df = load_home_credit_data()
    required = ["CODE_GENDER", "TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    filtered_df = df.copy()
    st.sidebar.subheader("Filters")
    gender_options = sorted(filtered_df["CODE_GENDER"].dropna().unique().tolist())
    selected_genders = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
    filtered_df = filtered_df[filtered_df["CODE_GENDER"].isin(selected_genders)]

    gender_summary = filtered_df.groupby("CODE_GENDER").agg(
        Customers=("TARGET", "count"),
        Defaults=("TARGET", "sum"),
        Avg_Income=("AMT_INCOME_TOTAL", "mean"),
        Avg_Credit=("AMT_CREDIT", "mean"),
    ).reset_index()
    gender_summary["Default Rate"] = (gender_summary["Defaults"] / gender_summary["Customers"] * 100).round(2)

    male_apps = int(gender_summary.loc[gender_summary["CODE_GENDER"] == "M", "Customers"].sum()) if "M" in gender_summary["CODE_GENDER"].values else 0
    female_apps = int(gender_summary.loc[gender_summary["CODE_GENDER"] == "F", "Customers"].sum()) if "F" in gender_summary["CODE_GENDER"].values else 0
    male_default_rate = float(gender_summary.loc[gender_summary["CODE_GENDER"] == "M", "Default Rate"].mean()) if "M" in gender_summary["CODE_GENDER"].values else 0
    female_default_rate = float(gender_summary.loc[gender_summary["CODE_GENDER"] == "F", "Default Rate"].mean()) if "F" in gender_summary["CODE_GENDER"].values else 0

    st.subheader("📊 Key charts")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Male Applicants", f"{male_apps:,}")
    c2.metric("Female Applicants", f"{female_apps:,}")
    c3.metric("Male Default Rate", f"{male_default_rate:.2f}%")
    c4.metric("Female Default Rate", f"{female_default_rate:.2f}%")

    st.subheader("📈 Visualizations")
    
    chart1, chart2 = st.columns(2)
    with chart1:
        fig1 = px.bar(gender_summary, x="CODE_GENDER", y="Customers", title="Applicants by Gender", text="Customers", color="CODE_GENDER", color_discrete_sequence=["#3b82f6", "#ec4899"])
        st.plotly_chart(fig1, use_container_width=True)
    with chart2:
        fig2 = px.bar(gender_summary, x="CODE_GENDER", y="Defaults", title="Default Customers by Gender", text="Defaults", color="CODE_GENDER", color_discrete_sequence=["#60a5fa", "#f472b6"])
        st.plotly_chart(fig2, use_container_width=True)

    chart3, chart4, chart5 = st.columns(3)
    with chart3:
        fig3 = px.bar(gender_summary, x="CODE_GENDER", y="Default Rate", title="Default Rate by Gender", text="Default Rate", color="CODE_GENDER", color_discrete_sequence=["#93c5fd", "#f9a8d4"])
        st.plotly_chart(fig3, use_container_width=True)
    with chart4:
        fig4 = px.bar(gender_summary, x="CODE_GENDER", y="Avg_Income", title="Average Income by Gender", text="Avg_Income", color="CODE_GENDER", color_discrete_sequence=["#0ea5e9", "#f43f5e"])
        st.plotly_chart(fig4, use_container_width=True)
    with chart5:
        fig5 = px.bar(gender_summary, x="CODE_GENDER", y="Avg_Credit", title="Average Credit by Gender", text="Avg_Credit", color="CODE_GENDER", color_discrete_sequence=["#8b5cf6", "#f97316"])
        st.plotly_chart(fig5, use_container_width=True)

    annuity_summary = filtered_df.groupby("CODE_GENDER", as_index=False)["AMT_ANNUITY"].mean().rename(columns={"AMT_ANNUITY": "Avg_Annuity"})
    fig6 = px.bar(annuity_summary, x="CODE_GENDER", y="Avg_Annuity", title="Average Annuity by Gender", text="Avg_Annuity", color="CODE_GENDER", color_discrete_sequence=["#22c55e", "#f59e0b"])
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Gender Comparison Table")
    table = gender_summary[["CODE_GENDER", "Customers", "Defaults", "Default Rate", "Avg_Income", "Avg_Credit"]].copy()
    table["Avg_Income"] = table["Avg_Income"].map("${:,.0f}".format)
    table["Avg_Credit"] = table["Avg_Credit"].map("${:,.0f}".format)
    table["Default Rate"] = table["Default Rate"].map("{:.2f}%".format)
    st.dataframe(table, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)