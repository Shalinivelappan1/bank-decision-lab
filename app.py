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
    page_title="Banking Fragility Decision Lab",
    layout="wide"
)

# -------------------------------------------------
# QUESTION BANK
# -------------------------------------------------
QUESTION_BANK = {
    "Growth-at-All-Costs": {
        "id": "Q3A",
        "text": "Growth is slowing and NPAs are rising. What is your primary decision?",
        "options": [
            "Continue aggressive growth to protect market share",
            "Pause growth and clean up the balance sheet",
            "Raise capital even if ROE and valuation fall",
            "Seek regulatory forbearance to buy time"
        ]
    },
    "Fortress Bank": {
        "id": "Q3B",
        "text": "The bank is stable but losing market share. What do you prioritize?",
        "options": [
            "Maintain conservative strategy and protect stability",
            "Selective growth in low-risk segments",
            "Push credit growth to improve ROE",
            "Seek policy or regulatory support"
        ]
    },
    "Margin Machine": {
        "id": "Q3C",
        "text": "The bank is profitable and trusted. What is the priority now?",
        "options": [
            "Defend margins and underwriting discipline",
            "Expand cautiously into new segments",
            "Take calculated risks to accelerate growth",
            "Maintain high buffers even if growth slows"
        ]
    },
    "Hidden Risk Bank": {
        "id": "Q3D",
        "text": "Returns are high but transparency is low. What do you do?",
        "options": [
            "Simplify structure even if profitability falls",
            "Continue business as usual",
            "Increase disclosure and risk visibility",
            "Ring-fence risky entities"
        ]
    },
    "Capital-Starved Growth": {
        "id": "Q3E",
        "text": "Growth exists but capital is weak. What comes first?",
        "options": [
            "Raise capital immediately",
            "Slow down lending",
            "Hide losses to buy time",
            "Depend on liquidity support"
        ]
    },
    "Regulator-Approved Bank": {
        "id": "Q3F",
        "text": "The bank is compliant but scaling slowly. What is the trade-off?",
        "options": [
            "Accept slower growth as the cost of safety",
            "Push the regulator for flexibility",
            "Innovate within regulatory constraints",
            "Increase risk appetite selectively"
        ]
    }
}

# -------------------------------------------------
# DECISION DIRECTION MAP (for shift analysis)
# -------------------------------------------------
DECISION_DIRECTION = {
    "Continue aggressive growth to protect market share": "Aggressive",
    "Push credit growth to improve ROE": "Aggressive",
    "Take calculated risks to accelerate growth": "Aggressive",
    "Pause growth and clean up the balance sheet": "Conservative",
    "Raise capital immediately": "Conservative",
    "Maintain conservative strategy and protect stability": "Conservative",
    "Slow down lending": "Conservative",
    "Delay and monitor": "Delay",
    "Depend on liquidity support": "Delay",
    "Seek regulatory forbearance to buy time": "Delay",
    "Continue business as usual": "Delay"
}

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

sheet = client.open_by_url(
    "PASTE_YOUR_GOOGLE_SHEET_URL_HERE"
).sheet1

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

    st.title("🏦 Banking Fragility Lab: Decision-Making Under Stress")

    with st.form("student_form"):

        participant_id = st.text_input(
            "Participant ID (any name/code)",
            help="Used only for before–after comparison"
        )

        role = st.selectbox(
            "Which role are you playing?",
            ["CEO", "CRO", "Regulator"]
        )

        bank = st.selectbox(
            "Which bank archetype are you deciding for?",
            list(QUESTION_BANK.keys())
        )

        q = QUESTION_BANK[bank]

        st.markdown(f"### {q['id']}")
        st.write(q["text"])

        decision = st.radio(
            "Your decision:",
            q["options"]
        )

        confidence = st.slider(
            "How confident are you?",
            1, 5, 3
        )

        reflection = st.text_area(
            "Why did you choose this option? (optional)"
        )

        round_no = st.selectbox(
            "Decision Round",
            [1, 2],
            help="Round 1 = initial role | Round 2 = after role switch"
        )

        submit = st.form_submit_button("Submit Decision")

    if submit:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            participant_id,
            role,
            bank,
            q["id"],
            decision,
            confidence,
            reflection,
            round_no
        ])
        st.success("Decision recorded successfully.")

# =================================================
# 👩‍🏫 INSTRUCTOR VIEW
# =================================================
else:

    st.title("📊 Instructor Dashboard")
    st_autorefresh(interval=5000, key="refresh")

    df = pd.DataFrame(sheet.get_all_records())

    if df.empty:
        st.warning("No responses yet.")
        st.stop()

    selected_bank = st.selectbox(
        "Select Bank Archetype",
        list(QUESTION_BANK.keys())
    )

    bank_df = df[df["Bank_Type"] == selected_bank]

    # ------------------------------
    # BEFORE vs AFTER ROLE SWITCH
    # ------------------------------
    st.subheader("Before vs After Role-Switch Analysis")

    paired = (
        bank_df
        .groupby(["Participant_ID"])
        .filter(lambda x: set(x["Round"]) == {1, 2})
    )

    before = paired[paired["Round"] == 1]
    after = paired[paired["Round"] == 2]

    comparison = before.merge(
        after,
        on=["Participant_ID", "Bank_Type"],
        suffixes=("_Before", "_After")
    )

    if not comparison.empty:

        comparison["Changed"] = (
            comparison["Decision_Before"] != comparison["Decision_After"]
        )

        change_rate = comparison["Changed"].mean() * 100

        st.metric(
            "Decision Change Rate After Role Switch",
            f"{change_rate:.1f}%"
        )

        comparison["Direction_Before"] = comparison["Decision_Before"].map(DECISION_DIRECTION)
        comparison["Direction_After"] = comparison["Decision_After"].map(DECISION_DIRECTION)

        st.subheader("Decision Shift Table")
        st.dataframe(
            comparison[[
                "Participant_ID",
                "Role_Before",
                "Decision_Before",
                "Role_After",
                "Decision_After"
            ]],
            use_container_width=True
        )

        st.subheader("Decision Direction Shift")
        st.dataframe(
            comparison
            .groupby(["Direction_Before", "Direction_After"])
            .size()
            .reset_index(name="Count"),
            use_container_width=True
        )

    else:
        st.info("Waiting for participants to complete both rounds.")
