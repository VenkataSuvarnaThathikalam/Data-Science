import streamlit as st
import pandas as pd


def sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.header("🔍 Filters")
    
    # Gender filter
    gender = []
    if "CODE_GENDER" in df.columns:
        gender = st.sidebar.multiselect(
            "Gender",
            options=sorted(df["CODE_GENDER"].dropna().unique()),
            default=sorted(df["CODE_GENDER"].dropna().unique()),
        )
    
    # Target filter
    target = st.sidebar.multiselect(
        "Target (Default Status)",
        options=[0, 1],
        default=[0, 1],
        format_func=lambda x: "Non-Default (0)" if x == 0 else "Default (1)",
    )
    
    # Income type filter
    income_type = st.sidebar.multiselect(
        "Income Type",
        options=sorted(df["NAME_INCOME_TYPE"].dropna().unique()),
        default=sorted(df["NAME_INCOME_TYPE"].dropna().unique()),
    )
    
    # Contract type filter
    contract_type = st.sidebar.multiselect(
        "Contract Type",
        options=sorted(df["NAME_CONTRACT_TYPE"].dropna().unique()),
        default=sorted(df["NAME_CONTRACT_TYPE"].dropna().unique()),
    )
    
    # Education type filter
    education_type = st.sidebar.multiselect(
        "Education Type",
        options=sorted(df["NAME_EDUCATION_TYPE"].dropna().unique()),
        default=sorted(df["NAME_EDUCATION_TYPE"].dropna().unique()),
    )
    
    # Housing type filter
    housing_type = st.sidebar.multiselect(
        "Housing Type",
        options=sorted(df["NAME_HOUSING_TYPE"].dropna().unique()),
        default=sorted(df["NAME_HOUSING_TYPE"].dropna().unique()),
    )
    
    # Family status filter
    family_status = st.sidebar.multiselect(
        "Family Status",
        options=sorted(df["NAME_FAMILY_STATUS"].dropna().unique()),
        default=sorted(df["NAME_FAMILY_STATUS"].dropna().unique()),
    )
    
    filters = {
        "CODE_GENDER": gender,
        "TARGET": target,
        "NAME_INCOME_TYPE": income_type,
        "NAME_CONTRACT_TYPE": contract_type,
        "NAME_EDUCATION_TYPE": education_type,
        "NAME_HOUSING_TYPE": housing_type,
        "NAME_FAMILY_STATUS": family_status,
    }
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    df_filtered = df.copy()
    
    if filters["CODE_GENDER"]:
        df_filtered = df_filtered[df_filtered["CODE_GENDER"].isin(filters["CODE_GENDER"])]
    
    if filters["TARGET"] is not None:
        df_filtered = df_filtered[df_filtered["TARGET"].isin(filters["TARGET"])]
    
    if filters["NAME_INCOME_TYPE"]:
        df_filtered = df_filtered[df_filtered["NAME_INCOME_TYPE"].isin(filters["NAME_INCOME_TYPE"])]
    
    if filters["NAME_CONTRACT_TYPE"]:
        df_filtered = df_filtered[df_filtered["NAME_CONTRACT_TYPE"].isin(filters["NAME_CONTRACT_TYPE"])]
    
    if filters["NAME_EDUCATION_TYPE"]:
        df_filtered = df_filtered[df_filtered["NAME_EDUCATION_TYPE"].isin(filters["NAME_EDUCATION_TYPE"])]
    
    if filters["NAME_HOUSING_TYPE"]:
        df_filtered = df_filtered[df_filtered["NAME_HOUSING_TYPE"].isin(filters["NAME_HOUSING_TYPE"])]
    
    if filters["NAME_FAMILY_STATUS"]:
        df_filtered = df_filtered[df_filtered["NAME_FAMILY_STATUS"].isin(filters["NAME_FAMILY_STATUS"])]
    
    return df_filtered