import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Income Analysis")
st.caption("Understand customer income levels and their relationship with default risk.")

try:
    df = load_home_credit_data()
    required = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "TARGET", "NAME_EDUCATION_TYPE", "OCCUPATION_TYPE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["INCOME_GROUP"] = pd.cut(
        df["AMT_INCOME_TOTAL"],
        bins=[0, 50000, 100000, 150000, 200000, 300000, 500000, float("inf")],
        labels=["<50K", "50K-100K", "100K-150K", "150K-200K", "200K-300K", "300K-500K", ">500K"],
        right=False,
    )

    st.sidebar.subheader("Filters")
    education_options = sorted(df["NAME_EDUCATION_TYPE"].dropna().unique().tolist())
    selected_education = st.sidebar.multiselect("Education", education_options, default=education_options)
    filtered_df = df[df["NAME_EDUCATION_TYPE"].isin(selected_education)].copy()

    st.subheader("📊 Key charts")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Income", f"${filtered_df['AMT_INCOME_TOTAL'].sum():,.0f}")
    c2.metric("Average Income", f"${filtered_df['AMT_INCOME_TOTAL'].mean():,.0f}")
    c3.metric("Median Income", f"${filtered_df['AMT_INCOME_TOTAL'].median():,.0f}")
    c4.metric("Maximum Income", f"${filtered_df['AMT_INCOME_TOTAL'].max():,.0f}")
    c5.metric("Average Income of Defaulters", f"${filtered_df.loc[filtered_df['TARGET']==1, 'AMT_INCOME_TOTAL'].mean():,.0f}")

    st.subheader("📈 Visualizations")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(filtered_df, x="AMT_INCOME_TOTAL", nbins=40, title="Income Distribution", color_discrete_sequence=["#10b981"])
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        income_group = filtered_df["INCOME_GROUP"].astype(str).value_counts().reindex(["<50K", "50K-100K", "100K-150K", "150K-200K", "200K-300K", "300K-500K", ">500K"], fill_value=0).reset_index()
        income_group.columns = ["Income Group", "Customers"]
        fig_group = px.bar(income_group, x="Income Group", y="Customers", title="Customers by Income Group", text="Customers", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_group, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        default_by_income = filtered_df.groupby("INCOME_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
        default_by_income["INCOME_GROUP"] = default_by_income["INCOME_GROUP"].astype(str)
        default_by_income["Default Rate"] = (default_by_income["Defaults"] / default_by_income["Customers"] * 100).round(2)
        default_by_income = default_by_income.set_index("INCOME_GROUP").reindex(["<50K", "50K-100K", "100K-150K", "150K-200K", "200K-300K", "300K-500K", ">500K"], fill_value=0).reset_index().rename(columns={"index": "INCOME_GROUP"})
        fig_def = px.bar(default_by_income, x="INCOME_GROUP", y="Default Rate", title="Default Rate by Income Group", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_def, use_container_width=True)
    with c4:
        income_credit = filtered_df[["AMT_INCOME_TOTAL", "AMT_CREDIT"]].dropna()
        fig_scatter = px.scatter(income_credit, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", title="Income vs Credit", opacity=0.6, color_discrete_sequence=["#8b5cf6"])
        st.plotly_chart(fig_scatter, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        annuity_income = filtered_df[["AMT_INCOME_TOTAL", "AMT_ANNUITY"]].dropna()
        fig_annuity = px.scatter(annuity_income, x="AMT_INCOME_TOTAL", y="AMT_ANNUITY", title="Income vs Annuity", opacity=0.6, color_discrete_sequence=["#f97316"])
        st.plotly_chart(fig_annuity, use_container_width=True)
    with c6:
        educ_income = filtered_df.groupby("NAME_EDUCATION_TYPE", as_index=False)["AMT_INCOME_TOTAL"].mean().rename(columns={"AMT_INCOME_TOTAL": "Average Income"})
        fig_education = px.bar(educ_income, x="NAME_EDUCATION_TYPE", y="Average Income", title="Income by Education", text="Average Income", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_education, use_container_width=True)

    occ_income = filtered_df.groupby("OCCUPATION_TYPE", as_index=False)["AMT_INCOME_TOTAL"].mean().rename(columns={"AMT_INCOME_TOTAL": "Average Income"})
    fig_occ = px.bar(occ_income, x="OCCUPATION_TYPE", y="Average Income", title="Income by Occupation", text="Average Income", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_occ, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)