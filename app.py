import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Bank Crisis Decision Lab",
    layout="wide"
)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
BANK_TYPES = [
    "Growth-at-All-Costs",
    "Fortress Bank",
    "Margin Machine",
    "Hidden Risk Bank",
    "Capital-Starved Growth",
    "Regulator-Approved Bank"
]

DECISIONS = [
    "Act early / tighten controls",
    "Continue current strategy",
    "Delay and monitor"
]

# -------------------------------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ⚠️ Sheet name must match EXACTLY
sheet = client.open("Bank_Decision_Lab").sheet1

# -------------------------------------------------
# MODE SELECT
# -------------------------------------------------
mode = st.sidebar.radio(
    "Select Mode",
    ["Student View", "Instructor View"]
)

# =================================================
# 👩‍🎓 STUDENT VIEW
# =================================================
if mode == "Student View":

    st.title("🏦 Bank Crisis Decision Lab")
    st.write(
        "Assume your role as **CEO, CRO, or Regulator**. "
        "Make a decision for each bank type."
    )

    with st.form("student_form"):

        role = st.selectbox(
            "Select your role",
            ["CEO", "CRO", "Regulator"]
        )

        bank = st.selectbox(
            "Select bank archetype",
            BANK_TYPES
        )

        decision = st.radio(
            "What do you do?",
            DECISIONS
        )

        confidence = st.slider(
            "How confident are you?",
            1, 5, 3
        )

        submit = st.form_submit_button("Submit Decision")

    if submit:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            role,
            bank,
            decision,
            confidence
        ])

        st.success("✅ Decision recorded successfully.")

# =================================================
# 👩‍🏫 INSTRUCTOR VIEW
# =================================================
else:

    st.title("📊 Live Decision Dashboard")

    # Auto-refresh every 5 seconds
    st_autorefresh(interval=5000, key="refresh")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No responses yet.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        selected_bank = st.selectbox(
            "Select bank archetype",
            BANK_TYPES
        )

    with col2:
        selected_role = st.selectbox(
            "Filter by role",
            ["All", "CEO", "CRO", "Regulator"]
        )

    filtered = df[df["Bank_Type"] == selected_bank]

    if selected_role != "All":
        filtered = filtered[filtered["Role"] == selected_role]

    st.subheader(f"Decisions: {selected_bank}")

    decision_counts = (
        filtered
        .groupby(["Decision", "Role"])
        .size()
        .unstack(fill_value=0)
    )

    st.bar_chart(decision_counts)

    st.subheader("Average Confidence Level")

    confidence_table = (
        filtered
        .groupby("Role")["Confidence"]
        .mean()
        .round(2)
        .reset_index()
    )

    st.dataframe(confidence_table, use_container_width=True)

    with st.expander("Show raw responses"):
        st.dataframe(filtered, use_container_width=True)

    if st.button("🎬 Reveal Real-World Outcome"):
        st.error(
            "Real-world pattern: delayed action + confidence shocks "
            "→ liquidity stress → regulatory intervention."
        )
