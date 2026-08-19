import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.page_helpers import load_home_credit_data

st.set_page_config(layout="wide")
st.title("Missing Value Analysis")
st.caption("Understand data quality and missingness before machine-learning modeling.")

try:
    df = load_home_credit_data()

    # ============================================================
    # SIDEBAR OPTIONS
    # ============================================================
    st.sidebar.subheader("Options")

    threshold = st.sidebar.slider(
        "Highlight columns with missing data above %",
        0,
        100,
        50
    )

    # ============================================================
    # BASIC DATASET INFORMATION
    # ============================================================
    total_rows = df.shape[0]
    total_columns = df.shape[1]
    total_missing = int(df.isna().sum().sum())
    columns_with_missing = int((df.isna().sum() > 0).sum())
    columns_over_threshold = int(
        (df.isna().mean() * 100 > threshold).sum()
    )

    st.subheader("📊 Key Charts")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Rows", f"{total_rows:,}")
    c2.metric("Total Columns", f"{total_columns:,}")
    c3.metric("Total Missing Values", f"{total_missing:,}")
    c4.metric("Columns with Missing Values", f"{columns_with_missing:,}")

    c5, c6 = st.columns(2)

    c5.metric(
        f"Columns with >{threshold}% Missing Data",
        f"{columns_over_threshold:,}"
    )

    c6.metric(
        "Overall Missing %",
        f"{(total_missing / (total_rows * total_columns) * 100):.2f}%"
    )

    # ============================================================
    # MISSING VALUE SUMMARY
    # ============================================================
    missing_summary = df.isna().sum().reset_index()

    missing_summary.columns = [
        "Column",
        "Missing Count"
    ]

    missing_summary["Missing %"] = (
        missing_summary["Missing Count"] / total_rows * 100
    ).round(2)

    missing_summary["Data Type"] = (
        df.dtypes.reset_index(drop=True)
        .astype(str)
        .values
    )

    missing_summary = missing_summary.sort_values(
        ["Missing Count", "Column"],
        ascending=[False, True]
    ).reset_index(drop=True)

    # ============================================================
    # IMPORTANT ACTION LOGIC
    # ============================================================
    def determine_action(column, missing_pct, dtype):
        """
        Decide what action should be taken for missing values.
        """

        # --------------------------------------------------------
        # 1. No missing values
        # --------------------------------------------------------
        if missing_pct == 0:
            return "No Action"

        # --------------------------------------------------------
        # 2. Very high missing values
        # --------------------------------------------------------
        if missing_pct > 50:
            return "Drop"

        # --------------------------------------------------------
        # Numeric columns
        # --------------------------------------------------------
        if dtype in [
            "int64",
            "int32",
            "float64",
            "float32"
        ]:

            # More than 30% missing:
            # Create missing indicator + median imputation
            if missing_pct > 30:
                return "Create Missing Indicator"

            # Between 10% and 30%:
            # Median is safer for skewed financial data
            elif missing_pct >= 10:
                return "Fill with Median"

            # Less than 10%:
            # Mean is acceptable for small missingness
            else:
                return "Fill with Mean"

        # --------------------------------------------------------
        # Categorical columns
        # --------------------------------------------------------
        if dtype == "object":

            # High categorical missingness
            if missing_pct > 30:
                return 'Fill with "Unknown"'

            # Moderate missingness
            elif missing_pct >= 10:
                return "Fill with Mode"

            # Low missingness
            else:
                return "Fill with Mode"

        # --------------------------------------------------------
        # Other data types
        # --------------------------------------------------------
        return "Create Missing Indicator"

    # Apply action to every column
    missing_summary["Important Action"] = missing_summary.apply(
        lambda row: determine_action(
            row["Column"],
            row["Missing %"],
            row["Data Type"]
        ),
        axis=1
    )

    # ============================================================
    # TOP MISSING VALUE CHART
    # ============================================================
    st.subheader("📈 Missing Value Charts")

    top_missing = missing_summary.head(20)

    fig_bar = px.bar(
        top_missing,
        x="Column",
        y="Missing Count",
        title="Top 20 Columns with Missing Values",
        color="Missing Count",
        color_continuous_scale="Blues"
    )

    fig_bar.update_xaxes(tickangle=45)

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # ============================================================
    # MISSING PERCENTAGE CHART
    # ============================================================
    fig_pct = px.bar(
        missing_summary.head(20),
        x="Column",
        y="Missing %",
        title="Missing Percentage by Column",
        color="Missing %",
        color_continuous_scale="Viridis"
    )

    fig_pct.update_xaxes(tickangle=45)

    st.plotly_chart(
        fig_pct,
        use_container_width=True
    )

    # ============================================================
    # HEATMAP
    # ============================================================
    heatmap_df = df.isna().astype(int)

    fig_heat = px.imshow(
        heatmap_df.iloc[
            :,
            :min(30, heatmap_df.shape[1])
        ],
        color_continuous_scale="Blues",
        title="Missing Values Heatmap"
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True
    )

    # ============================================================
    # MISSING VALUES BY DATA TYPE
    # ============================================================
    type_summary = (
        missing_summary
        .groupby("Data Type", as_index=False)["Missing Count"]
        .sum()
    )

    fig_type = px.bar(
        type_summary,
        x="Data Type",
        y="Missing Count",
        title="Missing Values by Data Type",
        text="Missing Count",
        color="Data Type"
    )

    st.plotly_chart(
        fig_type,
        use_container_width=True
    )

    # ============================================================
    # MISSING DATA DETAIL TABLE
    # ============================================================
    st.subheader("📋 Missing Data Detail Table")

    st.dataframe(
        missing_summary,
        use_container_width=True,
        hide_index=True
    )

    # ============================================================
    # IMPORTANT ACTIONS
    # ============================================================
    st.subheader("🚨 Important Actions")

    st.write(
        "For each column, the dashboard recommends the most suitable "
        "missing-value treatment before machine-learning modeling."
    )

    # ------------------------------------------------------------
    # Action Summary
    # ------------------------------------------------------------
    action_summary = (
        missing_summary["Important Action"]
        .value_counts()
        .reset_index()
    )

    action_summary.columns = [
        "Action",
        "Number of Columns"
    ]

    st.markdown("### Action Summary")

    a1, a2, a3 = st.columns(3)

    action_counts = dict(
        zip(
            action_summary["Action"],
            action_summary["Number of Columns"]
        )
    )

    a1.metric(
        "Drop",
        action_counts.get("Drop", 0)
    )

    a2.metric(
        "Mean / Median",
        action_counts.get("Fill with Mean", 0)
        + action_counts.get("Fill with Median", 0)
    )

    a3.metric(
        "Mode / Unknown",
        action_counts.get("Fill with Mode", 0)
        + action_counts.get('Fill with "Unknown"', 0)
    )

    # ============================================================
    # ACTION DISTRIBUTION CHART
    # ============================================================
    fig_action = px.bar(
        action_summary,
        x="Action",
        y="Number of Columns",
        title="Recommended Missing-Value Actions",
        text="Number of Columns",
        color="Action"
    )

    fig_action.update_xaxes(tickangle=30)

    st.plotly_chart(
        fig_action,
        use_container_width=True
    )

    # ============================================================
    # COLUMN-WISE IMPORTANT ACTIONS
    # ============================================================
    st.markdown("### Column-wise Important Actions")

    action_filter = st.multiselect(
        "Filter by Action",
        options=[
            "Drop",
            "Fill with Mean",
            "Fill with Median",
            "Fill with Mode",
            'Fill with "Unknown"',
            "Create Missing Indicator",
            "No Action"
        ],
        default=[
            "Drop",
            "Fill with Mean",
            "Fill with Median",
            "Fill with Mode",
            'Fill with "Unknown"',
            "Create Missing Indicator"
        ]
    )

    filtered_actions = missing_summary[
        missing_summary["Important Action"].isin(action_filter)
    ]

    st.dataframe(
        filtered_actions[
            [
                "Column",
                "Missing Count",
                "Missing %",
                "Data Type",
                "Important Action"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ============================================================
    # DETAILED ACTION EXPLANATION
    # ============================================================
    st.markdown("### 🔎 Action Details")

    for _, row in missing_summary.iterrows():

        col = row["Column"]
        missing_count = row["Missing Count"]
        missing_pct = row["Missing %"]
        dtype = row["Data Type"]
        action = row["Important Action"]

        # Skip columns with no missing values unless needed
        if action == "No Action":
            continue

        with st.expander(
            f"{col}  →  {action}"
        ):

            st.write(
                f"**Missing Count:** {missing_count:,}"
            )

            st.write(
                f"**Missing Percentage:** {missing_pct:.2f}%"
            )

            st.write(
                f"**Data Type:** {dtype}"
            )

            st.write(
                f"**Recommended Action:** {action}"
            )

            # Explanation
            if action == "Drop":

                st.info(
                    "The column has more than 50% missing values. "
                    "Dropping the column can reduce noise and avoid "
                    "unreliable imputation."
                )

            elif action == "Fill with Mean":

                st.info(
                    "The column is numeric and has a relatively small "
                    "percentage of missing values. Mean imputation can "
                    "be used when the distribution is reasonably balanced."
                )

            elif action == "Fill with Median":

                st.info(
                    "Median imputation is recommended for numeric data "
                    "with moderate missingness, especially when the data "
                    "may contain outliers or be skewed."
                )

            elif action == "Fill with Mode":

                st.info(
                    "The column is categorical. The most frequent category "
                    "can be used to replace missing values."
                )

            elif action == 'Fill with "Unknown"':

                st.info(
                    'Missing categorical values may contain useful information. '
                    'Replacing them with "Unknown" preserves the rows without '
                    "forcing them into an existing category."
                )

            elif action == "Create Missing Indicator":

                st.info(
                    "Create an additional binary column such as "
                    f"{col}_Missing where 1 means the original value "
                    "was missing and 0 means it was available. "
                    "The original missing value can then be imputed."
                )

    # ============================================================
    # DOWNLOAD ACTION REPORT
    # ============================================================
    st.markdown("### 📥 Download Missing Value Action Report")

    csv_data = missing_summary.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Action Report CSV",
        data=csv_data,
        file_name="home_credit_missing_value_actions.csv",
        mime="text/csv"
    )

except Exception as e:

    st.error(
        "Unable to load or process the Home Credit dataset."
    )

    st.exception(e)