import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="Banking Fragility Lab", layout="wide")

# =================================================
# QUESTION BANK
# =================================================
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

# =================================================
# SENTIMENT MAP (SMILIES)
# =================================================
SENTIMENT_MAP = {
    "Growth-at-All-Costs": {
        "Continue aggressive growth to protect market share":
            {"CEO": "😃", "CRO": "😟", "Regulator": "😠"},
        "Pause growth and clean up the balance sheet":
            {"CEO": "😐", "CRO": "🙂", "Regulator": "🙂"},
        "Raise capital even if ROE and valuation fall":
            {"CEO": "😟", "CRO": "🙂", "Regulator": "😃"},
        "Seek regulatory forbearance to buy time":
            {"CEO": "😐", "CRO": "😟", "Regulator": "😠"}
    }
}

# =================================================
# GOOGLE SHEETS CONNECTION
# =================================================
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
    "https://docs.google.com/spreadsheets/d/1iZJJMBwx6HRon73sKzbxoX99ocT6Fg0mS9RItGrve1U/edit#gid=0"
).sheet1

# =================================================
# MODE
# =================================================
mode = st.sidebar.radio("Mode", ["Student View", "Instructor View"])

# =================================================
# STUDENT VIEW
# =================================================
if mode == "Student View":

    st.title("🏦 Banking Live Decision Lab- Designed by Dr.Shalini Velappan")

    participant = st.text_input("Participant ID")
    role = st.selectbox("Role", ["CEO", "CRO", "Regulator", "HR"])

    bank = st.selectbox("Bank Archetype", list(QUESTION_BANK.keys()))
    q = QUESTION_BANK[bank]

    st.divider()
    st.subheader(q["text"])

    with st.form("form"):
        decision = st.radio("Decision", q["options"])
        confidence = st.slider("Confidence", 1, 5, 3)
        reflection = st.text_area("Why?")
        round_no = st.selectbox("Round", [1, 2])

        submit = st.form_submit_button("Submit")

    if submit:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            participant,
            role,
            bank,
            q["id"],
            decision,
            confidence,
            reflection,
            round_no
        ])
        st.success("Recorded")

# =================================================
# INSTRUCTOR VIEW
# =================================================
else:

    st.title("📊 Instructor Dashboard")
    st_autorefresh(interval=2000)

    data = sheet.get_all_records()
    if len(data) == 0:
        st.warning("No responses yet")
        st.stop()

    df = pd.DataFrame(data)

    df.columns = [
        "Timestamp","Participant","Role","Bank",
        "Question","Decision","Confidence","Reflection","Round"
    ]

    st.metric("Total Decisions", len(df))

    selected_bank = st.selectbox("Select Bank", df["Bank"].unique())
    bank_df = df[df["Bank"] == selected_bank]

    # ---------------------------
    # LIVE CHART
    # ---------------------------
    st.subheader("Live Decision Distribution")
    vote_counts = bank_df.groupby("Decision").size().reset_index(name="Count")
    st.bar_chart(vote_counts.set_index("Decision"))

    # ---------------------------
    # ROLE HEATMAP
    # ---------------------------
    st.subheader("Role vs Decision")
    pivot = pd.pivot_table(bank_df, index="Role", columns="Decision", aggfunc="size", fill_value=0)
    st.dataframe(pivot, use_container_width=True)

    # ---------------------------
    # ROUND SHIFT
    # ---------------------------
    st.subheader("Round 1 vs Round 2")
    r1 = bank_df[bank_df["Round"] == 1]
    r2 = bank_df[bank_df["Round"] == 2]

    if not r1.empty and not r2.empty:
        r1_counts = r1.groupby("Decision").size().reset_index(name="Round1")
        r2_counts = r2.groupby("Decision").size().reset_index(name="Round2")
        merged = pd.merge(r1_counts, r2_counts, on="Decision", how="outer").fillna(0)
        st.dataframe(merged)
        st.bar_chart(merged.set_index("Decision"))

    # ---------------------------
    # CONFIDENCE
    # ---------------------------
    st.subheader("Confidence Levels")
    st.bar_chart(bank_df.groupby("Confidence").size())

    # ---------------------------
    # SMILEY SENTIMENT PANEL
    # ---------------------------
    st.subheader("🙂 Role Comfort Sentiment")

    def sentiment(round_no):
        rd = bank_df[bank_df["Round"] == round_no]
        if rd.empty:
            return None
        dom = rd.groupby("Decision").size().idxmax()
        return SENTIMENT_MAP.get(selected_bank, {}).get(dom, {})

    col1, col2 = st.columns(2)

    with col1:
        st.write("Round 1")
        st.write(sentiment(1))

    with col2:
        st.write("Round 2")
        st.write(sentiment(2))

    # ---------------------------
    # REFLECTIONS
    # ---------------------------
    st.subheader("Student Reflections")
    st.dataframe(bank_df[["Role","Decision","Reflection"]])
