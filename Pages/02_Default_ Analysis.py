import streamlit as st
import pandas as pd
import plotly.express as px
from utils.page_helpers import load_home_credit_data

st.header("📉 Default Analysis")
st.caption("Comprehensive analysis of the TARGET variable—focusing on default patterns, risk segments, and borrower profiles across the portfolio.")

try:
    df = load_home_credit_data()

    # KPIs
    total = len(df)
    defaults = df[df["TARGET"] == 1].shape[0]
    non_defaults = df[df["TARGET"] == 0].shape[0]
    default_rate = (defaults / total) * 100
    non_default_rate = (non_defaults / total) * 100

    st.subheader("🏆 KPI Cards")
    st.caption("These metrics summarize the main TARGET variable and default behavior across the entire applicant base.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TARGET = 0 Customers", f"{non_defaults:,}")
    col2.metric("TARGET = 1 Customers", f"{defaults:,}")
    col3.metric("Default Rate %", f"{default_rate:.2f}%")
    col4.metric("Non-Default Rate %", f"{non_default_rate:.2f}%")

    st.divider()

    # Charts
    st.subheader("📈 Default Patterns by Segment")
    st.caption("These visualizations break down default rates across different borrower dimensions to identify high-risk groups.")

    col1, col2 = st.columns(2)
    with col1:
        try:
            default_counts = df["TARGET"].value_counts().rename(index={0: "Non-Default", 1: "Default"}).reset_index()
            default_counts.columns = ["Status", "Count"]
            fig1 = px.bar(default_counts, x="Status", y="Count", title="Customer Count by Default Status",
                          color="Status", text="Count", color_discrete_sequence=["#14b8a6", "#f97316"])
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Default Counts chart: {str(e)}")
    
    with col2:
        try:
            default_dist = df["TARGET"].value_counts().rename(index={0: "Non-Default", 1: "Default"})
            fig2 = px.pie(names=default_dist.index, values=default_dist.values, title="Default Distribution %",
                          hole=0.45, color_discrete_sequence=["#14b8a6", "#f97316"])
            fig2.update_traces(textinfo="percent+label")
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Distribution Pie chart: {str(e)}")

    col3, col4 = st.columns(2)
    with col3:
        try:
            gender_default = df.groupby("CODE_GENDER")["TARGET"].agg(["count", "sum"]).reset_index()
            gender_default["default_rate"] = (gender_default["sum"] / gender_default["count"] * 100).round(2)
            gender_default = gender_default.rename(columns={"CODE_GENDER": "Gender", "default_rate": "Default Rate %"})
            fig3 = px.bar(gender_default, x="Gender", y="Default Rate %", title="Default Rate by Gender",
                          text="Default Rate %", color="Gender", color_discrete_sequence=px.colors.qualitative.Set2)
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Gender chart: {str(e)}")
    
    with col4:
        try:
            income_default = df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(["count", "sum"]).reset_index()
            income_default["default_rate"] = (income_default["sum"] / income_default["count"] * 100).round(2)
            income_default = income_default.sort_values("default_rate", ascending=False)
            income_default = income_default.rename(columns={"NAME_INCOME_TYPE": "Income Type", "default_rate": "Default Rate %"})
            fig4 = px.bar(income_default, x="Default Rate %", y="Income Type", orientation="h", title="Default Rate by Income Type",
                          text="Default Rate %", color="Income Type", color_discrete_sequence=px.colors.qualitative.Safe)
            fig4.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Income Type chart: {str(e)}")

    col5, col6 = st.columns(2)
    with col5:
        try:
            education_default = df.groupby("NAME_EDUCATION_TYPE")["TARGET"].agg(["count", "sum"]).reset_index()
            education_default["default_rate"] = (education_default["sum"] / education_default["count"] * 100).round(2)
            education_default = education_default.sort_values("default_rate", ascending=False)
            education_default = education_default.rename(columns={"NAME_EDUCATION_TYPE": "Education", "default_rate": "Default Rate %"})
            fig5 = px.bar(education_default, x="Default Rate %", y="Education", orientation="h", title="Default Rate by Education",
                          text="Default Rate %", color="Education", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig5.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig5, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Education chart: {str(e)}")
    
    with col6:
        try:
            contract_default = df.groupby("NAME_CONTRACT_TYPE")["TARGET"].agg(["count", "sum"]).reset_index()
            contract_default["default_rate"] = (contract_default["sum"] / contract_default["count"] * 100).round(2)
            contract_default = contract_default.sort_values("default_rate", ascending=False)
            contract_default = contract_default.rename(columns={"NAME_CONTRACT_TYPE": "Contract Type", "default_rate": "Default Rate %"})
            fig6 = px.bar(contract_default, x="Default Rate %", y="Contract Type", orientation="h", title="Default Rate by Contract Type",
                          text="Default Rate %", color="Contract Type", color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig6.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig6, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Contract Type chart: {str(e)}")

    st.divider()

    st.subheader("📋 Detailed Breakdown Tables")
    st.caption("Expandable tables with corresponding charts showing default rates and customer counts for each segment.")

    with st.expander("📊 Default Rate Summary by Education Type", expanded=False):
        try:
            education_summary = df.groupby("NAME_EDUCATION_TYPE").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda s: int((s == 1).sum())),
            ).reset_index()
            education_summary["Default Rate %"] = (education_summary["Defaults"] / education_summary["Applications"] * 100).round(2)
            education_summary = education_summary.sort_values("Applications", ascending=False)
            
            table_col, chart_col = st.columns([1, 1.2])
            with table_col:
                st.write("**Summary Table:**")
                st.dataframe(education_summary, hide_index=True, use_container_width=True)
            
            with chart_col:
                st.write("**Application Distribution (Pie Chart):**")
                education_summary_renamed = education_summary.rename(columns={"NAME_EDUCATION_TYPE": "Education Type"})
                fig_edu = px.pie(education_summary_renamed, names="Education Type", values="Applications", 
                                title="Application Distribution by Education", hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Set2)
                fig_edu.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_edu, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Education Summary: {str(e)}")

    with st.expander("📊 Default Rate Summary by Contract Type", expanded=False):
        try:
            contract_summary = df.groupby("NAME_CONTRACT_TYPE").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda s: int((s == 1).sum())),
            ).reset_index()
            contract_summary["Default Rate %"] = (contract_summary["Defaults"] / contract_summary["Applications"] * 100).round(2)
            contract_summary = contract_summary.sort_values("Applications", ascending=False)
            
            table_col, chart_col = st.columns([1, 1.2])
            with table_col:
                st.write("**Summary Table:**")
                st.dataframe(contract_summary, hide_index=True, use_container_width=True)
            
            with chart_col:
                st.write("**Applications vs Default Rate (Scatter Plot):**")
                contract_summary_renamed = contract_summary.rename(columns={"NAME_CONTRACT_TYPE": "Contract Type"})
                fig_cont = px.scatter(contract_summary_renamed, x="Applications", y="Default Rate %", 
                                     size="Applications", color="Contract Type", hover_name="Contract Type",
                                     title="Contract Type: Applications vs Default Rate", 
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_cont.update_traces(marker=dict(size=15, opacity=0.7))
                st.plotly_chart(fig_cont, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Contract Summary: {str(e)}")

    with st.expander("📊 Default Rate Summary by Income Type", expanded=False):
        try:
            income_summary = df.groupby("NAME_INCOME_TYPE").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda s: int((s == 1).sum())),
            ).reset_index()
            income_summary["Default Rate %"] = (income_summary["Defaults"] / income_summary["Applications"] * 100).round(2)
            income_summary = income_summary.sort_values("Applications", ascending=False)
            
            table_col, chart_col = st.columns([1, 1.2])
            with table_col:
                st.write("**Summary Table:**")
                st.dataframe(income_summary, hide_index=True, use_container_width=True)
            
            with chart_col:
                st.write("**Defaults Distribution (Doughnut Chart):**")
                income_summary_renamed = income_summary.rename(columns={"NAME_INCOME_TYPE": "Income Type"})
                fig_inc = px.pie(income_summary_renamed, names="Income Type", values="Defaults", 
                                title="Default Customers by Income Type", hole=0.5,
                                color_discrete_sequence=px.colors.qualitative.Set3)
                fig_inc.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_inc, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Income Summary: {str(e)}")

except Exception as e:
    st.error("Dataset not found or invalid.")
    st.caption(f"Error: {str(e)}")