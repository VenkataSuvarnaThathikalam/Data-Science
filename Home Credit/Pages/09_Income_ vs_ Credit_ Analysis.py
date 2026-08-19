import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Income vs Credit Analysis")
st.caption("Determine whether applicants are borrowing proportionally to their income and how this affects default risk.")

try:
    df = load_home_credit_data()
    required = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET", "CODE_GENDER", "NAME_EDUCATION_TYPE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["CREDIT_TO_INCOME_RATIO"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    df["RISK_GROUP"] = pd.cut(
        df["CREDIT_TO_INCOME_RATIO"],
        bins=[0, 2, 4, 6, float("inf")],
        labels=["Low", "Moderate", "High", "Very High"],
        right=False,
    )

    st.sidebar.subheader("Filters")
    gender_options = sorted(df["CODE_GENDER"].dropna().unique().tolist())
    selected_genders = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
    filtered_df = df[df["CODE_GENDER"].isin(selected_genders)].copy()

    st.subheader("📊 Key charts")

    c1, c2, c3 = st.columns(3)
    c1.metric("Average Credit-to-Income Ratio", f"{filtered_df['CREDIT_TO_INCOME_RATIO'].mean():.2f}")
    c2.metric("Highest Ratio", f"{filtered_df['CREDIT_TO_INCOME_RATIO'].max():.2f}")
    c3.metric("Default Rate for High Ratio Customers", f"{filtered_df.loc[filtered_df['CREDIT_TO_INCOME_RATIO']>4, 'TARGET'].mean()*100:.2f}%")

    st.subheader("📈 Visualizations")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_scatter = px.scatter(filtered_df, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", title="Income vs Credit Scatter Plot", opacity=0.5, color="RISK_GROUP", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        ratio_hist = px.histogram(filtered_df, x="CREDIT_TO_INCOME_RATIO", nbins=40, title="Credit/Income Ratio Distribution", color_discrete_sequence=["#f59e0b"])
        st.plotly_chart(ratio_hist, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        ratio_default = filtered_df.groupby("RISK_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
        ratio_default["Default Rate"] = (ratio_default["Defaults"] / ratio_default["Customers"] * 100).round(2)
        fig_rate = px.bar(ratio_default, x="RISK_GROUP", y="Default Rate", title="Default Rate vs Credit/Income Ratio", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_rate, use_container_width=True)
    with c4:
        gender_ratio = filtered_df.groupby("CODE_GENDER", as_index=False)["CREDIT_TO_INCOME_RATIO"].mean().rename(columns={"CREDIT_TO_INCOME_RATIO": "Avg Ratio"})
        fig_gender = px.bar(gender_ratio, x="CODE_GENDER", y="Avg Ratio", title="Gender-wise Credit/Income Ratio", text="Avg Ratio", color="CODE_GENDER", color_discrete_sequence=["#3b82f6", "#ec4899"])
        st.plotly_chart(fig_gender, use_container_width=True)

    edu_ratio = filtered_df.groupby("NAME_EDUCATION_TYPE", as_index=False)["CREDIT_TO_INCOME_RATIO"].mean().rename(columns={"CREDIT_TO_INCOME_RATIO": "Avg Ratio"})
    fig_edu = px.bar(edu_ratio, x="NAME_EDUCATION_TYPE", y="Avg Ratio", title="Education-wise Credit/Income Ratio", text="Avg Ratio", color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_edu, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)