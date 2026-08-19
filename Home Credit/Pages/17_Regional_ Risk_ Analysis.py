import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")

st.title("Regional Risk Analysis")
st.caption(
    "Analyze whether customer location characteristics affect default risk."
)

try:
    # =========================================================
    # LOAD DATA
    # =========================================================
    df = load_home_credit_data()

    required = [
        "REGION_POPULATION_RELATIVE",
        "REGION_RATING_CLIENT",
        "REGION_RATING_CLIENT_W_CITY",
        "REG_REGION_NOT_LIVE_REGION",
        "REG_REGION_NOT_WORK_REGION",
        "REG_CITY_NOT_LIVE_CITY",
        "REG_CITY_NOT_WORK_CITY",
        "TARGET",
        "AMT_CREDIT",
        "AMT_INCOME_TOTAL",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
    ]

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}"
        )

    # =========================================================
    # SIDEBAR FILTER
    # =========================================================
    st.sidebar.subheader("Filters")

    rating_options = sorted(
        df["REGION_RATING_CLIENT"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_ratings = st.sidebar.multiselect(
        "Region Rating",
        rating_options,
        default=rating_options
    )

    filtered_df = df[
        df["REGION_RATING_CLIENT"].isin(
            selected_ratings
        )
    ].copy()

    # =========================================================
    # KPI SECTION
    # =========================================================
    st.subheader("📊 Key Performance Indicators")

    if not filtered_df.empty:

        most_common_rating = (
            filtered_df["REGION_RATING_CLIENT"]
            .mode()
            .iloc[0]
        )

        rating_risk = (
            filtered_df
            .groupby("REGION_RATING_CLIENT")["TARGET"]
            .mean()
        )

        if not rating_risk.empty:
            highest_risk_rating = rating_risk.idxmax()
        else:
            highest_risk_rating = "N/A"

        avg_population_indicator = (
            filtered_df[
                "REGION_POPULATION_RELATIVE"
            ].mean()
        )

    else:

        most_common_rating = "N/A"
        highest_risk_rating = "N/A"
        avg_population_indicator = 0

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🌍 Most Common Region Rating",
            most_common_rating
        )

    with c2:
        st.metric(
            "⚠️ Highest Risk Region Rating",
            highest_risk_rating
        )

    with c3:
        st.metric(
            "👥 Average Regional Population Indicator",
            f"{avg_population_indicator:.3f}"
        )

    # =========================================================
    # VISUALIZATIONS
    # =========================================================
    st.subheader("📈 Visualizations")

    # =========================================================
    # CHART 1 & 2
    # =========================================================
    c1, c2 = st.columns(2)

    # ---------------------------------------------------------
    # 1. Customers by Region Rating
    # DONUT CHART
    # ---------------------------------------------------------
    with c1:

        rating_counts = (
            filtered_df[
                "REGION_RATING_CLIENT"
            ]
            .value_counts()
            .reset_index()
        )

        rating_counts.columns = [
            "Region Rating",
            "Customers"
        ]

        fig_ratings = px.pie(
            rating_counts,
            names="Region Rating",
            values="Customers",
            hole=0.55,
            title="🌍 Customers by Region Rating"
        )

        fig_ratings.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "<b>Region Rating %{label}</b><br>"
                "Customers: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(
            fig_ratings,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 2. Default Rate by Region Rating
    # LINE CHART
    # ---------------------------------------------------------
    with c2:

        rating_default = (
            filtered_df
            .groupby(
                "REGION_RATING_CLIENT",
                as_index=False
            )["TARGET"]
            .mean()
        )

        rating_default["Default Rate"] = (
            rating_default["TARGET"] * 100
        )

        fig_default = px.line(
            rating_default,
            x="REGION_RATING_CLIENT",
            y="Default Rate",
            title="📉 Default Rate by Region Rating",
            markers=True,
            text="Default Rate"
        )

        fig_default.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="top center"
        )

        fig_default.update_layout(
            xaxis_title="Region Rating",
            yaxis_title="Default Rate (%)"
        )

        st.plotly_chart(
            fig_default,
            use_container_width=True
        )

    # =========================================================
    # CHART 3 & 4
    # =========================================================
    c3, c4 = st.columns(2)

    # ---------------------------------------------------------
    # 3. Credit Distribution by Region Rating
    # BOX PLOT
    # ---------------------------------------------------------
    with c3:

        credit_by_rating = filtered_df[
            [
                "REGION_RATING_CLIENT",
                "AMT_CREDIT"
            ]
        ].dropna()

        fig_credit = px.box(
            credit_by_rating,
            x="REGION_RATING_CLIENT",
            y="AMT_CREDIT",
            title="💳 Credit Amount Distribution by Region Rating",
            points=False
        )

        fig_credit.update_layout(
            xaxis_title="Region Rating",
            yaxis_title="Credit Amount"
        )

        st.plotly_chart(
            fig_credit,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 4. Income Distribution by Region Rating
    # BOX PLOT
    # ---------------------------------------------------------
    with c4:

        income_by_rating = filtered_df[
            [
                "REGION_RATING_CLIENT",
                "AMT_INCOME_TOTAL"
            ]
        ].dropna()

        fig_income = px.box(
            income_by_rating,
            x="REGION_RATING_CLIENT",
            y="AMT_INCOME_TOTAL",
            title="💰 Income Distribution by Region Rating",
            points=False
        )

        fig_income.update_layout(
            xaxis_title="Region Rating",
            yaxis_title="Income"
        )

        st.plotly_chart(
            fig_income,
            use_container_width=True
        )

    # =========================================================
    # EXTERNAL CREDIT SCORE ANALYSIS
    # =========================================================
    st.markdown("### 💳 External Credit Score vs Default Risk")

    # Calculate average external score
    filtered_df["AVG_EXTERNAL_SCORE"] = filtered_df[
        [
            "EXT_SOURCE_1",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3"
        ]
    ].mean(axis=1)

    # Keep customers with at least one external score
    external_score_df = filtered_df[
        filtered_df["AVG_EXTERNAL_SCORE"].notna()
    ].copy()

    if not external_score_df.empty:

        # -----------------------------------------------------
        # MEDIAN THRESHOLD
        # -----------------------------------------------------
        score_threshold = (
            external_score_df[
                "AVG_EXTERNAL_SCORE"
            ].median()
        )

        # -----------------------------------------------------
        # HIGH / LOW SCORE GROUP
        # -----------------------------------------------------
        external_score_df["External Score Group"] = (
            external_score_df["AVG_EXTERNAL_SCORE"]
            .apply(
                lambda x:
                "High External Score"
                if x >= score_threshold
                else "Low External Score"
            )
        )

        # -----------------------------------------------------
        # DEFAULT RATE
        # -----------------------------------------------------
        external_default = (
            external_score_df
            .groupby(
                "External Score Group",
                as_index=False
            )["TARGET"]
            .mean()
        )

        external_default["Default Rate"] = (
            external_default["TARGET"] * 100
        )

        # Ensure desired order
        group_order = [
            "Low External Score",
            "High External Score"
        ]

        external_default["External Score Group"] = pd.Categorical(
            external_default["External Score Group"],
            categories=group_order,
            ordered=True
        )

        external_default = (
            external_default
            .sort_values("External Score Group")
        )

        # -----------------------------------------------------
        # CHART
        # -----------------------------------------------------
        fig_external = px.bar(
            external_default,
            x="External Score Group",
            y="Default Rate",
            title="⚠️ Default Rate: High vs Low External Score",
            text="Default Rate",
            color="External Score Group"
        )

        fig_external.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_external.update_layout(
            xaxis_title="External Score Group",
            yaxis_title="Default Rate (%)",
            showlegend=False
        )

        st.plotly_chart(
            fig_external,
            use_container_width=True
        )

        st.caption(
            f"High and Low External Score groups are classified "
            f"using the median Average External Score "
            f"({score_threshold:.3f}) as the threshold."
        )

    else:

        st.warning(
            "No external credit score data is available "
            "for the selected filters."
        )

    # =========================================================
    # LOCATION MISMATCH ANALYSIS
    # =========================================================
    st.markdown("### 📍 Location Mismatch Analysis")

    mismatch_cols = [
        (
            "REG_REGION_NOT_LIVE_REGION",
            "Region Mismatch"
        ),
        (
            "REG_REGION_NOT_WORK_REGION",
            "Work Region Mismatch"
        ),
        (
            "REG_CITY_NOT_LIVE_CITY",
            "City Mismatch"
        ),
        (
            "REG_CITY_NOT_WORK_CITY",
            "Work City Mismatch"
        ),
    ]

    # =========================================================
    # MISMATCH CHARTS
    # =========================================================
    for i in range(0, len(mismatch_cols), 2):

        c1, c2 = st.columns(2)

        # -----------------------------------------------------
        # LEFT CHART
        # -----------------------------------------------------
        col, label = mismatch_cols[i]

        with c1:

            summary = (
                filtered_df
                .groupby(
                    col,
                    as_index=False
                )["TARGET"]
                .mean()
            )

            summary["Default Rate"] = (
                summary["TARGET"] * 100
            )

            summary["Status"] = summary[col].map({
                0: "No Mismatch",
                1: "Mismatch"
            })

            fig = px.bar(
                summary,
                x="Status",
                y="Default Rate",
                title=f"⚠️ {label} vs Default",
                text="Default Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Location Status",
                yaxis_title="Default Rate (%)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------------------------------
        # RIGHT CHART
        # -----------------------------------------------------
        if i + 1 < len(mismatch_cols):

            col, label = mismatch_cols[i + 1]

            with c2:

                summary = (
                    filtered_df
                    .groupby(
                        col,
                        as_index=False
                    )["TARGET"]
                    .mean()
                )

                summary["Default Rate"] = (
                    summary["TARGET"] * 100
                )

                summary["Status"] = summary[col].map({
                    0: "No Mismatch",
                    1: "Mismatch"
                })

                fig = px.bar(
                    summary,
                    x="Status",
                    y="Default Rate",
                    title=f"⚠️ {label} vs Default",
                    text="Default Rate"
                )

                fig.update_traces(
                    texttemplate="%{text:.2f}%",
                    textposition="outside"
                )

                fig.update_layout(
                    xaxis_title="Location Status",
                    yaxis_title="Default Rate (%)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

except Exception as e:

    st.error(
        "Unable to load or process the Home Credit dataset."
    )

    st.exception(e)