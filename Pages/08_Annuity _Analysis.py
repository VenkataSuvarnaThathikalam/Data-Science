import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Annuity Analysis")
st.caption("Study customers' annual payment obligations and their effect on credit risk.")

try:
    df = load_home_credit_data()
    required = ["AMT_ANNUITY", "AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET", "NAME_INCOME_TYPE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    st.sidebar.subheader("Filters")
    selected_income_types = st.sidebar.multiselect("Income Type", sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist()))
    filtered_df = df[df["NAME_INCOME_TYPE"].isin(selected_income_types)].copy()

    st.subheader("📊 Key charts")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Annuity", f"${filtered_df['AMT_ANNUITY'].mean():,.0f}")
    c2.metric("Median Annuity", f"${filtered_df['AMT_ANNUITY'].median():,.0f}")
    c3.metric("Maximum Annuity", f"${filtered_df['AMT_ANNUITY'].max():,.0f}")
    c4.metric("Average Annuity for Defaulters", f"${filtered_df.loc[filtered_df['TARGET']==1, 'AMT_ANNUITY'].mean():,.0f}")

    st.subheader("📈 Visualizations")

    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(filtered_df, x="AMT_ANNUITY", nbins=40, title="Annuity Distribution", color_discrete_sequence=["#22c55e"])
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        fig_target = px.box(filtered_df, x="TARGET", y="AMT_ANNUITY", title="Annuity by TARGET", color="TARGET", color_discrete_sequence=["#16a34a", "#ef4444"], category_orders={"TARGET": [0, 1]})
        st.plotly_chart(fig_target, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_income = px.scatter(filtered_df, x="AMT_INCOME_TOTAL", y="AMT_ANNUITY", title="Annuity vs Income", opacity=0.5, color_discrete_sequence=["#0ea5e9"])
        st.plotly_chart(fig_income, use_container_width=True)
    with c4:
        fig_credit = px.scatter(filtered_df, x="AMT_CREDIT", y="AMT_ANNUITY", title="Annuity vs Credit", opacity=0.5, color_discrete_sequence=["#f97316"])
        st.plotly_chart(fig_credit, use_container_width=True)

    avg_annuity_income = filtered_df.groupby("NAME_INCOME_TYPE", as_index=False)["AMT_ANNUITY"].mean().rename(columns={"AMT_ANNUITY": "Average Annuity"})
    fig_income_type = px.bar(avg_annuity_income, x="NAME_INCOME_TYPE", y="Average Annuity", title="Average Annuity by Income Type", text="Average Annuity", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_income_type, use_container_width=True)

    annuity_groups = pd.cut(filtered_df["AMT_ANNUITY"], bins=[0, 10000, 20000, 30000, 40000, float("inf")], labels=["<10K", "10K-20K", "20K-30K", "30K-40K", ">40K"], right=False)
    annuity_summary = filtered_df.assign(ANN_GROUP=annuity_groups).groupby("ANN_GROUP", observed=False).agg(Customers=("TARGET", "count"), Defaults=("TARGET", "sum")).reset_index()
    annuity_summary["Default Rate"] = (annuity_summary["Defaults"] / annuity_summary["Customers"] * 100).round(2)
    fig_group = px.bar(annuity_summary, x="ANN_GROUP", y="Default Rate", title="Default Rate by Annuity Group", text="Default Rate", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_group, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)