import io
import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Customer Risk Explorer")
st.caption("Explore individual customers, filtered applicant records, and risk indicators in one place.")

try:
    df = load_home_credit_data()
    required = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "DAYS_BIRTH",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "NAME_EDUCATION_TYPE",
        "OCCUPATION_TYPE",
        "NAME_FAMILY_STATUS",
        "CNT_CHILDREN",
        "NAME_HOUSING_TYPE",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "NAME_INCOME_TYPE",
        "NAME_CONTRACT_TYPE",
        "DAYS_EMPLOYED",
        "AMT_GOODS_PRICE",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df["AGE"] = (df["DAYS_BIRTH"].abs() / 365).round(1)
    df["EMPLOYMENT_YEARS"] = (df["DAYS_EMPLOYED"].replace({365243: pd.NA}).abs() / 365).round(1)
    df["CREDIT_TO_INCOME_RATIO"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    df["ANNUITY_TO_INCOME_RATIO"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    df["CREDIT_TO_GOODS_RATIO"] = df["AMT_CREDIT"] / df["AMT_GOODS_PRICE"].replace(0, pd.NA)
    df["AVG_EXTERNAL_SCORE"] = df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)

    st.sidebar.subheader("Filters")
    target_options = sorted(df["TARGET"].dropna().unique().tolist())
    selected_targets = st.sidebar.multiselect("TARGET", target_options, default=target_options)
    selected_gender = st.sidebar.multiselect("Gender", sorted(df["CODE_GENDER"].dropna().unique().tolist()), default=sorted(df["CODE_GENDER"].dropna().unique().tolist()))
    age_min, age_max = st.sidebar.slider("Age Range", int(df["AGE"].min()), int(df["AGE"].max()), (int(df["AGE"].min()), int(df["AGE"].max())))
    selected_income_type = st.sidebar.multiselect("Income Type", sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist()))
    selected_education = st.sidebar.multiselect("Education", sorted(df["NAME_EDUCATION_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_EDUCATION_TYPE"].dropna().unique().tolist()))
    selected_occupation = st.sidebar.multiselect("Occupation", sorted(df["OCCUPATION_TYPE"].dropna().unique().tolist()), default=sorted(df["OCCUPATION_TYPE"].dropna().unique().tolist()))
    selected_contract = st.sidebar.multiselect("Contract Type", sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()))
    selected_housing = st.sidebar.multiselect("Housing Type", sorted(df["NAME_HOUSING_TYPE"].dropna().unique().tolist()), default=sorted(df["NAME_HOUSING_TYPE"].dropna().unique().tolist()))
    car_options = sorted(df["FLAG_OWN_CAR"].dropna().unique().tolist()) if "FLAG_OWN_CAR" in df.columns else ["Y", "N"]
    selected_car = st.sidebar.multiselect("Car Ownership", car_options, default=car_options)
    realty_options = sorted(df["FLAG_OWN_REALTY"].dropna().unique().tolist()) if "FLAG_OWN_REALTY" in df.columns else ["Y", "N"]
    selected_realty = st.sidebar.multiselect("Property Ownership", realty_options, default=realty_options)

    income_min, income_max = st.sidebar.slider("Income Range", float(df["AMT_INCOME_TOTAL"].min()), float(df["AMT_INCOME_TOTAL"].max()), (float(df["AMT_INCOME_TOTAL"].min()), float(df["AMT_INCOME_TOTAL"].max())))
    credit_min, credit_max = st.sidebar.slider("Credit Range", float(df["AMT_CREDIT"].min()), float(df["AMT_CREDIT"].max()), (float(df["AMT_CREDIT"].min()), float(df["AMT_CREDIT"].max())))

    filtered_df = df[
        df["TARGET"].isin(selected_targets) &
        df["CODE_GENDER"].isin(selected_gender) &
        df["AGE"].between(age_min, age_max) &
        df["NAME_INCOME_TYPE"].isin(selected_income_type) &
        df["NAME_EDUCATION_TYPE"].isin(selected_education) &
        df["OCCUPATION_TYPE"].isin(selected_occupation) &
        df["NAME_CONTRACT_TYPE"].isin(selected_contract) &
        df["NAME_HOUSING_TYPE"].isin(selected_housing) &
        df.get("FLAG_OWN_CAR", pd.Series("Y", index=df.index)).isin(selected_car) &
        df.get("FLAG_OWN_REALTY", pd.Series("Y", index=df.index)).isin(selected_realty) &
        df["AMT_INCOME_TOTAL"].between(income_min, income_max) &
        df["AMT_CREDIT"].between(credit_min, credit_max)
    ].copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Customers", f"{len(filtered_df):,}")
    c2.metric("Default Customers", f"{int((filtered_df['TARGET'] == 1).sum()):,}")
    c3.metric("Avg Credit-to-Income", f"{filtered_df['CREDIT_TO_INCOME_RATIO'].mean():.2f}")
    c4.metric("Avg External Score", f"{filtered_df['AVG_EXTERNAL_SCORE'].mean():.2f}")

    search_value = st.text_input("Search by Customer ID", value="")
    if search_value:
        filtered_df = filtered_df[filtered_df["SK_ID_CURR"].astype(str).str.contains(str(search_value), case=False, na=False)]

    customer_ids = filtered_df["SK_ID_CURR"].tolist()
    selected_customer = st.selectbox("Select customer", customer_ids, index=0 if customer_ids else None)

    if selected_customer is not None:
        profile = filtered_df[filtered_df["SK_ID_CURR"] == selected_customer].iloc[0]
        st.subheader(f"Customer Risk Profile — {selected_customer}")
        st.markdown(
            f"""
            - Target: **{profile['TARGET']}**  
            - Age: **{profile['AGE']:.0f}**  
            - Gender: **{profile['CODE_GENDER']}**  
            - Income: **${profile['AMT_INCOME_TOTAL']:,.0f}**  
            - Credit Amount: **${profile['AMT_CREDIT']:,.0f}**  
            - Annuity: **${profile['AMT_ANNUITY']:,.0f}**  
            - Education: **{profile['NAME_EDUCATION_TYPE']}**  
            - Occupation: **{profile['OCCUPATION_TYPE']}**  
            - Family Status: **{profile['NAME_FAMILY_STATUS']}**  
            - Children: **{profile['CNT_CHILDREN']}**  
            - Housing Type: **{profile['NAME_HOUSING_TYPE']}**  
            - Avg External Score: **{profile['AVG_EXTERNAL_SCORE']:.2f}**  
            - Credit-to-Income Ratio: **{profile['CREDIT_TO_INCOME_RATIO']:.2f}**  
            - Annuity-to-Income Ratio: **{profile['ANNUITY_TO_INCOME_RATIO']:.2f}**  
            - Credit-to-Goods Ratio: **{profile['CREDIT_TO_GOODS_RATIO']:.2f}**  
            - Employment Years: **{profile['EMPLOYMENT_YEARS']:.1f}**  
            """
        )

    st.subheader("Customer Risk Overview")
    risk_plot_df = filtered_df[["TARGET", "CREDIT_TO_INCOME_RATIO", "ANNUITY_TO_INCOME_RATIO", "AVG_EXTERNAL_SCORE", "AGE"]].copy().dropna()
    fig_risk = px.scatter(risk_plot_df, x="CREDIT_TO_INCOME_RATIO", y="ANNUITY_TO_INCOME_RATIO", color="TARGET", title="Risk Indicator Scatter", opacity=0.6)
    st.plotly_chart(fig_risk, use_container_width=True)

    st.subheader("Filtered Applicant Records")
    display_df = filtered_df[
        [
            "SK_ID_CURR",
            "TARGET",
            "AGE",
            "CODE_GENDER",
            "AMT_INCOME_TOTAL",
            "AMT_CREDIT",
            "AMT_ANNUITY",
            "NAME_EDUCATION_TYPE",
            "OCCUPATION_TYPE",
            "NAME_FAMILY_STATUS",
            "CNT_CHILDREN",
            "NAME_HOUSING_TYPE",
            "EXT_SOURCE_1",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3",
            "CREDIT_TO_INCOME_RATIO",
            "ANNUITY_TO_INCOME_RATIO",
            "CREDIT_TO_GOODS_RATIO",
            "EMPLOYMENT_YEARS",
            "AVG_EXTERNAL_SCORE",
        ]
    ].copy()
    display_df.columns = [
        "Customer ID",
        "TARGET",
        "Age",
        "Gender",
        "Income",
        "Credit Amount",
        "Annuity",
        "Education",
        "Occupation",
        "Family Status",
        "Number of Children",
        "Housing Type",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "Credit-to-Income Ratio",
        "Annuity-to-Income Ratio",
        "Credit-to-Goods Ratio",
        "Employment Years",
        "Average External Score",
    ]
    st.dataframe(display_df, use_container_width=True, height=500)

    st.subheader("Download Filtered Data")
    csv = display_df.to_csv(index=False)
    st.download_button("Download Filtered Customers", data=csv, file_name="filtered_customers.csv", mime="text/csv")

    default_df = display_df[display_df["TARGET"] == 1]
    if not default_df.empty:
        st.download_button("Download Default Customers", data=default_df.to_csv(index=False), file_name="default_customers.csv", mime="text/csv")

    high_risk = display_df[(display_df["Credit-to-Income Ratio"] > 4) | (display_df["Annuity-to-Income Ratio"] > 0.3) | (display_df["Average External Score"] < 0.3)]
    if not high_risk.empty:
        st.download_button("Download High-Risk Customers", data=high_risk.to_csv(index=False), file_name="high_risk_customers.csv", mime="text/csv")

    summary_csv = pd.DataFrame({
        "Metric": ["Filtered Customers", "Default Customers", "Avg Credit-to-Income", "Avg External Score"],
        "Value": [len(filtered_df), int((filtered_df['TARGET'] == 1).sum()), round(filtered_df['CREDIT_TO_INCOME_RATIO'].mean(), 2), round(filtered_df['AVG_EXTERNAL_SCORE'].mean(), 2)],
    })
    st.download_button("Download Summary CSV", data=summary_csv.to_csv(index=False), file_name="risk_summary.csv", mime="text/csv")

except Exception as e:
    st.error("Unable to load or process the Home Credit dataset.")
    st.exception(e)