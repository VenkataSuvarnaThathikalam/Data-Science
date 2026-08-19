import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")

st.title("Correlation & Risk Factor Analysis")
st.caption(
    "Identify key numerical relationships associated with default risk "
    "and loan behavior."
)

try:
    df = load_home_credit_data()

    # ============================================================
    # REQUIRED NUMERICAL FEATURES
    # ============================================================
    numerical_features = [
        "TARGET",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "DAYS_BIRTH",
        "DAYS_EMPLOYED",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
    ]

    missing_cols = [
        c for c in numerical_features
        if c not in df.columns
    ]

    if missing_cols:
        raise ValueError(
            f"Required numerical columns missing: {missing_cols}"
        )

    # ============================================================
    # DERIVED FEATURES
    # ============================================================
    df_corr = df[numerical_features].copy()

    df_corr["AGE"] = (
        df_corr["DAYS_BIRTH"].abs() / 365
    ).round(1)

    df_corr["EMPLOYMENT_YEARS"] = (
        df_corr["DAYS_EMPLOYED"].abs() / 365
    ).round(1)

    df_corr["CREDIT_TO_INCOME_RATIO"] = (
        df_corr["AMT_CREDIT"]
        / df_corr["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    )

    df_corr["ANNUITY_TO_INCOME_RATIO"] = (
        df_corr["AMT_ANNUITY"]
        / df_corr["AMT_INCOME_TOTAL"].replace(0, pd.NA)
    )

    df_corr["AVG_EXTERNAL_SCORE"] = df_corr[
        [
            "EXT_SOURCE_1",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3"
        ]
    ].mean(axis=1)

    # ============================================================
    # CORRELATION DATA
    # ============================================================
    corr_df = (
        df_corr
        .select_dtypes(include=["number"])
        .corr()
        .round(3)
    )

    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3 = st.tabs(
        [
            "Correlations",
            "Scatter Plots",
            "Risk Factor Insights"
        ]
    )

    # ============================================================
    # TAB 1: CORRELATIONS
    # ============================================================
    with tab1:

        st.subheader("Correlation Heatmap")

        fig_heat = px.imshow(
            corr_df,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Numeric Feature Correlation Heatmap"
        )

        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )

        # --------------------------------------------------------
        # Correlation with TARGET
        # --------------------------------------------------------
        corr_with_target = (
            corr_df["TARGET"]
            .dropna()
            .sort_values(ascending=False)
        )

        corr_target = (
            corr_with_target
            .reset_index()
            .rename(
                columns={
                    "index": "Feature",
                    "TARGET": "Correlation with TARGET"
                }
            )
        )

        corr_target = corr_target[
            corr_target["Feature"] != "TARGET"
        ]

        fig_target = px.bar(
            corr_target,
            x="Feature",
            y="Correlation with TARGET",
            title="Correlation with TARGET",
            text="Correlation with TARGET",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_target.update_xaxes(tickangle=45)

        st.plotly_chart(
            fig_target,
            use_container_width=True
        )

        # --------------------------------------------------------
        # Absolute Correlation
        # --------------------------------------------------------
        corr_target_series = (
            corr_df["TARGET"]
            .dropna()
            .sort_values(ascending=False)
        )

        corr_target_series = corr_target_series[
            corr_target_series.index != "TARGET"
        ]

        abs_corr = (
            corr_target_series
            .abs()
            .sort_values(ascending=False)
        )

        abs_corr_df = (
            abs_corr
            .reset_index()
            .rename(
                columns={
                    "index": "Feature",
                    "TARGET": "Absolute Correlation"
                }
            )
            .head(15)
        )

        fig_abs = px.bar(
            abs_corr_df,
            x="Feature",
            y="Absolute Correlation",
            title="Top Features by Absolute Correlation with TARGET",
            text="Absolute Correlation",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_abs.update_xaxes(tickangle=45)

        st.plotly_chart(
            fig_abs,
            use_container_width=True
        )

    # ============================================================
    # TAB 2: SCATTER PLOTS
    # ============================================================
    with tab2:

        st.subheader("Credit vs Income")

        scatter_df = df_corr[
            [
                "AMT_INCOME_TOTAL",
                "AMT_CREDIT",
                "TARGET",
                "AVG_EXTERNAL_SCORE",
                "CREDIT_TO_INCOME_RATIO"
            ]
        ].dropna()

        fig_scatter = px.scatter(
            scatter_df,
            x="AMT_INCOME_TOTAL",
            y="AMT_CREDIT",
            color="TARGET",
            title="Credit vs Income Scatter Plot",
            opacity=0.5
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

        # --------------------------------------------------------
        # External Score
        # --------------------------------------------------------
        st.subheader("External Score vs Default Risk")

        ext_score_df = df_corr[
            [
                "AVG_EXTERNAL_SCORE",
                "TARGET"
            ]
        ].dropna()

        fig_ext = px.box(
            ext_score_df,
            x="TARGET",
            y="AVG_EXTERNAL_SCORE",
            title="External Score vs TARGET",
            color="TARGET",
            category_orders={
                "TARGET": [0, 1]
            }
        )

        st.plotly_chart(
            fig_ext,
            use_container_width=True
        )

        # --------------------------------------------------------
        # Age vs TARGET
        # --------------------------------------------------------
        st.subheader("Age vs Default Risk")

        age_plot_df = df_corr[
            [
                "AGE",
                "TARGET"
            ]
        ].dropna()

        fig_age = px.box(
            age_plot_df,
            x="TARGET",
            y="AGE",
            color="TARGET",
            category_orders={
                "TARGET": [0, 1]
            },
            title="Age Distribution by Default Status"
        )

        st.plotly_chart(
            fig_age,
            use_container_width=True
        )

    # ============================================================
    # TAB 3: RISK FACTOR INSIGHTS
    # ============================================================
    with tab3:

        st.subheader("🚨 Important Risk Factors")

        # ========================================================
        # 1. CERTAIN INCOME TYPES
        # ========================================================
        if "NAME_INCOME_TYPE" in df.columns:

            income_risk = (
                df.groupby("NAME_INCOME_TYPE", dropna=False)
                .agg(
                    Customers=("TARGET", "count"),
                    Defaults=("TARGET", "sum"),
                    Default_Rate=("TARGET", "mean")
                )
                .reset_index()
            )

            income_risk["Default Rate (%)"] = (
                income_risk["Default_Rate"] * 100
            ).round(2)

            income_risk = income_risk[
                income_risk["Customers"] >= 100
            ].sort_values(
                "Default Rate (%)",
                ascending=False
            )

            if not income_risk.empty:

                highest_income_type = (
                    income_risk.iloc[0]["NAME_INCOME_TYPE"]
                )

                highest_income_rate = (
                    income_risk.iloc[0]["Default Rate (%)"]
                )

                income_insight = (
                    f"Certain income types show higher default risk. "
                    f"The highest observed default rate among income groups "
                    f"with at least 100 applicants is "
                    f"'{highest_income_type}' at "
                    f"{highest_income_rate:.2f}%."
                )

            else:
                income_insight = (
                    "Income-type risk could not be calculated because "
                    "there were insufficient observations."
                )

        else:

            income_insight = (
                "NAME_INCOME_TYPE is not available in the dataset."
            )

        # ========================================================
        # 2. YOUNGER AGE GROUPS
        # ========================================================
        df_age = df.copy()

        df_age["AGE"] = (
            df_age["DAYS_BIRTH"].abs() / 365
        ).round(1)

        # Age groups
        df_age["AGE_GROUP"] = pd.cut(
            df_age["AGE"],
            bins=[
                18,
                25,
                30,
                35,
                40,
                50,
                60,
                100
            ],
            labels=[
                "18-25",
                "26-30",
                "31-35",
                "36-40",
                "41-50",
                "51-60",
                "61+"
            ],
            include_lowest=True
        )

        age_risk = (
            df_age.groupby(
                "AGE_GROUP",
                observed=False
            )
            .agg(
                Customers=("TARGET", "count"),
                Defaults=("TARGET", "sum"),
                Default_Rate=("TARGET", "mean")
            )
            .reset_index()
        )

        age_risk["Default Rate (%)"] = (
            age_risk["Default_Rate"] * 100
        ).round(2)

        age_risk = age_risk[
            age_risk["Customers"] >= 100
        ]

        if not age_risk.empty:

            youngest_risk = age_risk.iloc[0]

            age_insight = (
                f"Younger age groups should be monitored closely. "
                f"The {youngest_risk['AGE_GROUP']} age group has a "
                f"default rate of "
                f"{youngest_risk['Default Rate (%)']:.2f}%."
            )

        else:

            age_insight = (
                "Age-group risk could not be calculated because "
                "there were insufficient observations."
            )

        # ========================================================
        # STATIC + DATA-DRIVEN INSIGHTS
        # ========================================================
        insights = [
            "Low external credit scores are frequently associated with higher default risk.",

            "High credit-to-income ratios suggest over-borrowing "
            "relative to income and should be monitored closely.",

            "High annuity-to-income ratios increase repayment pressure "
            "and may signal affordability risk.",

            "Younger applicants and shorter employment histories can "
            "show higher repayment risk.",

            income_insight,

            age_insight,

            "Regional rating and city mismatches can be useful "
            "segmentation signals for risk monitoring.",

            "Income type and occupation groups with weaker repayment "
            "profiles can show elevated default rates."
        ]

        for insight in insights:
            st.markdown(f"- {insight}")

        # ========================================================
        # INCOME TYPE RISK CHART
        # ========================================================
        if "NAME_INCOME_TYPE" in df.columns:

            st.subheader("Income Type vs Default Rate")

            income_chart = income_risk.sort_values(
                "Default Rate (%)",
                ascending=True
            )

            fig_income = px.bar(
                income_chart,
                x="Default Rate (%)",
                y="NAME_INCOME_TYPE",
                orientation="h",
                text="Default Rate (%)",
                title="Default Rate by Income Type",
                color="Default Rate (%)"
            )

            st.plotly_chart(
                fig_income,
                use_container_width=True
            )

            st.dataframe(
                income_risk[
                    [
                        "NAME_INCOME_TYPE",
                        "Customers",
                        "Defaults",
                        "Default Rate (%)"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        # ========================================================
        # AGE GROUP RISK CHART
        # ========================================================
        st.subheader("Age Group vs Default Rate")

        fig_age_risk = px.bar(
            age_risk,
            x="AGE_GROUP",
            y="Default Rate (%)",
            text="Default Rate (%)",
            title="Default Rate by Age Group",
            color="Default Rate (%)"
        )

        st.plotly_chart(
            fig_age_risk,
            use_container_width=True
        )

        st.dataframe(
            age_risk[
                [
                    "AGE_GROUP",
                    "Customers",
                    "Defaults",
                    "Default Rate (%)"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        # ========================================================
        # RISK FACTOR SUMMARY TABLE
        # ========================================================
        st.subheader("📋 Risk Factor Summary")

        risk_summary = pd.DataFrame({
            "Risk Factor": [
                "Low External Score",
                "High Credit-to-Income Ratio",
                "High Annuity-to-Income Ratio",
                "Certain Income Types",
                "Younger Age Groups",
                "Lower Employment History",
                "High Regional Risk Rating",
            ],

            "Why It Matters": [
                "Lower external scores indicate higher repayment uncertainty.",

                "Borrowing more relative to income can increase "
                "default probability.",

                "Higher payments relative to income create repayment strain.",

                "Some income categories may show higher observed "
                "default rates than others.",

                "Younger applicants may have less established "
                "repayment history and income stability.",

                "Shorter employment tenure can indicate less stable income.",

                "Region-level risk can signal weaker economic conditions "
                "or local credit behavior."
            ],
        })

        st.dataframe(
            risk_summary,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:

    st.error(
        "Unable to load or process the Home Credit dataset."
    )

    st.exception(e)