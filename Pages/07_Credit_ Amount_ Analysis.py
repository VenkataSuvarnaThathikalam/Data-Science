import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Credit Amount Analysis")
st.caption("Analyze loan request sizes, credit demand, and default behavior across applicant segments.")

try:
    df = load_home_credit_data()
    required = ["AMT_CREDIT", "TARGET", "CODE_GENDER", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_CONTRACT_TYPE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["CREDIT_GROUP"] = pd.cut(
        df["AMT_CREDIT"],
        bins=[0, 100000, 300000, 500000, 700000, 1000000, float("inf")],
        labels=["<100K", "100K-300K", "300K-500K", "500K-700K", "700K-1M", ">1M"],
        right=False,
    )

    st.sidebar.subheader("Filters")
    selected_contracts = st.sidebar.multiselect("Contract Type", sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()))
    filtered_df = df[df["NAME_CONTRACT_TYPE"].isin(selected_contracts)].copy()

    st.subheader("📊 Key charts")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Credit", f"${filtered_df['AMT_CREDIT'].sum():,.0f}")
    c2.metric("Average Credit", f"${filtered_df['AMT_CREDIT'].mean():,.0f}")
    c3.metric("Median Credit", f"${filtered_df['AMT_CREDIT'].median():,.0f}")
    c4.metric("Maximum Credit", f"${filtered_df['AMT_CREDIT'].max():,.0f}")
    c5.metric("Minimum Credit", f"${filtered_df['AMT_CREDIT'].min():,.0f}")

    st.subheader("📈 Visualizations")

    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(filtered_df, x="AMT_CREDIT", nbins=40, title="Credit Amount Distribution", color_discrete_sequence=["#6366f1"])
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        target_credit = filtered_df.groupby("TARGET")["AMT_CREDIT"].mean().reset_index()
        target_credit["TARGET"] = target_credit["TARGET"].map({0: "Non-Default", 1: "Default"})
        fig_target = px.bar(target_credit, x="TARGET", y="AMT_CREDIT", title="Credit Amount by TARGET", text="AMT_CREDIT", color="TARGET", color_discrete_sequence=["#22c55e", "#ef4444"])
        st.plotly_chart(fig_target, use_container_width=True)

    c3, c4, c5 = st.columns(3)
    with c3:
        gender_credit = filtered_df.groupby("CODE_GENDER", as_index=False)["AMT_CREDIT"].mean().rename(columns={"AMT_CREDIT": "Average Credit"})
        fig_gender = px.bar(gender_credit, x="CODE_GENDER", y="Average Credit", title="Average Credit by Gender", text="Average Credit", color_discrete_sequence=["#3b82f6", "#ec4899"])
        st.plotly_chart(fig_gender, use_container_width=True)
    with c4:
        income_credit = filtered_df.groupby("NAME_INCOME_TYPE", as_index=False)["AMT_CREDIT"].mean().rename(columns={"AMT_CREDIT": "Average Credit"})
        fig_income = px.bar(income_credit, x="NAME_INCOME_TYPE", y="Average Credit", title="Credit by Income Type", text="Average Credit", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_income, use_container_width=True)
    with c5:
        education_credit = filtered_df.groupby("NAME_EDUCATION_TYPE", as_index=False)["AMT_CREDIT"].mean().rename(columns={"AMT_CREDIT": "Average Credit"})
        fig_education = px.bar(education_credit, x="NAME_EDUCATION_TYPE", y="Average Credit", title="Credit by Education", text="Average Credit", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_education, use_container_width=True)

    c6, c7 = st.columns(2)
    with c6:
        contract_credit = filtered_df.groupby("NAME_CONTRACT_TYPE", as_index=False)["AMT_CREDIT"].mean().rename(columns={"AMT_CREDIT": "Average Credit"})
        fig_contract = px.bar(contract_credit, x="NAME_CONTRACT_TYPE", y="Average Credit", title="Credit by Contract Type", text="Average Credit", color_discrete_sequence=["#14b8a6", "#f59e0b"])
        st.plotly_chart(fig_contract, use_container_width=True)
    with c7:
        credit_range = filtered_df.groupby("CREDIT_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
        credit_range["Default Rate"] = (credit_range["Defaults"] / credit_range["Customers"] * 100).round(2)
        fig_range = px.bar(credit_range, x="CREDIT_GROUP", y="Default Rate", title="Default Rate by Credit Range", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_range, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)