import pandas as pd
import streamlit as st
import plotly.express as px

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")

st.title("Housing & Asset Analysis")
st.caption(
    "Analyze property and vehicle ownership status and how it relates to credit risk."
)

try:
    # =========================================================
    # LOAD DATA
    # =========================================================
    df = load_home_credit_data()

    required = [
        "FLAG_OWN_CAR",
        "FLAG_OWN_REALTY",
        "OWN_CAR_AGE",
        "NAME_HOUSING_TYPE",
        "TARGET",
        "AMT_CREDIT",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    # =========================================================
    # SIDEBAR FILTER
    # =========================================================
    st.sidebar.subheader("Filters")

    housing_types = sorted(
        df["NAME_HOUSING_TYPE"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_housing = st.sidebar.multiselect(
        "Housing Type",
        housing_types,
        default=housing_types
    )

    filtered_df = df[
        df["NAME_HOUSING_TYPE"].isin(selected_housing)
    ].copy()

    # =========================================================
    # KPI SECTION
    # =========================================================
    st.subheader("📊 Key Performance Indicators")

    car_owners = (
        filtered_df["FLAG_OWN_CAR"] == "Y"
    ).sum()

    property_owners = (
        filtered_df["FLAG_OWN_REALTY"] == "Y"
    ).sum()

    customers_both = (
        (filtered_df["FLAG_OWN_CAR"] == "Y")
        & (filtered_df["FLAG_OWN_REALTY"] == "Y")
    ).sum()

    property_owner_df = filtered_df[
        filtered_df["FLAG_OWN_REALTY"] == "Y"
    ]

    if not property_owner_df.empty:
        property_owner_default_rate = (
            property_owner_df["TARGET"].mean() * 100
        )
    else:
        property_owner_default_rate = 0

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="🚗 Car Owners",
            value=f"{car_owners:,}"
        )

    with c2:
        st.metric(
            label="🏠 Property Owners",
            value=f"{property_owners:,}"
        )

    with c3:
        st.metric(
            label="🏡 Customers Owning Both",
            value=f"{customers_both:,}"
        )

    with c4:
        st.metric(
            label="⚠️ Default Rate of Property Owners",
            value=f"{property_owner_default_rate:.2f}%"
        )

    # =========================================================
    # VISUALIZATIONS SECTION
    # =========================================================
    st.subheader("📈 Visualizations")

    # =========================================================
    # CHART 1 & 2 - DONUT CHARTS
    # =========================================================
    c1, c2 = st.columns(2)

    # ---------------------------------------------------------
    # 1. Car Ownership Distribution - DONUT
    # ---------------------------------------------------------
    with c1:

        car_counts = (
            filtered_df["FLAG_OWN_CAR"]
            .value_counts()
            .reset_index()
        )

        car_counts.columns = [
            "Own Car",
            "Customers"
        ]

        car_counts["Ownership"] = car_counts["Own Car"].map({
            "Y": "Owns Car",
            "N": "Does Not Own Car"
        })

        fig_car = px.pie(
            car_counts,
            names="Ownership",
            values="Customers",
            hole=0.55,
            title="🚗 Car Ownership Distribution",
        )

        fig_car.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Customers: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(
            fig_car,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 2. Property Ownership Distribution - DONUT
    # ---------------------------------------------------------
    with c2:

        property_counts = (
            filtered_df["FLAG_OWN_REALTY"]
            .value_counts()
            .reset_index()
        )

        property_counts.columns = [
            "Own Realty",
            "Customers"
        ]

        property_counts["Ownership"] = property_counts[
            "Own Realty"
        ].map({
            "Y": "Owns Property",
            "N": "Does Not Own Property"
        })

        fig_property = px.pie(
            property_counts,
            names="Ownership",
            values="Customers",
            hole=0.55,
            title="🏠 Property Ownership Distribution",
        )

        fig_property.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Customers: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(
            fig_property,
            use_container_width=True
        )

    # =========================================================
    # CHART 3 & 4 - DEFAULT RATE
    # =========================================================
    c3, c4 = st.columns(2)

    # ---------------------------------------------------------
    # 3. Default Rate by Car Ownership
    # ---------------------------------------------------------
    with c3:

        car_default = (
            filtered_df
            .groupby("FLAG_OWN_CAR", as_index=False)["TARGET"]
            .mean()
        )

        car_default["Default Rate"] = (
            car_default["TARGET"] * 100
        )

        car_default["Ownership"] = car_default[
            "FLAG_OWN_CAR"
        ].map({
            "Y": "Owns Car",
            "N": "Does Not Own Car"
        })

        fig_car_default = px.bar(
            car_default,
            x="Ownership",
            y="Default Rate",
            title="⚠️ Default Rate by Car Ownership",
            text="Default Rate",
        )

        fig_car_default.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_car_default.update_yaxes(
            title="Default Rate (%)"
        )

        st.plotly_chart(
            fig_car_default,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 4. Default Rate by Property Ownership
    # ---------------------------------------------------------
    with c4:

        property_default = (
            filtered_df
            .groupby("FLAG_OWN_REALTY", as_index=False)["TARGET"]
            .mean()
        )

        property_default["Default Rate"] = (
            property_default["TARGET"] * 100
        )

        property_default["Ownership"] = property_default[
            "FLAG_OWN_REALTY"
        ].map({
            "Y": "Owns Property",
            "N": "Does Not Own Property"
        })

        fig_property_default = px.bar(
            property_default,
            x="Ownership",
            y="Default Rate",
            title="⚠️ Default Rate by Property Ownership",
            text="Default Rate",
        )

        fig_property_default.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_property_default.update_yaxes(
            title="Default Rate (%)"
        )

        st.plotly_chart(
            fig_property_default,
            use_container_width=True
        )

    # =========================================================
    # CHART 5 & 6 - HOUSING TYPE
    # =========================================================
    c5, c6 = st.columns(2)

    # ---------------------------------------------------------
    # 5. Applicants by Housing Type - HORIZONTAL BAR
    # ---------------------------------------------------------
    with c5:

        housing_counts = (
            filtered_df["NAME_HOUSING_TYPE"]
            .value_counts()
            .reset_index()
        )

        housing_counts.columns = [
            "Housing Type",
            "Applications"
        ]

        housing_counts = housing_counts.sort_values(
            "Applications"
        )

        fig_housing = px.bar(
            housing_counts,
            x="Applications",
            y="Housing Type",
            orientation="h",
            title="🏠 Applicants by Housing Type",
            text="Applications",
        )

        fig_housing.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        st.plotly_chart(
            fig_housing,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # 6. Default Rate by Housing Type - LINE
    # ---------------------------------------------------------
    with c6:

        housing_default = (
            filtered_df
            .groupby("NAME_HOUSING_TYPE", as_index=False)["TARGET"]
            .mean()
        )

        housing_default["Default Rate"] = (
            housing_default["TARGET"] * 100
        )

        housing_default = housing_default.sort_values(
            "Default Rate"
        )

        fig_housing_default = px.line(
            housing_default,
            x="NAME_HOUSING_TYPE",
            y="Default Rate",
            title="📉 Default Rate by Housing Type",
            markers=True,
            text="Default Rate",
        )

        fig_housing_default.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="top center"
        )

        fig_housing_default.update_yaxes(
            title="Default Rate (%)"
        )

        fig_housing_default.update_layout(
            xaxis_tickangle=-30
        )

        st.plotly_chart(
            fig_housing_default,
            use_container_width=True
        )

    # =========================================================
    # CHART 7 - AVERAGE CREDIT
    # =========================================================
    housing_credit = (
        filtered_df
        .groupby("NAME_HOUSING_TYPE", as_index=False)["AMT_CREDIT"]
        .mean()
    )

    housing_credit = housing_credit.rename(
        columns={
            "AMT_CREDIT": "Average Credit"
        }
    )

    # ---------------------------------------------------------
    # Treemap
    # ---------------------------------------------------------
    fig_credit = px.treemap(
        housing_credit,
        path=["NAME_HOUSING_TYPE"],
        values="Average Credit",
        title="💳 Average Credit by Housing Type",
    )

    fig_credit.update_traces(
        texttemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f}"
        )
    )

    st.plotly_chart(
        fig_credit,
        use_container_width=True
    )

except Exception as e:
    st.error(
        "Unable to load or process the Home Credit dataset."
    )
    st.exception(e)