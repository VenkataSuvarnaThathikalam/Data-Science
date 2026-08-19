import streamlit as st
from utils.page_helpers import load_home_credit_data

st.set_page_config(
    page_title="Home Credit Default Risk Dashboard",
    page_icon=":credit_card:",
    layout="wide",
)

st.title("💳 Home Credit Default Risk Dashboard")
st.caption("Interactive Dashboard for Loan Applicant Risk Analysis")

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #0b3d91 0%, #2563eb 100%); padding: 1.2rem 1.5rem; border-radius: 0.8rem; color: white;">
    <strong>Credit risk intelligence for smarter lending decisions.</strong><br>
    This dashboard converts loan application data into risk signals that help teams detect default patterns,
    compare customer segments, and monitor credit portfolio quality.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


def build_customer_table(df):
    customer_cols = [
        "SK_ID_CURR",
        "AGE",
        "CODE_GENDER",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "NAME_EDUCATION_TYPE",
        "OCCUPATION_TYPE",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "LOAN_TO_INCOME",
        "ANNUITY_TO_INCOME",
        "TARGET",
    ]
    table = df[[col for col in customer_cols if col in df.columns]].copy()
    return table.rename(columns={
        "SK_ID_CURR": "ID",
        "AGE": "Age",
        "CODE_GENDER": "Gender",
        "AMT_INCOME_TOTAL": "Income",
        "AMT_CREDIT": "Credit",
        "AMT_ANNUITY": "Annuity",
        "NAME_EDUCATION_TYPE": "Education",
        "OCCUPATION_TYPE": "Occupation",
        "EXT_SOURCE_1": "External Score 1",
        "EXT_SOURCE_2": "External Score 2",
        "EXT_SOURCE_3": "External Score 3",
        "LOAN_TO_INCOME": "Loan-to-Income Ratio",
        "ANNUITY_TO_INCOME": "Annuity-to-Income Ratio",
        "TARGET": "Target",
    })


# SECTION 1: DATASET SUMMARY (FIRST - SHOW ACTUAL DATA)
st.subheader("📈 Dataset Summary")
try:
    df = load_home_credit_data()

    info_cols = st.columns(3)
    info_cols[0].info(f"Total Records\n{len(df):,}")
    info_cols[1].info(f"Total Features\n{len(df.columns)}")
    info_cols[2].info(f"Default Rate\n{(df['TARGET'].mean() * 100):.2f}%")

    detail_cols = st.columns(3)
    detail_cols[0].info(f"Avg. Income\n${df['AMT_INCOME_TOTAL'].mean():,.0f}")
    detail_cols[1].info(f"Avg. Credit\n${df['AMT_CREDIT'].mean():,.0f}")
    detail_cols[2].info(f"Avg. Annuity\n${df['AMT_ANNUITY'].mean():,.0f}")

    data_summary_cols = st.columns(3)
    data_summary_cols[0].info(f"Total Credit\n${df['AMT_CREDIT'].sum():,.0f}")
    data_summary_cols[1].info(f"Default Customers (TARGET = 1)\n{int((df['TARGET'] == 1).sum()):,}")
    data_summary_cols[2].info(f"Non-Default Customers (TARGET = 0)\n{int((df['TARGET'] == 0).sum()):,}")

    st.caption("Dataset summary generated from the current application data file.")

    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%); border-left: 6px solid #16a34a; border-radius: 10px; padding: 0.9rem 1rem; margin-top: 0.6rem; color: #0f172a; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);">
            <div style="font-weight: 700; color: #166534; margin-bottom: 0.3rem;">TARGET = 0</div>
            <div style="margin-bottom: 0.3rem;">→ customer had no payment difficulty</div>
            <div style="font-weight: 700; color: #b91c1c; margin-top: 0.3rem;">TARGET = 1</div>
            <div>→ customer had payment difficulties / higher default risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
except Exception as e:
    st.warning("Dataset is not available yet. Please verify the data file path.")
    st.caption(str(e))

st.markdown("---")

# SECTION 2: IMPORTANT BUSINESS INSIGHTS
st.subheader("📊 Important Business Insights")
insights = [
    ("Default risk monitoring", "Default rate is used as a key risk indicator for the overall loan portfolio."),
    ("Affordability analysis", "Income, credit amount, and annuity patterns help evaluate whether borrowers can manage repayment."),
    ("Customer segmentation", "Demographic and family profile trends help identify groups with greater repayment risk."),
    ("Portfolio action", "These insights support better risk review, monitoring, and targeted lending decisions."),
]

