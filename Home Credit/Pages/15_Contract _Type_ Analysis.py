import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Contract Type Analysis")
st.caption("Analyze credit applications by loan contract type and compare default behavior across contracts.")

try:
    df = load_home_credit_data()
    required = ["NAME_CONTRACT_TYPE", "TARGET", "AMT_CREDIT", "AMT_INCOME_TOTAL", "AMT_ANNUITY"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["CREDIT_TO_INCOME_RATIO"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)

    st.sidebar.subheader("Filters")
    contract_types = sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist())
    selected_contracts = st.sidebar.multiselect("Contract Type", contract_types, default=contract_types)
    filtered_df = df[df["NAME_CONTRACT_TYPE"].isin(selected_contracts)].copy()

    contract_summary = filtered_df.groupby("NAME_CONTRACT_TYPE").agg(
        Customers=("TARGET", "count"),
        Defaults=("TARGET", "sum"),
        Avg_Credit=("AMT_CREDIT", "mean"),
        Avg_Income=("AMT_INCOME_TOTAL", "mean"),
        Avg_Annuity=("AMT_ANNUITY", "mean"),
        Avg_CTI=("CREDIT_TO_INCOME_RATIO", "mean"),
    ).reset_index()
    contract_summary["Default Rate"] = (contract_summary["Defaults"] / contract_summary["Customers"] * 100).round(2)

    st.subheader("📊 Key charts")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash Loan Applications", f"{contract_summary.loc[contract_summary['NAME_CONTRACT_TYPE']=='Cash loans', 'Customers'].sum() if 'Cash loans' in contract_summary['NAME_CONTRACT_TYPE'].values else 0:,}")
    c2.metric("Revolving Loan Applications", f"{contract_summary.loc[contract_summary['NAME_CONTRACT_TYPE']=='Revolving loans', 'Customers'].sum() if 'Revolving loans' in contract_summary['NAME_CONTRACT_TYPE'].values else 0:,}")
    c3.metric("Cash Loan Default Rate", f"{contract_summary.loc[contract_summary['NAME_CONTRACT_TYPE']=='Cash loans', 'Default Rate'].mean() if 'Cash loans' in contract_summary['NAME_CONTRACT_TYPE'].values else 0:.2f}%")
    c4.metric("Revolving Loan Default Rate", f"{contract_summary.loc[contract_summary['NAME_CONTRACT_TYPE']=='Revolving loans', 'Default Rate'].mean() if 'Revolving loans' in contract_summary['NAME_CONTRACT_TYPE'].values else 0:.2f}%")

    st.subheader("📈 Visualizations")
    
    c1, c2 = st.columns(2)
    with c1:
        app_count = filtered_df["NAME_CONTRACT_TYPE"].value_counts().reset_index()
        app_count.columns = ["Contract Type", "Applications"]
        fig_apps = px.bar(app_count, x="Contract Type", y="Applications", title="Applications by Contract Type", text="Applications", color_discrete_sequence=["#3b82f6", "#f97316"])
        st.plotly_chart(fig_apps, use_container_width=True)
    with c2:
        fig_default = px.bar(contract_summary, x="NAME_CONTRACT_TYPE", y="Default Rate", title="Default Rate by Contract Type", text="Default Rate", color_discrete_sequence=["#93c5fd", "#fdba74"])
        st.plotly_chart(fig_default, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_credit = px.bar(contract_summary, x="NAME_CONTRACT_TYPE", y="Avg_Credit", title="Average Credit by Contract Type", text="Avg_Credit", color_discrete_sequence=["#10b981", "#f59e0b"])
        st.plotly_chart(fig_credit, use_container_width=True)
    with c4:
        fig_income = px.bar(contract_summary, x="NAME_CONTRACT_TYPE", y="Avg_Income", title="Average Income by Contract Type", text="Avg_Income", color_discrete_sequence=["#8b5cf6", "#22c55e"])
        st.plotly_chart(fig_income, use_container_width=True)

    fig_annuity = px.bar(contract_summary, x="NAME_CONTRACT_TYPE", y="Avg_Annuity", title="Average Annuity by Contract Type", text="Avg_Annuity", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_annuity, use_container_width=True)

    fig_cti = px.bar(contract_summary, x="NAME_CONTRACT_TYPE", y="Avg_CTI", title="Credit-to-Income Ratio by Contract Type", text="Avg_CTI", color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_cti, use_container_width=True)

    st.subheader("Contract Comparison Table")
    table = contract_summary[["NAME_CONTRACT_TYPE", "Customers", "Defaults", "Default Rate", "Avg_Income", "Avg_Credit"]].copy()
    table["Avg_Income"] = table["Avg_Income"].map("${:,.0f}".format)
    table["Avg_Credit"] = table["Avg_Credit"].map("${:,.0f}".format)
    table["Default Rate"] = table["Default Rate"].map("{:.2f}%".format)
    st.dataframe(table, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)