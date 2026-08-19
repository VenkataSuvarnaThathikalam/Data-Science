import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Annuity Burden Analysis")
st.caption("Understand repayment burden relative to income and how it relates to default risk.")

try:
    df = load_home_credit_data()
    required = ["AMT_ANNUITY", "AMT_INCOME_TOTAL", "TARGET", "CODE_GENDER", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["ANNUITY_TO_INCOME_RATIO"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    df["RISK_GROUP"] = pd.cut(
        df["ANNUITY_TO_INCOME_RATIO"],
        bins=[0, 0.1, 0.2, 0.3, float("inf")],
        labels=["Low", "Medium", "High", "Very High"],
        right=False,
    )

    st.sidebar.subheader("Filters")
    income_types = sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect("Income Type", income_types, default=income_types)
    filtered_df = df[df["NAME_INCOME_TYPE"].isin(selected_types)].copy()

    st.subheader("📊 Key charts")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Ratio", f"{filtered_df['ANNUITY_TO_INCOME_RATIO'].mean():.3f}")
    c2.metric("Median Ratio", f"{filtered_df['ANNUITY_TO_INCOME_RATIO'].median():.3f}")
    c3.metric("Max Ratio", f"{filtered_df['ANNUITY_TO_INCOME_RATIO'].max():.3f}")
    c4.metric("High Burden Customers", f"{(filtered_df['ANNUITY_TO_INCOME_RATIO'] > 0.2).sum():,}")

    st.subheader("📈 Visualizations")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(filtered_df, x="ANNUITY_TO_INCOME_RATIO", nbins=40, title="Annuity-to-Income Distribution", color_discrete_sequence=["#10b981"])
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        burden_default = filtered_df.groupby("RISK_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
        burden_default["Default Rate"] = (burden_default["Defaults"] / burden_default["Customers"] * 100).round(2)
        fig_default = px.bar(burden_default, x="RISK_GROUP", y="Default Rate", title="Default Rate by Ratio Group", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_default, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        gender_ratio = filtered_df.groupby("CODE_GENDER", as_index=False)["ANNUITY_TO_INCOME_RATIO"].mean().rename(columns={"ANNUITY_TO_INCOME_RATIO": "Avg Ratio"})
        fig_gender = px.bar(gender_ratio, x="CODE_GENDER", y="Avg Ratio", title="Ratio by Gender", text="Avg Ratio", color="CODE_GENDER", color_discrete_sequence=["#3b82f6", "#ec4899"])
        st.plotly_chart(fig_gender, use_container_width=True)
    with c4:
        income_ratio = filtered_df.groupby("NAME_INCOME_TYPE", as_index=False)["ANNUITY_TO_INCOME_RATIO"].mean().rename(columns={"ANNUITY_TO_INCOME_RATIO": "Avg Ratio"})
        fig_income = px.bar(income_ratio, x="NAME_INCOME_TYPE", y="Avg Ratio", title="Ratio by Income Type", text="Avg Ratio", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_income, use_container_width=True)

    edu_ratio = filtered_df.groupby("NAME_EDUCATION_TYPE", as_index=False)["ANNUITY_TO_INCOME_RATIO"].mean().rename(columns={"ANNUITY_TO_INCOME_RATIO": "Avg Ratio"})
    fig_edu = px.bar(edu_ratio, x="NAME_EDUCATION_TYPE", y="Avg Ratio", title="Ratio by Education", text="Avg Ratio", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_edu, use_container_width=True)

    ratio_target = filtered_df.groupby("TARGET", as_index=False)["ANNUITY_TO_INCOME_RATIO"].mean().rename(columns={"ANNUITY_TO_INCOME_RATIO": "Avg Ratio"})
    ratio_target["TARGET"] = ratio_target["TARGET"].map({0: "Non-Default", 1: "Default"})
    fig_target = px.bar(ratio_target, x="TARGET", y="Avg Ratio", title="Ratio vs TARGET", text="Avg Ratio", color="TARGET", color_discrete_sequence=["#22c55e", "#ef4444"])
    st.plotly_chart(fig_target, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)