for title, text in insights:
    st.markdown(f"**{title}:** {text}")
    st.write("")

st.markdown("---")

# SECTION 3: BUSINESS PROBLEM
st.subheader("🎯 Business Problem")
with st.expander("📌 View business problem details"):
    st.markdown(
        """
        Home Credit needs to reduce portfolio risk without losing access to credit for healthy applicants.
        The main challenge is to identify which borrower characteristics are linked to repayment difficulty,
        and to focus attention on the segments most likely to create losses.

        The dashboard helps answer:
        - What customer profiles show the highest risk?
        - Which financial signals are most predictive of default?
        - How do income, loan size, and family profile influence repayment outcome?
        - Which segments need stronger monitoring or risk controls?
        """
    )

# SECTION 4: DASHBOARD OVERVIEW
st.subheader("🧭 Dashboard Structure")
with st.expander("📌 View dashboard overview"):
    st.markdown(
        """
        The dashboard is structured to help business and analytics teams understand loan risk from multiple angles:
        - **Executive overview and KPI review** - High-level risk metrics and summaries
        - **Demographic and applicant profile analysis** - Customer characteristics and segments
        - **Income, affordability, and credit behavior analysis** - Financial patterns and risk signals
        - **Employment, housing, and organization insights** - Professional and living situation analysis
        - **Regional and external risk score analysis** - Geographic and credit bureau data
        - **Advanced filtering and data exploration** - Custom filters and data downloads
        """
    )

st.markdown("---")

# SECTION 5: EXPANDABLE TECHNICAL DETAILS (AT THE BOTTOM)
col1, col2 = st.columns(2)

with col1:
    with st.expander("📋 Dataset Information"):
        st.write(
            """
            This project uses a loan application dataset for customer-level credit risk analysis.

            Each record represents one loan applicant and contains key information such as:
            - demographic attributes
            - family and education status
            - income and credit details
            - housing and employment data
            - repayment/default outcome label

            Main fields include:
            SK_ID_CURR, TARGET, CODE_GENDER, DAYS_BIRTH, NAME_INCOME_TYPE,
            NAME_EDUCATION_TYPE, NAME_FAMILY_STATUS, AMT_INCOME_TOTAL, AMT_CREDIT,
            AMT_ANNUITY, NAME_CONTRACT_TYPE, DAYS_EMPLOYED, OCCUPATION_TYPE,
            ORGANIZATION_TYPE, REGION_RATING_CLIENT, EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3
            """
        )

with col2:
    with st.expander("🧰 Technology Stack"):
        st.markdown(
            """
            - **Language:** Python
            - **Frontend Framework:** Streamlit
            - **Data Processing:** Pandas, NumPy
            - **Visualization:** Plotly
            - **Analytics:** Data storytelling and business intelligence workflow
            """
        )

st.subheader("📋 Detailed Customer Data")
customer_view = build_customer_table(df)
st.dataframe(customer_view, hide_index=True, use_container_width=True)

export_cols = st.columns(3)
with export_cols[0]:
    st.download_button(
        label="Download filtered customers (.csv)",
        data=df.to_csv(index=False),
        file_name="filtered_customers.csv",
        mime="text/csv",
    )
with export_cols[1]:
    default_customers = df[df["TARGET"] == 1].copy()
    st.download_button(
        label="Download default customers (.csv)",
        data=default_customers.to_csv(index=False),
        file_name="default_customers.csv",
        mime="text/csv",
    )
with export_cols[2]:
    high_risk_customers = df[df["TARGET"] == 1].copy()
    st.download_button(
        label="Download high-risk customers (.csv)",
        data=high_risk_customers.to_csv(index=False),
        file_name="high_risk_customers.csv",
        mime="text/csv",
    )

st.markdown("---")

# SECTION 6: FINAL CALL-TO-ACTION
st.success(
    "✅ This dashboard is designed to improve portfolio monitoring, strengthen risk understanding, and drive more informed credit decisions."
)

st.info(
    "👈 Use the left sidebar to navigate between the executive overview and additional analysis pages."
)