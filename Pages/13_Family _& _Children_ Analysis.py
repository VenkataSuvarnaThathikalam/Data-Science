import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Family & Children Analysis",
    layout="wide"
)

st.title("Family & Children Analysis")
st.caption(
    "Study household characteristics and their relation to credit risk."
)


try:

    # ========================================================
    # LOAD DATA
    # ========================================================
    df = load_home_credit_data()

    required = [
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
        "NAME_FAMILY_STATUS",
        "TARGET",
        "AMT_INCOME_TOTAL"
    ]

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}"
        )

    # ========================================================
    # CLEAN DATA
    # ========================================================
    analysis_df = df[
        [
            "CNT_CHILDREN",
            "CNT_FAM_MEMBERS",
            "NAME_FAMILY_STATUS",
            "TARGET",
            "AMT_INCOME_TOTAL"
        ]
    ].copy()

    analysis_df["CNT_CHILDREN"] = pd.to_numeric(
        analysis_df["CNT_CHILDREN"],
        errors="coerce"
    )

    analysis_df["CNT_FAM_MEMBERS"] = pd.to_numeric(
        analysis_df["CNT_FAM_MEMBERS"],
        errors="coerce"
    )

    analysis_df["TARGET"] = pd.to_numeric(
        analysis_df["TARGET"],
        errors="coerce"
    )

    analysis_df["AMT_INCOME_TOTAL"] = pd.to_numeric(
        analysis_df["AMT_INCOME_TOTAL"],
        errors="coerce"
    )

    # ========================================================
    # SIDEBAR FILTERS
    # ========================================================
    st.sidebar.subheader("Filters")

    family_status = sorted(
        analysis_df["NAME_FAMILY_STATUS"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_status = st.sidebar.multiselect(
        "Family Status",
        family_status,
        default=family_status
    )

    filtered_df = analysis_df[
        analysis_df["NAME_FAMILY_STATUS"]
        .astype(str)
        .isin(selected_status)
    ].copy()

    # ========================================================
    # EMPTY FILTER CHECK
    # ========================================================
    if filtered_df.empty:

        st.warning(
            "No records match the selected Family Status filter. "
            "Please select at least one family status."
        )

        st.stop()

    # ========================================================
    # KEY METRICS
    # ========================================================
    st.subheader("📊 Key Metrics")

    c1, c2, c3, c4, c5 = st.columns(5)

    avg_children = filtered_df[
        "CNT_CHILDREN"
    ].mean()

    avg_family_members = filtered_df[
        "CNT_FAM_MEMBERS"
    ].mean()

    customers_with_children = (
        filtered_df["CNT_CHILDREN"] > 0
    ).sum()

    customers_without_children = (
        filtered_df["CNT_CHILDREN"] == 0
    ).sum()

    family_risk = (
        filtered_df
        .dropna(subset=["NAME_FAMILY_STATUS", "TARGET"])
        .groupby("NAME_FAMILY_STATUS")["TARGET"]
        .mean()
        .sort_values(ascending=False)
    )

    if not family_risk.empty:

        highest_risk_family = family_risk.index[0]

        highest_risk_rate = (
            family_risk.iloc[0] * 100
        )

        highest_risk_display = (
            f"{highest_risk_family} "
            f"({highest_risk_rate:.2f}%)"
        )

    else:

        highest_risk_display = "N/A"

    c1.metric(
        "Average Children",
        f"{avg_children:.2f}"
        if pd.notna(avg_children)
        else "N/A"
    )

    c2.metric(
        "Average Family Members",
        f"{avg_family_members:.2f}"
        if pd.notna(avg_family_members)
        else "N/A"
    )

    c3.metric(
        "Customers with Children",
        f"{customers_with_children:,}"
    )

    c4.metric(
        "Customers without Children",
        f"{customers_without_children:,}"
    )

    c5.metric(
        "Highest Risk Family Type",
        highest_risk_display
    )

    # ========================================================
    # VISUALIZATIONS
    # ========================================================
    st.subheader("📈 Visualizations")

    # ========================================================
    # ROW 1
    # ========================================================
    c1, c2 = st.columns(2)

    # --------------------------------------------------------
    # Customers by Number of Children
    # --------------------------------------------------------
    with c1:

        child_counts = (
            filtered_df["CNT_CHILDREN"]
            .dropna()
            .value_counts()
            .sort_index()
            .reset_index()
        )

        child_counts.columns = [
            "Children",
            "Customers"
        ]

        fig_child = px.bar(
            child_counts,
            x="Children",
            y="Customers",
            title="Customers by Number of Children",
            text="Customers"
        )

        fig_child.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_child,
            use_container_width=True
        )

    # --------------------------------------------------------
    # Default Rate by Number of Children
    # --------------------------------------------------------
    with c2:

        child_default = (
            filtered_df
            .dropna(subset=["CNT_CHILDREN", "TARGET"])
            .groupby("CNT_CHILDREN", as_index=False)["TARGET"]
            .mean()
        )

        child_default["Default Rate (%)"] = (
            child_default["TARGET"] * 100
        ).round(2)

        fig_child_default = px.bar(
            child_default,
            x="CNT_CHILDREN",
            y="Default Rate (%)",
            title="Default Rate by Number of Children",
            text="Default Rate (%)"
        )

        fig_child_default.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_child_default,
            use_container_width=True
        )

    # ========================================================
    # ROW 2
    # ========================================================
    c3, c4 = st.columns(2)

    # --------------------------------------------------------
    # Customers by Family Size
    # --------------------------------------------------------
    with c3:

        fam_size = (
            filtered_df["CNT_FAM_MEMBERS"]
            .dropna()
            .value_counts()
            .sort_index()
            .reset_index()
        )

        fam_size.columns = [
            "Family Size",
            "Customers"
        ]

        fig_fam = px.bar(
            fam_size,
            x="Family Size",
            y="Customers",
            title="Customers by Family Size",
            text="Customers"
        )

        fig_fam.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_fam,
            use_container_width=True
        )

    # --------------------------------------------------------
    # Default Rate by Family Size
    # --------------------------------------------------------
    with c4:

        fam_default = (
            filtered_df
            .dropna(subset=["CNT_FAM_MEMBERS", "TARGET"])
            .groupby("CNT_FAM_MEMBERS", as_index=False)["TARGET"]
            .mean()
        )

        fam_default["Default Rate (%)"] = (
            fam_default["TARGET"] * 100
        ).round(2)

        fig_fam_default = px.bar(
            fam_default,
            x="CNT_FAM_MEMBERS",
            y="Default Rate (%)",
            title="Default Rate by Family Size",
            text="Default Rate (%)"
        )

        fig_fam_default.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_fam_default,
            use_container_width=True
        )

    # ========================================================
    # ROW 3
    # ========================================================
    c5, c6 = st.columns(2)

    # --------------------------------------------------------
    # Applications by Family Status
    # --------------------------------------------------------
    with c5:

        app_family = (
            filtered_df["NAME_FAMILY_STATUS"]
            .value_counts()
            .reset_index()
        )

        app_family.columns = [
            "Family Status",
            "Applications"
        ]

        fig_family = px.bar(
            app_family,
            x="Family Status",
            y="Applications",
            title="Applications by Family Status",
            text="Applications"
        )

        fig_family.update_xaxes(
            tickangle=30
        )

        fig_family.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_family,
            use_container_width=True
        )

    # --------------------------------------------------------
    # Default Rate by Family Status
    # --------------------------------------------------------
    with c6:

        fam_status_default = (
            filtered_df
            .dropna(subset=[
                "NAME_FAMILY_STATUS",
                "TARGET"
            ])
            .groupby(
                "NAME_FAMILY_STATUS",
                as_index=False
            )["TARGET"]
            .mean()
        )

        fam_status_default["Default Rate (%)"] = (
            fam_status_default["TARGET"] * 100
        ).round(2)

        fig_status_default = px.bar(
            fam_status_default,
            x="NAME_FAMILY_STATUS",
            y="Default Rate (%)",
            title="Default Rate by Family Status",
            text="Default Rate (%)"
        )

        fig_status_default.update_xaxes(
            tickangle=30
        )

        fig_status_default.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig_status_default,
            use_container_width=True
        )

    # ========================================================
    # INCOME VS FAMILY SIZE
    # ========================================================
    st.subheader("💰 Income vs Family Size")

    income_family = (
        filtered_df[
            [
                "CNT_FAM_MEMBERS",
                "AMT_INCOME_TOTAL"
            ]
        ]
        .dropna()
    )

    fig_income_family = px.scatter(
        income_family,
        x="CNT_FAM_MEMBERS",
        y="AMT_INCOME_TOTAL",
        title="Income vs Family Size",
        opacity=0.6
    )

    fig_income_family.update_yaxes(
        title="Total Income"
    )

    fig_income_family.update_xaxes(
        title="Family Size"
    )

    st.plotly_chart(
        fig_income_family,
        use_container_width=True
    )

    # ========================================================
    # RISK INSIGHTS
    # ========================================================
    st.subheader("🚨 Family & Children Risk Insights")

    # Highest children default rate
    if not child_default.empty:

        highest_child_risk = (
            child_default
            .sort_values(
                "Default Rate (%)",
                ascending=False
            )
            .iloc[0]
        )

        st.info(
            f"Highest observed default rate by children count: "
            f"{int(highest_child_risk['CNT_CHILDREN'])} children "
            f"with {highest_child_risk['Default Rate (%)']:.2f}% "
            f"default rate."
        )

    # Highest family-size default rate
    if not fam_default.empty:

        highest_family_risk = (
            fam_default
            .sort_values(
                "Default Rate (%)",
                ascending=False
            )
            .iloc[0]
        )

        st.info(
            f"Highest observed default rate by family size: "
            f"{highest_family_risk['CNT_FAM_MEMBERS']:.0f} family members "
            f"with {highest_family_risk['Default Rate (%)']:.2f}% "
            f"default rate."
        )

    # Highest family status risk
    if not fam_status_default.empty:

        highest_status_risk = (
            fam_status_default
            .sort_values(
                "Default Rate (%)",
                ascending=False
            )
            .iloc[0]
        )

        st.info(
            f"Family status with the highest observed default rate: "
            f"{highest_status_risk['NAME_FAMILY_STATUS']} "
            f"({highest_status_risk['Default Rate (%)']:.2f}%)."
        )

    # ========================================================
    # SUMMARY TABLE
    # ========================================================
    st.subheader("📋 Family Risk Summary")

    summary_df = pd.DataFrame({
        "Metric": [
            "Average Children",
            "Average Family Members",
            "Customers with Children",
            "Customers without Children",
            "Highest Risk Family Type"
        ],
        "Value": [
            f"{avg_children:.2f}"
            if pd.notna(avg_children)
            else "N/A",

            f"{avg_family_members:.2f}"
            if pd.notna(avg_family_members)
            else "N/A",

            f"{customers_with_children:,}",

            f"{customers_without_children:,}",

            highest_risk_display
        ]
    })

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )


except Exception as e:

    st.error(
        "Unable to load or process the Home Credit dataset."
    )

    st.exception(e)