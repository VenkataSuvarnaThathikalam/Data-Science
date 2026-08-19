import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Employment Analysis")
st.caption("Understand how employment status and work history relate to credit risk.")

try:
    df = load_home_credit_data()
    required = ["DAYS_EMPLOYED", "NAME_INCOME_TYPE", "OCCUPATION_TYPE", "ORGANIZATION_TYPE", "TARGET"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["EMPLOYMENT_YEARS"] = (df["DAYS_EMPLOYED"].replace({365243: pd.NA}).abs() / 365).round(1)
    df["EMPLOYMENT_GROUP"] = pd.cut(df["EMPLOYMENT_YEARS"], bins=[0, 2, 5, 10, 20, 40, float("inf")], labels=["<2", "2-5", "5-10", "10-20", "20-40", ">40"], right=False)

    st.sidebar.subheader("Filters")
    income_types = sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect("Income Type", income_types, default=income_types)
    filtered_df = df[df["NAME_INCOME_TYPE"].isin(selected_types)].copy()

    st.subheader("📊 Key charts")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Employment Years", f"{filtered_df['EMPLOYMENT_YEARS'].mean():.1f} years")
    c2.metric("Most Common Occupation", filtered_df["OCCUPATION_TYPE"].mode().iloc[0] if not filtered_df["OCCUPATION_TYPE"].empty else "N/A")
    c3.metric("Most Common Income Type", filtered_df["NAME_INCOME_TYPE"].mode().iloc[0] if not filtered_df["NAME_INCOME_TYPE"].empty else "N/A")
    c4.metric("Highest Risk Occupation", filtered_df.groupby("OCCUPATION_TYPE")["TARGET"].mean().idxmax() if not filtered_df.empty else "N/A")

    st.subheader("📈 Visualizations")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(filtered_df, x="EMPLOYMENT_YEARS", nbins=30, title="Employment Years Distribution", color_discrete_sequence=["#8b5cf6"])
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        emp_default = filtered_df.groupby("EMPLOYMENT_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
        emp_default["Default Rate"] = (emp_default["Defaults"] / emp_default["Customers"] * 100).round(2)
        fig_emp_default = px.bar(emp_default, x="EMPLOYMENT_GROUP", y="Default Rate", title="Default Rate by Employment Years", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_emp_default, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        income_type_counts = filtered_df["NAME_INCOME_TYPE"].value_counts().reset_index()
        income_type_counts.columns = ["Income Type", "Applications"]
        fig_income_type = px.bar(income_type_counts, x="Income Type", y="Applications", title="Applications by Income Type", text="Applications", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_income_type, use_container_width=True)
    with c4:
        income_default = filtered_df.groupby("NAME_INCOME_TYPE", as_index=False)["TARGET"].mean().rename(columns={"TARGET": "Default Rate"})
        fig_income_default = px.bar(income_default, x="NAME_INCOME_TYPE", y="Default Rate", title="Default Rate by Income Type", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_income_default, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        occ_counts = filtered_df["OCCUPATION_TYPE"].value_counts().reset_index().head(10)
        occ_counts.columns = ["Occupation", "Applications"]
        fig_occ = px.bar(occ_counts, x="Occupation", y="Applications", title="Applications by Occupation", text="Applications", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_occ, use_container_width=True)
    with c6:
        occ_default = filtered_df.groupby("OCCUPATION_TYPE", as_index=False)["TARGET"].mean().rename(columns={"TARGET": "Default Rate"})
        fig_occ_default = px.bar(occ_default, x="OCCUPATION_TYPE", y="Default Rate", title="Default Rate by Occupation", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig_occ_default, use_container_width=True)

    org_default = filtered_df.groupby("ORGANIZATION_TYPE", as_index=False)["TARGET"].mean().rename(columns={"TARGET": "Default Rate"})
    fig_org = px.bar(org_default, x="ORGANIZATION_TYPE", y="Default Rate", title="Default Rate by Organization Type", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_org, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)