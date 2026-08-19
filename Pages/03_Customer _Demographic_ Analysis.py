import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")

st.header("👥 Customer Demographic Analysis")
st.caption("Comprehensive view of applicant demographics, family structure, education, and housing characteristics across the portfolio.")

try:
    df = load_home_credit_data()

    # Sidebar Filters
    st.sidebar.subheader("🔍 Filter Options")
    
    # Age calculation
    if "DAYS_BIRTH" in df.columns:
        df["AGE"] = (-df["DAYS_BIRTH"] / 365).astype(int)
    else:
        df["AGE"] = 0

    # Gender filter
    selected_genders = st.sidebar.multiselect(
        "Select Gender",
        options=df["CODE_GENDER"].unique(),
        default=df["CODE_GENDER"].unique(),
    )

    # Age range filter
    min_age, max_age = st.sidebar.slider(
        "Select Age Range",
        min_value=int(df["AGE"].min()),
        max_value=int(df["AGE"].max()),
        value=(int(df["AGE"].min()), int(df["AGE"].max())),
    )

    # Family Status filter
    selected_family_status = st.sidebar.multiselect(
        "Select Family Status",
        options=df["NAME_FAMILY_STATUS"].unique(),
        default=df["NAME_FAMILY_STATUS"].unique(),
    )

    # Education filter
    selected_education = st.sidebar.multiselect(
        "Select Education Level",
        options=df["NAME_EDUCATION_TYPE"].unique(),
        default=df["NAME_EDUCATION_TYPE"].unique(),
    )

    # Housing Type filter
    selected_housing = st.sidebar.multiselect(
        "Select Housing Type",
        options=df["NAME_HOUSING_TYPE"].unique(),
        default=df["NAME_HOUSING_TYPE"].unique(),
    )

    # Apply filters
    filtered_df = df[
        (df["CODE_GENDER"].isin(selected_genders))
        & (df["AGE"] >= min_age)
        & (df["AGE"] <= max_age)
        & (df["NAME_FAMILY_STATUS"].isin(selected_family_status))
        & (df["NAME_EDUCATION_TYPE"].isin(selected_education))
        & (df["NAME_HOUSING_TYPE"].isin(selected_housing))
    ]

    st.markdown(f"**Filtered Applicants:** {len(filtered_df):,} out of {len(df):,} total")

    # KPI Cards
    st.subheader("📊 Demographic KPI Cards")
    st.caption("Summary statistics of demographic characteristics for the filtered applicant base.")

    total_customers = len(filtered_df)
    avg_age = filtered_df["AGE"].mean() if "AGE" in filtered_df.columns else 0
    male_customers = len(filtered_df[filtered_df["CODE_GENDER"] == "M"])
    female_customers = len(filtered_df[filtered_df["CODE_GENDER"] == "F"])
    avg_family_size = filtered_df["CNT_FAM_MEMBERS"].mean() if "CNT_FAM_MEMBERS" in filtered_df.columns else 0

    kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4, kpi_col_5 = st.columns(5)
    kpi_col_1.metric("Total Customers", f"{total_customers:,}")
    kpi_col_2.metric("Average Age", f"{avg_age:.1f} years")
    kpi_col_3.metric("Male Customers", f"{male_customers:,}")
    kpi_col_4.metric("Female Customers", f"{female_customers:,}")
    kpi_col_5.metric("Average Family Size", f"{avg_family_size:.2f}")

    st.divider()

    # Visualizations
    st.subheader("📈 Demographic Distribution Charts")
    st.caption("These visualizations show the breakdown of applicants across various demographic dimensions.")

    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        try:
            gender_counts = filtered_df["CODE_GENDER"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            gender_counts["Gender"] = gender_counts["Gender"].map({"M": "Male", "F": "Female"})
            fig_gender = px.bar(
                gender_counts,
                x="Gender",
                y="Count",
                title="Customers by Gender",
                text="Count",
                color="Gender",
                color_discrete_sequence=["#3b82f6", "#ec4899"],
            )
            fig_gender.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_gender, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Gender chart: {str(e)}")

    with chart_col_2:
        try:
            # Age groups
            filtered_df_temp = filtered_df.copy()
            filtered_df_temp["Age Group"] = pd.cut(
                filtered_df_temp["AGE"],
                bins=[0, 25, 35, 45, 55, 65, 100],
                labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
            )
            age_counts = filtered_df_temp["Age Group"].value_counts().sort_index().reset_index()
            age_counts.columns = ["Age Group", "Count"]
            fig_age = px.histogram(
                filtered_df_temp,
                x="Age Group",
                nbins=30,
                title="Customers by Age Group",
                color_discrete_sequence=["#10b981"],
            )
            fig_age.update_layout(hovermode="x unified", showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Age Group chart: {str(e)}")

    chart_col_3, chart_col_4 = st.columns(2)
    with chart_col_3:
        try:
            family_status_counts = filtered_df["NAME_FAMILY_STATUS"].value_counts().reset_index()
            family_status_counts.columns = ["Family Status", "Count"]
            fig_family_status = px.bar(
                family_status_counts,
                x="Family Status",
                y="Count",
                title="Customers by Family Status",
                text="Count",
                color="Family Status",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_family_status.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_family_status, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Family Status chart: {str(e)}")

    with chart_col_4:
        try:
            education_counts = filtered_df["NAME_EDUCATION_TYPE"].value_counts().reset_index()
            education_counts.columns = ["Education", "Count"]
            fig_education = px.bar(
                education_counts,
                x="Education",
                y="Count",
                title="Customers by Education Level",
                text="Count",
                color="Education",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_education.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_education, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Education chart: {str(e)}")

    chart_col_5, chart_col_6 = st.columns(2)
    with chart_col_5:
        try:
            housing_counts = filtered_df["NAME_HOUSING_TYPE"].value_counts().reset_index()
            housing_counts.columns = ["Housing Type", "Count"]
            fig_housing = px.bar(
                housing_counts,
                x="Housing Type",
                y="Count",
                title="Customers by Housing Type",
                text="Count",
                color="Housing Type",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_housing.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_housing, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Housing Type chart: {str(e)}")

    with chart_col_6:
        try:
            # Default rate by demographic group (Gender)
            demo_default = filtered_df.groupby("CODE_GENDER").agg(
                Total=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
            ).reset_index()
            demo_default["Default Rate %"] = (demo_default["Defaults"] / demo_default["Total"] * 100).round(2)
            demo_default["Gender"] = demo_default["CODE_GENDER"].map({"M": "Male", "F": "Female"})
            
            fig_demo_default = px.bar(
                demo_default,
                x="Gender",
                y="Default Rate %",
                title="Default Rate by Gender",
                text="Default Rate %",
                color="Gender",
                color_discrete_sequence=["#3b82f6", "#ec4899"],
            )
            fig_demo_default.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_demo_default, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Default Rate by Gender chart: {str(e)}")

    st.divider()

    # Default Rate Analysis by Demographics
    st.subheader("🔍 Default Rate Analysis by Demographic Segments")
    st.caption("Comparative analysis of default rates across different demographic dimensions.")

    analysis_col_1, analysis_col_2 = st.columns(2)
    with analysis_col_1:
        try:
            family_default = filtered_df.groupby("NAME_FAMILY_STATUS").agg(
                Total=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
            ).reset_index()
            family_default["Default Rate %"] = (family_default["Defaults"] / family_default["Total"] * 100).round(2)
            family_default = family_default.sort_values("Default Rate %", ascending=False)
            family_default = family_default.rename(columns={"NAME_FAMILY_STATUS": "Family Status"})
            
            fig_family_default = px.bar(
                family_default,
                x="Default Rate %",
                y="Family Status",
                orientation="h",
                title="Default Rate by Family Status",
                text="Default Rate %",
                color="Family Status",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_family_default.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_family_default, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Family Status Default Rate chart: {str(e)}")

    with analysis_col_2:
        try:
            education_default = filtered_df.groupby("NAME_EDUCATION_TYPE").agg(
                Total=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
            ).reset_index()
            education_default["Default Rate %"] = (education_default["Defaults"] / education_default["Total"] * 100).round(2)
            education_default = education_default.sort_values("Default Rate %", ascending=False)
            education_default = education_default.rename(columns={"NAME_EDUCATION_TYPE": "Education"})
            
            fig_education_default = px.bar(
                education_default,
                x="Default Rate %",
                y="Education",
                orientation="h",
                title="Default Rate by Education Level",
                text="Default Rate %",
                color="Education",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_education_default.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_education_default, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Education Default Rate chart: {str(e)}")

    analysis_col_3, analysis_col_4 = st.columns(2)
    with analysis_col_3:
        try:
            housing_default = filtered_df.groupby("NAME_HOUSING_TYPE").agg(
                Total=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
            ).reset_index()
            housing_default["Default Rate %"] = (housing_default["Defaults"] / housing_default["Total"] * 100).round(2)
            housing_default = housing_default.sort_values("Default Rate %", ascending=False)
            housing_default = housing_default.rename(columns={"NAME_HOUSING_TYPE": "Housing Type"})
            
            fig_housing_default = px.bar(
                housing_default,
                x="Default Rate %",
                y="Housing Type",
                orientation="h",
                title="Default Rate by Housing Type",
                text="Default Rate %",
                color="Housing Type",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_housing_default.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_housing_default, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Housing Type Default Rate chart: {str(e)}")

    with analysis_col_4:
        try:
            # Age group default rate
            filtered_df_temp = filtered_df.copy()
            filtered_df_temp["Age Group"] = pd.cut(
                filtered_df_temp["AGE"],
                bins=[0, 25, 35, 45, 55, 65, 100],
                labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
            )
            age_group_default = filtered_df_temp.groupby("Age Group").agg(
                Total=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
            ).reset_index()
            age_group_default["Default Rate %"] = (age_group_default["Defaults"] / age_group_default["Total"] * 100).round(2)
            
            fig_age_default = px.bar(
                age_group_default,
                x="Age Group",
                y="Default Rate %",
                title="Default Rate by Age Group",
                text="Default Rate %",
                color="Age Group",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig_age_default.update_layout(showlegend=False, hovermode="x unified")
            st.plotly_chart(fig_age_default, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Age Group Default Rate chart: {str(e)}")

    st.divider()

    # Summary Tables
    st.subheader("📋 Demographic Summary Tables")
    st.caption("Detailed breakdown of applicant demographics and default patterns.")

    with st.expander("📊 Gender Distribution & Default Rate", expanded=False):
        try:
            gender_summary = filtered_df.groupby("CODE_GENDER").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
                Average_Age=("AGE", "mean"),
                Average_Family_Size=("CNT_FAM_MEMBERS", "mean"),
            ).reset_index()
            gender_summary["Default Rate %"] = (gender_summary["Defaults"] / gender_summary["Applications"] * 100).round(2)
            gender_summary["CODE_GENDER"] = gender_summary["CODE_GENDER"].map({"M": "Male", "F": "Female"})
            gender_summary = gender_summary.rename(columns={
                "CODE_GENDER": "Gender",
                "Average_Age": "Avg Age",
                "Average_Family_Size": "Avg Family Size"
            })
            st.dataframe(gender_summary, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Gender Summary: {str(e)}")

    with st.expander("📊 Education & Default Rate Summary", expanded=False):
        try:
            education_summary = filtered_df.groupby("NAME_EDUCATION_TYPE").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
                Average_Age=("AGE", "mean"),
            ).reset_index()
            education_summary["Default Rate %"] = (education_summary["Defaults"] / education_summary["Applications"] * 100).round(2)
            education_summary = education_summary.rename(columns={
                "NAME_EDUCATION_TYPE": "Education Type",
                "Average_Age": "Avg Age"
            })
            education_summary = education_summary.sort_values("Applications", ascending=False)
            st.dataframe(education_summary, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Education Summary: {str(e)}")

    with st.expander("📊 Family Status & Default Rate Summary", expanded=False):
        try:
            family_summary = filtered_df.groupby("NAME_FAMILY_STATUS").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
                Average_Age=("AGE", "mean"),
                Average_Family_Size=("CNT_FAM_MEMBERS", "mean"),
            ).reset_index()
            family_summary["Default Rate %"] = (family_summary["Defaults"] / family_summary["Applications"] * 100).round(2)
            family_summary = family_summary.rename(columns={
                "NAME_FAMILY_STATUS": "Family Status",
                "Average_Age": "Avg Age",
                "Average_Family_Size": "Avg Family Size"
            })
            family_summary = family_summary.sort_values("Applications", ascending=False)
            st.dataframe(family_summary, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Family Status Summary: {str(e)}")

    with st.expander("📊 Housing Type & Default Rate Summary", expanded=False):
        try:
            housing_summary = filtered_df.groupby("NAME_HOUSING_TYPE").agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda x: int((x == 1).sum())),
                Average_Age=("AGE", "mean"),
                Average_Family_Size=("CNT_FAM_MEMBERS", "mean"),
            ).reset_index()
            housing_summary["Default Rate %"] = (housing_summary["Defaults"] / housing_summary["Applications"] * 100).round(2)
            housing_summary = housing_summary.rename(columns={
                "NAME_HOUSING_TYPE": "Housing Type",
                "Average_Age": "Avg Age",
                "Average_Family_Size": "Avg Family Size"
            })
            housing_summary = housing_summary.sort_values("Applications", ascending=False)
            st.dataframe(housing_summary, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Housing Summary: {str(e)}")

except Exception as e:
    st.error("Dataset not found or invalid.")
    st.caption(f"Error: {str(e)}")