import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")

st.title("Age Analysis")
st.caption(
    "Analyze the relationship between age and credit risk across the Home Credit applicant base."
)

try:
    # =========================================================
    # LOAD DATA
    # =========================================================
    df = load_home_credit_data()

    required = [
        "DAYS_BIRTH",
        "TARGET",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    # =========================================================
    # AGE CALCULATION
    # =========================================================
    df["AGE"] = (
        df["DAYS_BIRTH"].abs() / 365
    ).round(1)

    age_bins = [
        18, 26, 31, 36, 41,
        46, 51, 56, 61, 100
    ]

    labels = [
        "18-25",
        "26-30",
        "31-35",
        "36-40",
        "41-45",
        "46-50",
        "51-55",
        "56-60",
        "61+"
    ]

    df["AGE_GROUP"] = pd.cut(
        df["AGE"],
        bins=age_bins,
        labels=labels,
        right=False
    )

    # =========================================================
    # SIDEBAR FILTERS
    # =========================================================
    st.sidebar.subheader("Filters")

    # Gender
    if "CODE_GENDER" in df.columns:

        gender_options = sorted(
            df["CODE_GENDER"]
            .dropna()
            .unique()
            .tolist()
        )

        gender_filter = st.sidebar.multiselect(
            "Gender",
            gender_options,
            default=gender_options
        )

    else:
        gender_filter = []

    # Income Type
    if "NAME_INCOME_TYPE" in df.columns:

        income_col = df["NAME_INCOME_TYPE"]

        income_options = sorted(
            income_col
            .dropna()
            .unique()
            .tolist()
        )

        income_type_filter = st.sidebar.multiselect(
            "Income Type",
            income_options,
            default=income_options
        )

    else:

        income_col = pd.Series(
            "Unknown",
            index=df.index
        )

        income_type_filter = ["Unknown"]

    # =========================================================
    # APPLY FILTERS
    # =========================================================
    if "CODE_GENDER" in df.columns:

        filtered_df = df[
            df["CODE_GENDER"].isin(gender_filter)
            &
            income_col.isin(income_type_filter)
        ].copy()

    else:

        filtered_df = df[
            income_col.isin(income_type_filter)
        ].copy()

    # =========================================================
    # KPI CALCULATIONS
    # =========================================================
    if not filtered_df.empty:

        average_age = filtered_df["AGE"].mean()
        youngest_customer = filtered_df["AGE"].min()
        oldest_customer = filtered_df["AGE"].max()

        age_group_default = (
            filtered_df
            .groupby(
                "AGE_GROUP",
                observed=False
            )["TARGET"]
            .mean()
            .reset_index(
                name="Default Rate"
            )
        )

        age_group_default["AGE_GROUP"] = pd.Categorical(
            age_group_default["AGE_GROUP"],
            categories=labels,
            ordered=True
        )

        age_group_default = (
            age_group_default
            .sort_values("AGE_GROUP")
        )

        valid_risk_groups = age_group_default.dropna(
            subset=["Default Rate"]
        )

        if not valid_risk_groups.empty:

            highest_risk_age_group = (
                valid_risk_groups
                .loc[
                    valid_risk_groups["Default Rate"].idxmax(),
                    "AGE_GROUP"
                ]
            )

        else:
            highest_risk_age_group = "N/A"

    else:

        average_age = 0
        youngest_customer = 0
        oldest_customer = 0
        highest_risk_age_group = "N/A"

    # =========================================================
    # KPI SECTION
    # =========================================================
    st.subheader("📊 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Age",
            f"{average_age:.1f} years"
        )

    with col2:
        st.metric(
            "Youngest Customer",
            f"{youngest_customer:.0f} years"
        )

    with col3:
        st.metric(
            "Oldest Customer",
            f"{oldest_customer:.0f} years"
        )

    with col4:
        st.metric(
            "Highest Risk Age Group",
            highest_risk_age_group
        )

    # =========================================================
    # VISUALIZATIONS SECTION
    # =========================================================
    st.subheader("📈 Visualizations")

    # =========================================================
    # CHART 1 & 2
    # =========================================================
    c1, c2 = st.columns(2)

    # ---------------------------------------------------------
    # 1. Age Distribution
    # HISTOGRAM
    # ---------------------------------------------------------
    with c1:

        fig_hist = px.histogram(
            filtered_df,
            x="AGE",
            nbins=30,
            title="👥 Age Distribution",
            labels={
                "AGE": "Age"
            }
        )

        fig_hist.update_layout(
            xaxis_title="Age (Years)",
            yaxis_title="Number of Customers",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 2. Applications by Age Group
    # BAR CHART
    # ---------------------------------------------------------
    with c2:

        app_by_group = (
            filtered_df["AGE_GROUP"]
            .value_counts()
            .reindex(
                labels,
                fill_value=0
            )
            .reset_index()
        )

        app_by_group.columns = [
            "Age Group",
            "Applications"
        ]

        fig_app = px.bar(
            app_by_group,
            x="Age Group",
            y="Applications",
            title="📊 Applications by Age Group",
            text="Applications",
            color_discrete_sequence=(
                px.colors.qualitative.Set2
            )
        )

        fig_app.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        fig_app.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Applications"
        )

        st.plotly_chart(
            fig_app,
            use_container_width=True
        )

    # =========================================================
    # CHART 3 & 4
    # =========================================================
    c3, c4 = st.columns(2)

    # ---------------------------------------------------------
    # 3. Payment Difficulty by Age Group
    # STACKED BAR WITH MANUALLY CALCULATED %
    # ---------------------------------------------------------
    with c3:

        age_target = filtered_df[
            ["AGE_GROUP", "TARGET"]
        ].copy()

        age_target["Risk Status"] = age_target[
            "TARGET"
        ].map({
            0: "No Payment Difficulty",
            1: "Payment Difficulty"
        })

        # Count customers
        age_target_counts = (
            age_target
            .groupby(
                ["AGE_GROUP", "Risk Status"],
                observed=False
            )
            .size()
            .reset_index(
                name="Customers"
            )
        )

        # Total customers per age group
        age_totals = (
            age_target_counts
            .groupby(
                "AGE_GROUP",
                observed=False
            )["Customers"]
            .transform("sum")
        )

        # Calculate percentage manually
        age_target_counts["Percentage"] = (
            age_target_counts["Customers"]
            / age_totals
            * 100
        )

        age_target_counts["AGE_GROUP"] = pd.Categorical(
            age_target_counts["AGE_GROUP"],
            categories=labels,
            ordered=True
        )

        age_target_counts = (
            age_target_counts
            .sort_values("AGE_GROUP")
        )

        fig_default_age = px.bar(
            age_target_counts,
            x="AGE_GROUP",
            y="Percentage",
            color="Risk Status",
            title="⚠️ Payment Difficulty by Age Group",
            barmode="stack"
        )

        fig_default_age.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Risk Status: %{fullData.name}<br>"
                "Share: %{y:.1f}%"
                "<extra></extra>"
            )
        )

        fig_default_age.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Customer Share (%)",
            yaxis=dict(
                range=[0, 100]
            ),
            legend_title="Risk Status"
        )

        st.plotly_chart(
            fig_default_age,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 4. Default Rate by Age Group
    # BAR CHART
    # ---------------------------------------------------------
    with c4:

        group_df = (
            filtered_df
            .groupby(
                "AGE_GROUP",
                observed=False
            )
            .agg(
                Applications=("TARGET", "count"),
                Defaults=("TARGET", "sum")
            )
            .reset_index()
        )

        group_df["Default Rate"] = (
            group_df["Defaults"]
            / group_df["Applications"]
            * 100
        )

        group_df["AGE_GROUP"] = pd.Categorical(
            group_df["AGE_GROUP"],
            categories=labels,
            ordered=True
        )

        group_df = (
            group_df
            .sort_values("AGE_GROUP")
        )

        fig_group = px.bar(
            group_df,
            x="AGE_GROUP",
            y="Default Rate",
            title="📉 Default Rate by Age Group",
            text="Default Rate",
            color_discrete_sequence=(
                px.colors.qualitative.Pastel
            )
        )

        fig_group.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_group.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Default Rate (%)"
        )

        st.plotly_chart(
            fig_group,
            use_container_width=True
        )

    # =========================================================
    # CHART 5 & 6
    # =========================================================
    c5, c6 = st.columns(2)

    # ---------------------------------------------------------
    # 5. Credit Distribution by Age Group
    # BOX PLOT
    # ---------------------------------------------------------
    with c5:

        credit_age = (
            filtered_df[
                [
                    "AGE_GROUP",
                    "AMT_CREDIT"
                ]
            ]
            .dropna()
            .copy()
        )

        credit_age["AGE_GROUP"] = pd.Categorical(
            credit_age["AGE_GROUP"],
            categories=labels,
            ordered=True
        )

        fig_credit = px.box(
            credit_age.sort_values(
                "AGE_GROUP"
            ),
            x="AGE_GROUP",
            y="AMT_CREDIT",
            title="💳 Credit Amount Distribution by Age Group",
            points=False
        )

        fig_credit.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Credit Amount"
        )

        st.plotly_chart(
            fig_credit,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 6. Income Distribution by Age Group
    # BOX PLOT
    # ---------------------------------------------------------
    with c6:

        income_age = (
            filtered_df[
                [
                    "AGE_GROUP",
                    "AMT_INCOME_TOTAL"
                ]
            ]
            .dropna()
            .copy()
        )

        income_age["AGE_GROUP"] = pd.Categorical(
            income_age["AGE_GROUP"],
            categories=labels,
            ordered=True
        )

        fig_income = px.box(
            income_age.sort_values(
                "AGE_GROUP"
            ),
            x="AGE_GROUP",
            y="AMT_INCOME_TOTAL",
            title="💰 Income Distribution by Age Group",
            points=False
        )

        fig_income.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Income"
        )

        st.plotly_chart(
            fig_income,
            use_container_width=True
        )

except Exception as e:

    st.error(
        "Unable to load or process the Home Credit dataset."
    )

    st.exception(e)