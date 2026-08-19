import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("External Credit Score Analysis")
st.caption("Analyze external credit scores and evaluate their relationship with default risk.")

try:
    df = load_home_credit_data()
    required = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "TARGET"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["AVG_EXTERNAL_SCORE"] = df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)

    st.sidebar.subheader("Filters")
    target_filter = st.sidebar.multiselect("Target", sorted(df["TARGET"].dropna().unique().tolist()), default=sorted(df["TARGET"].dropna().unique().tolist()))
    filtered_df = df[df["TARGET"].isin(target_filter)].copy()

    st.subheader("📊 Key charts")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average EXT_SOURCE_1", f"{filtered_df['EXT_SOURCE_1'].mean():.3f}")
    c2.metric("Average EXT_SOURCE_2", f"{filtered_df['EXT_SOURCE_2'].mean():.3f}")
    c3.metric("Average EXT_SOURCE_3", f"{filtered_df['EXT_SOURCE_3'].mean():.3f}")
    c4.metric("Missing External Score Records", f"{filtered_df[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].isnull().sum().sum():,}")

    st.subheader("📈 Visualizations")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.histogram(filtered_df, x="EXT_SOURCE_1", nbins=30, title="EXT_SOURCE_1 Distribution", color_discrete_sequence=["#3b82f6"])
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.histogram(filtered_df, x="EXT_SOURCE_2", nbins=30, title="EXT_SOURCE_2 Distribution", color_discrete_sequence=["#10b981"])
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.histogram(filtered_df, x="EXT_SOURCE_3", nbins=30, title="EXT_SOURCE_3 Distribution", color_discrete_sequence=["#f59e0b"])
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.histogram(filtered_df, x="AVG_EXTERNAL_SCORE", nbins=30, title="Average External Score Distribution", color_discrete_sequence=["#8b5cf6"])
        st.plotly_chart(fig4, use_container_width=True)

    score_by_target = filtered_df.groupby("TARGET")[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].mean().reset_index()
    score_by_target["TARGET"] = score_by_target["TARGET"].map({0: "Non-Default", 1: "Default"})
    fig5 = px.bar(score_by_target, x="TARGET", y=["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"], title="External Scores by TARGET", barmode="group")
    st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.box(filtered_df, x="TARGET", y="AVG_EXTERNAL_SCORE", title="Average External Score by TARGET", color="TARGET", color_discrete_sequence=["#22c55e", "#ef4444"])
    st.plotly_chart(fig6, use_container_width=True)

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)