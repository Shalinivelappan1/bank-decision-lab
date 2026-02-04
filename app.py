import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Banking Fragility Decision Lab",
    layout="wide"
)

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
# SENTIMENT MAP (TEACHING JUDGMENT LAYER)
# =================================================
SENTIMENT_MAP = {
    "Growth-at-All-Costs": {
        "Continue aggressive growth to protect market share": {
            "CEO": "😃", "CRO": "😟", "Regulator": "😠"
        },
        "Pause growth and clean up the balance sheet": {
            "CEO": "😐", "CRO": "🙂", "Regulator": "🙂"
        },
        "Raise capital even if ROE and valuation fall": {
            "CEO": "😟", "CRO": "🙂", "Regulator": "😃"
        },
        "Seek regulatory forbearance to buy time": {
            "CEO": "😐", "CRO": "😟", "Regulator": "😠"
        }
    },
    "Fortress Bank": {
        "Maintain conservative strategy and protect stability": {
            "CEO": "🙂", "CRO": "😃", "Regulator": "😃"
        },
        "Push credit growth to improve ROE": {
            "CEO": "😃", "CRO": "😟", "Regulator": "😠"
        }
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
# MODE SELECT
# =================================================
mode = st.sidebar.radio(
    "Select Mode",
    ["Student View", "Instructor View"]
)

# =================================================
# 👩‍🎓 STUDENT VIEW
# =================================================
if mode == "Student View":

    st.title("🏦 Banking Fragility Lab: Decision-Making Under Stress")

    st.write(
        "There are no correct answers. "
        "Your task is to decide based on the role you are playing. "
        "Different roles see the same situation differently — that tension is the lesson."
    )

    with st.form("student_form"):

        participant_id = st.text_input(
            "Participant ID (any name / roll no.)",
            help="Used only to compare Round 1 vs Round 2 decisions"
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
            "How confident are you in this decision?",
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
        st.success("✅ Decision recorded.")

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

    # ------------------------------
    # ROUND-WISE SENTIMENT
    # ------------------------------
    st.subheader("Round-wise Sentiment Comparison")

    def get_sentiment(round_no):
        round_df = df[
            (df["Bank_Type"] == selected_bank) &
            (df["Round"] == round_no)
        ]
        if round_df.empty:
            return None

        dominant_decision = (
            round_df
            .groupby("Decision")
            .size()
            .idxmax()
        )

        mapping = SENTIMENT_MAP.get(selected_bank, {}).get(dominant_decision, {})
        return {
            "Scenario": selected_bank,
            "CEO": mapping.get("CEO", "—"),
            "CRO": mapping.get("CRO", "—"),
            "Regulator": mapping.get("Regulator", "—")
        }

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟦 Round 1 Sentiment")
        r1 = get_sentiment(1)
        if r1:
            st.dataframe(pd.DataFrame([r1]), use_container_width=True)
        else:
            st.info("No Round 1 data yet.")

    with col2:
        st.markdown("### 🟧 Round 2 Sentiment")
        r2 = get_sentiment(2)
        if r2:
            st.dataframe(pd.DataFrame([r2]), use_container_width=True)
        else:
            st.info("No Round 2 data yet.")

    st.caption(
        "Legend: 😃 Comfortable | 🙂 Acceptable | 😐 Neutral | 😟 Worried | 😠 Alarmed"
    )

    # ------------------------------
    # REAL-WORLD LEARNING INSIGHTS
    # ------------------------------
    st.subheader("🧠 Real-World Insights from This Lab")

    with st.expander("1️⃣ Incentives, not intelligence, drive bank decisions"):
        st.write(
            "Bank failures rarely occur because managers lack information. "
            "They occur because different roles face different incentives. "
            "CEOs are rewarded for growth, CROs for loss avoidance, and regulators "
            "for system stability. The same facts therefore lead to different choices."
        )

    with st.expander("2️⃣ Delay is the most common — and dangerous — decision"):
        st.write(
            "Across global banking crises, delay is the most frequent response to stress. "
            "Delay feels rational individually but is systemically costly. "
            "Most bank collapses were not sudden — they were built through repeated delays."
        )

    with st.expander("3️⃣ Capital problems usually appear as liquidity crises"):
        st.write(
            "Banks typically fail when confidence collapses and liquidity evaporates, "
            "not when capital ratios first weaken. "
            "What looks like a liquidity shock is often a capital problem postponed."
        )

    with st.expander("4️⃣ Stability has a visible cost — and an invisible benefit"):
        st.write(
            "When decisions shift toward caution, growth slows. "
            "This is not a failure — it is the price of resilience. "
            "Strong banking systems prioritize survival over peak profitability."
        )

    with st.expander("5️⃣ The regulator’s problem is always timing"):
        st.write(
            "Regulators face a dilemma: act early and face criticism, "
            "or act late and face crisis. "
            "The cost of delay is usually borne by depositors and taxpayers, "
            "not the original decision-makers."
        )
        st.subheader("🧾 Wrap-Up: What Did We Learn?")

st.markdown("""
**1. The same facts produce different decisions**  
Changing roles changed outcomes — even when information stayed constant.  
This reveals how incentives shape judgment.

**2. Comfort is redistributed, not eliminated**  
Round 1 concentrated comfort with growth decision-makers.  
Round 2 shifted comfort toward risk managers and regulators.

**3. Delay is the most common failure mode**  
Most banking collapses arise from repeated, rational delays — not reckless bets.

**4. Growth and stability are a trade-off**  
Slower growth is often the price of resilience, not a failure of strategy.

**5. Banking crises are incentive failures, not moral failures**  
Systemic risk emerges from misaligned roles, not bad intentions.

**Key takeaway:**  
*Banks choose their failure mode through strategy.  
The best banks optimize resilience — not headline growth.*
""")

