import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.page_helpers import load_home_credit_data
from utils.kpis import calc_kpis, get_default_summary


st.header("📊 Executive Overview")
st.caption("Management summary of applicant volume, credit demand, and portfolio default risk.")


def format_currency(value: float | int | pd.Series | None) -> str:
    if value is None or pd.isna(value):
        return "$0"
    return f"${float(value):,.0f}"


def build_applicant_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly trend when a date-like column exists; otherwise show the overall portfolio summary."""
    date_candidates = [
        col for col in df.columns
        if "DATE" in col.upper() or "MONTH" in col.upper() or col.upper() in {"APPR_PROCESS_DAY"}
    ]

    if date_candidates:
        date_col = None
        for col in [
            "DATE_APPLICATION",
            "DATE_DECISION",
            "DATE_REGISTRATION",
            "DAYS_REGISTRATION",
            "DAYS_DECISION",
            "APPR_PROCESS_DAY",
            "MONTHS_BALANCE",
        ]:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            date_col = date_candidates[0]

        try:
            converted = pd.to_datetime(df[date_col], errors="coerce")
            if not converted.dropna().empty:
                summary = (
                    df.assign(_period=converted)
                    .groupby(pd.Grouper(key="_period", freq="M"))
                    .agg(
                        Applications=("SK_ID_CURR", "count"),
                        Defaults=("TARGET", lambda s: int((s == 1).sum())),
                    )
                    .reset_index()
                    .rename(columns={"_period": "Period"})
                )
                summary["Default Rate %"] = (summary["Defaults"] / summary["Applications"] * 100).round(2)
                return summary
        except Exception:
            pass

    return pd.DataFrame(
        {
            "Period": ["Overall"],
            "Applications": [len(df)],
            "Defaults": [int((df["TARGET"] == 1).sum())],
            "Default Rate %": [round((df["TARGET"].mean() * 100), 2)],
        }
    )


try:
    df = load_home_credit_data()
    metrics = calc_kpis(df)
    default_summary = get_default_summary(df)
    applicant_summary = build_applicant_summary(df)

    default_rate = metrics["default_rate"]
    if default_rate < 8:
        portfolio_health = "Low risk"
        health_color = "#22c55e"
    elif default_rate < 15:
        portfolio_health = "Moderate risk"
        health_color = "#f59e0b"
    else:
        portfolio_health = "Elevated risk"
        health_color = "#ef4444"

    st.markdown(
        f"""
        <div style="background: linear-gradient(90deg, #0f172a 0%, #1d4ed8 100%); padding: 1rem 1.2rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
            <strong>Portfolio Health:</strong> <span style="color: {health_color}; font-weight: 700;">{portfolio_health}</span>
            &nbsp;•&nbsp; Default rate is <strong>{default_rate:.2f}%</strong> across the current applicant base.
        </div>
        """,
        unsafe_allow_html=True,
    )

    risk_signal = min(max((default_rate / 25) * 100, 5), 100)
    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #dfe7f1; border-radius: 12px; padding: 0.8rem 1rem; margin: 0.8rem 0 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <strong style="font-size: 1rem; color: #0f172a;">Risk Signal</strong>
                <span style="font-weight: 700; color: {health_color};">{portfolio_health}</span>
            </div>
            <div style="height: 10px; background: #e2e8f0; border-radius: 999px; margin-top: 0.6rem; overflow: hidden;">
                <div style="height: 100%; width: {risk_signal}%; background: linear-gradient(90deg, #22c55e 0%, #f59e0b 55%, #ef4444 100%); border-radius: 999px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("KPI Cards")
    st.caption("These core metrics summarize portfolio size, credit exposure, and default risk across the current applicant population.")
    kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)
    kpi_col_1.metric("Total Applications", f"{metrics['total_applications']:,}")
    kpi_col_2.metric("Total Default Customers", f"{metrics['total_defaults']:,}")
    kpi_col_3.metric("Total Non-Default Customers", f"{metrics['total_non_defaults']:,}")
    kpi_col_4.metric("Default Rate %", f"{metrics['default_rate']:.2f}%")

    kpi_col_5, kpi_col_6, kpi_col_7, kpi_col_8 = st.columns(4)
    kpi_col_5.metric("Total Credit Amount", format_currency(metrics["total_credit"]))
    kpi_col_6.metric("Average Credit Amount", format_currency(metrics["avg_credit"]))
    kpi_col_7.metric("Average Income", format_currency(metrics["avg_income"]))
    kpi_col_8.metric("Average Annuity", format_currency(metrics["avg_annuity"]))

    st.divider()

    st.subheader("📈 Visualizations")
    st.caption("This section highlights portfolio mix, borrower profile, and credit demand trends using different charts to make the portfolio story easier to interpret.")

    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        default_counts = df["TARGET"].value_counts().rename(index={0: "Non-Default", 1: "Default"}).reset_index()
        default_counts.columns = ["Customer Type", "Count"]
        fig_default = px.pie(
            default_counts,
            names="Customer Type",
            values="Count",
            title="Default vs Non-Default Customers",
            hole=0.45,
            color_discrete_sequence=["#14b8a6", "#f97316"],
        )
        fig_default.update_traces(textinfo="percent+label", pull=[0.03, 0.02])
        st.plotly_chart(fig_default, use_container_width=True)

    with chart_col_2:
        gender_counts = df.groupby("CODE_GENDER")["SK_ID_CURR"].count().reset_index(name="Applications")
        fig_gender = px.bar(
            gender_counts,
            x="CODE_GENDER",
            y="Applications",
            title="Total Applications by Gender",
            color="CODE_GENDER",
            text="Applications",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_gender.update_layout(showlegend=False)
        st.plotly_chart(fig_gender, use_container_width=True)

    chart_col_3, chart_col_4 = st.columns(2)
    with chart_col_3:
        contract_counts = df.groupby("NAME_CONTRACT_TYPE")["SK_ID_CURR"].count().reset_index(name="Applications")
        fig_contract = px.bar(
            contract_counts,
            x="Applications",
            y="NAME_CONTRACT_TYPE",
            orientation="h",
            title="Applications by Contract Type",
            color="NAME_CONTRACT_TYPE",
            text="Applications",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_contract.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_contract, use_container_width=True)

    with chart_col_4:
        income_counts = df.groupby("NAME_INCOME_TYPE")["SK_ID_CURR"].count().reset_index(name="Applications")
        fig_income = px.bar(
            income_counts,
            x="Applications",
            y="NAME_INCOME_TYPE",
            orientation="h",
            title="Applications by Income Type",
            color="NAME_INCOME_TYPE",
            text="Applications",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_income.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_income, use_container_width=True)

    chart_col_5, chart_col_6 = st.columns([2, 1])
    with chart_col_5:
        credit_data = df["AMT_CREDIT"].dropna()
        fig_credit = px.histogram(
            credit_data,
            x=credit_data,
            nbins=40,
            title="Credit Amount Distribution",
            color_discrete_sequence=["#60a5fa"],
        )
        fig_credit.update_layout(hovermode="x unified")
        st.plotly_chart(fig_credit, use_container_width=True)

    with chart_col_6:
        if "Period" in applicant_summary.columns and len(applicant_summary) > 1:
            fig_summary = px.line(
                applicant_summary,
                x="Period",
                y="Applications",
                title="Monthly Applicant Summary",
                markers=True,
                color_discrete_sequence=["#2563eb"],
            )
        else:
            fig_summary = px.bar(
                applicant_summary,
                x="Period",
                y="Applications",
                title="Overall Applicant Summary",
                text="Applications",
                color_discrete_sequence=["#2563eb"],
            )
        st.plotly_chart(fig_summary, use_container_width=True)

    st.divider()

    st.subheader("🔎 Important Insights")
    st.caption("These highlights summarize the most relevant portfolio findings for management review and action planning.")

    insight_cards = [
        {
            "title": "Default Rate",
            "value": f"{default_summary['default_rate']:.2f}%",
            "caption": "Share of applicants currently showing default behavior in this portfolio view.",
            "bg": "linear-gradient(135deg, #0f172a 0%, #3b82f6 100%)",
            "tone": "#e0f2fe",
        },
        {
            "title": "Average Income",
            "value": format_currency(metrics["avg_income"]),
            "caption": "Typical affordability level across the applicant base for repayment capacity checks.",
            "bg": "linear-gradient(135deg, #14532d 0%, #22c55e 100%)",
            "tone": "#dcfce7",
        },
        {
            "title": "Average Loan Amount",
            "value": format_currency(metrics["avg_credit"]),
            "caption": "Average credit request size relative to customer income and portfolio mix.",
            "bg": "linear-gradient(135deg, #7c2d12 0%, #f59e0b 100%)",
            "tone": "#fef3c7",
        },
        {
            "title": "Most Common Income Type",
            "value": default_summary["most_common_income"],
            "caption": "Largest income segment driving application demand and borrower mix.",
            "bg": "linear-gradient(135deg, #4c1d95 0%, #a78bfa 100%)",
            "tone": "#ede9fe",
        },
        {
            "title": "Most Common Education Level",
            "value": default_summary["most_common_education"],
            "caption": "Profile trend that helps explain borrower readiness and risk behavior.",
            "bg": "linear-gradient(135deg, #0f766e 0%, #2dd4bf 100%)",
            "tone": "#ccfbf1",
        },
        {
            "title": "Highest Risk Segment",
            "value": default_summary["highest_risk_segment"],
            "caption": "Customer group with the strongest concentration of default risk in the portfolio.",
            "bg": "linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%)",
            "tone": "#fee2e2",
        },
    ]

    for idx in range(0, len(insight_cards), 3):
        cols = st.columns(3)
        for i, card in enumerate(insight_cards[idx: idx + 3]):
            with cols[i]:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: {card['bg']}; border-radius: 16px; padding: 1.1rem 1rem; color: white; min-height: 130px; margin-bottom: 0.75rem; cursor: pointer;">
                            <div style="font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.9; color: {card['tone']};">{card['title']}</div>
                            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.7rem; line-height: 1.2;">{card['value']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.expander("", expanded=False):
                        st.write(card["caption"])

    st.markdown("---")

    with st.expander("🧭 Executive Summary", expanded=True):
        st.markdown("This summary combines the portfolio risk signal, affordability profile, and business mix into a simple management view.")

        snapshot_df = pd.DataFrame(
            {
                "Metric": [
                    "Total Applications",
                    "Default Rate %",
                    "Average Income",
                    "Average Credit Amount",
                    "Most Common Income Type",
                    "Most Common Education Level",
                    "Highest Risk Segment",
                ],
                "Value": [
                    f"{metrics['total_applications']:,}",
                    f"{default_summary['default_rate']:.2f}%",
                    format_currency(metrics['avg_income']),
                    format_currency(metrics['avg_credit']),
                    default_summary['most_common_income'],
                    default_summary['most_common_education'],
                    default_summary['highest_risk_segment'],
                ],
            }
        )
        st.dataframe(snapshot_df, hide_index=True, use_container_width=True)

        st.markdown(
            "**Key Recommendation:** The portfolio's **{default_rate:.2f}% default rate** indicates {risk_assessment}. "
            "Focus retention and monitoring efforts on **{risk_segment}** customers, as they represent the highest concentration of defaults. "
            "The loan-to-income ratio suggests borrowers have moderate afford inability capacity; ensure ongoing income verification is part of your risk management protocol.".format(
                default_rate=default_rate,
                risk_assessment="moderate risk levels" if default_rate < 15 else "elevated risk that requires immediate action",
                risk_segment=default_summary['highest_risk_segment'],
            )
        )

    with st.expander("📉 Segment Risk Table", expanded=False):
        segment_df = (
            df.groupby("NAME_INCOME_TYPE")
            .agg(
                Applications=("SK_ID_CURR", "count"),
                Defaults=("TARGET", lambda s: int((s == 1).sum())),
            )
            .reset_index()
        )
        segment_df["Default Rate %"] = (segment_df["Defaults"] / segment_df["Applications"] * 100).round(2)
        segment_df = segment_df.sort_values("Applications", ascending=False).head(10)
        st.dataframe(segment_df, hide_index=True, use_container_width=True)

    st.divider()

    st.subheader("🔍 Filtered Data View")
    st.caption("Filter the portfolio data by key dimensions to analyze specific customer segments.")

    filter_col_1, filter_col_2, filter_col_3 = st.columns(3)
    with filter_col_1:
        selected_income = st.multiselect(
            "Filter by Income Type",
            options=df["NAME_INCOME_TYPE"].unique(),
            default=df["NAME_INCOME_TYPE"].unique(),
        )
    with filter_col_2:
        selected_gender = st.multiselect(
            "Filter by Gender",
            options=df["CODE_GENDER"].unique(),
            default=df["CODE_GENDER"].unique(),
        )
    with filter_col_3:
        selected_education = st.multiselect(
            "Filter by Education",
            options=df["NAME_EDUCATION_TYPE"].unique(),
            default=df["NAME_EDUCATION_TYPE"].unique(),
        )

    filtered_df = df[
        (df["NAME_INCOME_TYPE"].isin(selected_income))
        & (df["CODE_GENDER"].isin(selected_gender))
        & (df["NAME_EDUCATION_TYPE"].isin(selected_education))
    ]

    st.markdown(f"**Filtered Portfolio:** {len(filtered_df):,} applications")

    filtered_kpi_col_1, filtered_kpi_col_2, filtered_kpi_col_3, filtered_kpi_col_4 = st.columns(4)
    filtered_defaults = int((filtered_df["TARGET"] == 1).sum())
    filtered_non_defaults = int((filtered_df["TARGET"] == 0).sum())
    filtered_default_rate = (filtered_defaults / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    filtered_avg_income = filtered_df["AMT_INCOME_TOTAL"].mean() if len(filtered_df) > 0 else 0

    filtered_kpi_col_1.metric("Filtered Applications", f"{len(filtered_df):,}")
    filtered_kpi_col_2.metric("Filtered Defaults", f"{filtered_defaults:,}")
    filtered_kpi_col_3.metric("Default Rate %", f"{filtered_default_rate:.2f}%")
    filtered_kpi_col_4.metric("Avg Income", format_currency(filtered_avg_income))

    with st.expander("📋 Filtered Data Table", expanded=False):
        st.dataframe(filtered_df.head(100), use_container_width=True)

except Exception as e:
    st.error("Dataset not found or invalid.")
    st.caption(str(e))