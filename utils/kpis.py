import pandas as pd
import numpy as np


def calc_kpis(df: pd.DataFrame) -> dict:
    total_applications = len(df)
    total_defaults = (df["TARGET"] == 1).sum()
    total_non_defaults = (df["TARGET"] == 0).sum()
    default_rate = (total_defaults / total_applications * 100) if total_applications > 0 else 0
    
    total_credit = df["AMT_CREDIT"].sum()
    avg_credit = df["AMT_CREDIT"].mean()
    avg_income = df["AMT_INCOME_TOTAL"].mean()
    avg_annuity = df["AMT_ANNUITY"].mean()
    
    return {
        "total_applications": total_applications,
        "total_defaults": total_defaults,
        "total_non_defaults": total_non_defaults,
        "default_rate": default_rate,
        "total_credit": total_credit,
        "avg_credit": avg_credit,
        "avg_income": avg_income,
        "avg_annuity": avg_annuity,
    }


def get_default_summary(df: pd.DataFrame) -> dict:
    total_apps = len(df)
    default_count = (df["TARGET"] == 1).sum()
    default_rate = (default_count / total_apps * 100) if total_apps > 0 else 0
    
    most_common_income = df["NAME_INCOME_TYPE"].mode()[0] if not df["NAME_INCOME_TYPE"].mode().empty else "N/A"
    most_common_education = df["NAME_EDUCATION_TYPE"].mode()[0] if not df["NAME_EDUCATION_TYPE"].mode().empty else "N/A"
    
    # Get highest risk segment by default rate
    segment_default_rate = df.groupby("NAME_INCOME_TYPE")["TARGET"].apply(lambda x: (x == 1).sum() / len(x) * 100)
    highest_risk_segment = segment_default_rate.idxmax() if not segment_default_rate.empty else "N/A"
    
    return {
        "default_rate": default_rate,
        "most_common_income": most_common_income,
        "most_common_education": most_common_education,
        "highest_risk_segment": highest_risk_segment,
    }


def get_demographic_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by gender"""
    return df.groupby("CODE_GENDER").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()


def get_income_type_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by income type"""
    result = df.groupby("NAME_INCOME_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result.sort_values("Applications", ascending=False)


def get_education_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by education type"""
    result = df.groupby("NAME_EDUCATION_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result.sort_values("Applications", ascending=False)


def get_contract_type_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by contract type"""
    result = df.groupby("NAME_CONTRACT_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_CREDIT": "mean",
        "AMT_INCOME_TOTAL": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_CREDIT": "Avg Credit",
        "AMT_INCOME_TOTAL": "Avg Income",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result


def get_housing_type_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by housing type"""
    result = df.groupby("NAME_HOUSING_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result.sort_values("Applications", ascending=False)


def get_occupation_kpis(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Get KPIs by occupation"""
    result = df.groupby("OCCUPATION_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    result = result.sort_values("Applications", ascending=False)
    if top_n:
        result = result.head(top_n)
    return result


def get_organization_type_kpis(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Get KPIs by organization type"""
    result = df.groupby("ORGANIZATION_TYPE").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    result = result.sort_values("Applications", ascending=False)
    if top_n:
        result = result.head(top_n)
    return result


def get_age_group_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by age group"""
    if "AGE" not in df.columns:
        return pd.DataFrame()
    
    df["Age_Group"] = pd.cut(df["AGE"], bins=[0, 25, 35, 45, 55, 65, 100], 
                             labels=["<25", "25-35", "35-45", "45-55", "55-65", "65+"])
    
    result = df.groupby("Age_Group", observed=True).agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "AMT_CREDIT": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "AMT_CREDIT": "Avg Credit",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result


def get_credit_score_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get statistics for external credit scores"""
    external_sources = [col for col in ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"] if col in df.columns]
    
    if not external_sources:
        return pd.DataFrame()
    
    result = {
        "Metric": ["Mean", "Median", "Min", "Max", "Std Dev"],
    }
    
    for source in external_sources:
        data = df[source].dropna()
        result[source] = [
            data.mean(),
            data.median(),
            data.min(),
            data.max(),
            data.std(),
        ]
    
    return pd.DataFrame(result)


def get_regional_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Get KPIs by region"""
    result = df.groupby("REGION_RATING_CLIENT").agg({
        "SK_ID_CURR": "count",
        "TARGET": lambda x: (x == 1).sum(),
        "AMT_INCOME_TOTAL": "mean",
        "REGION_POPULATION_RELATIVE": "mean",
    }).rename(columns={
        "SK_ID_CURR": "Applications",
        "TARGET": "Defaults",
        "AMT_INCOME_TOTAL": "Avg Income",
        "REGION_POPULATION_RELATIVE": "Avg Pop Relative",
    }).reset_index()
    result["Default_Rate_%"] = (result["Defaults"] / result["Applications"] * 100).round(2)
    return result.sort_values("Applications", ascending=False)