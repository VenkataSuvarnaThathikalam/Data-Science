import pandas as pd
import numpy as np


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(
        csv_path,
        encoding="utf-8",
    )
    
    # Standardize column names
    df.columns = [col.strip() for col in df.columns]
    
    # Create new columns dictionary to avoid DataFrame fragmentation
    new_cols = {}
    
    # Convert DAYS_BIRTH to age in years
    if "DAYS_BIRTH" in df.columns:
        new_cols["AGE"] = abs(df["DAYS_BIRTH"]) / 365.25
    
    # Convert DAYS_EMPLOYED to years of employment
    if "DAYS_EMPLOYED" in df.columns:
        years_employed = abs(df["DAYS_EMPLOYED"]) / 365.25
        years_employed = years_employed.clip(lower=0)  # Replace negative with 0
        new_cols["YEARS_EMPLOYED"] = years_employed
    
    # Calculate loan-to-income ratio
    if "AMT_CREDIT" in df.columns and "AMT_INCOME_TOTAL" in df.columns:
        new_cols["LOAN_TO_INCOME"] = df["AMT_CREDIT"] / (df["AMT_INCOME_TOTAL"] + 1)
    
    # Calculate annuity-to-income ratio
    if "AMT_ANNUITY" in df.columns and "AMT_INCOME_TOTAL" in df.columns:
        new_cols["ANNUITY_TO_INCOME"] = df["AMT_ANNUITY"] / (df["AMT_INCOME_TOTAL"] + 1)
    
    # Add all new columns at once
    if new_cols:
        df = pd.concat([df, pd.DataFrame(new_cols)], axis=1)
    
    # Replace 365243 days (flag for unemployed) with NaN
    if "DAYS_EMPLOYED" in df.columns:
        df.loc[df["DAYS_EMPLOYED"] == 365243, "DAYS_EMPLOYED"] = np.nan
    
    return df