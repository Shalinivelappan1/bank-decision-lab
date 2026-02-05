import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="Banking Fragility Decision Lab", layout="wide")

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
# FULL SENTIMENT MAP (😊)
# =================================================
SENTIMENT_MAP = {
"Growth-at-All-Costs": {
"Continue aggressive growth to protect market share":{"CEO":"😃","CRO":"😟","Regulator":"😠"},
"Pause growth and clean up the balance sheet":{"CEO":"😐","CRO":"🙂","Regulator":"🙂"},
"Raise capital even if ROE and valuation fall":{"CEO":"😟","CRO":"🙂","Regulator":"😃"},
"Seek regulatory forbearance to buy time":{"CEO":"😐","CRO":"😟","Regulator":"😠"}
},
"Fortress Bank": {
"Maintain conservative strategy and protect stability":{"CEO":"🙂","CRO":"😃","Regulator":"😃"},
"Selective growth in low-risk segments":{"CEO":"😃","CRO":"🙂","Regulator":"🙂"},
"Push credit growth to improve ROE":{"CEO":"😃","CRO":"😟","Regulator":"😠"},
"Seek policy or regulatory support":{"CEO":"😐","CRO":"🙂","Regulator":"🙂"}
},
"Margin Machine": {
"Defend margins and underwriting discipline":{"CEO":"😃","CRO":"😃","Regulator":"🙂"},
"Expand cautiously into new segments":{"CEO":"🙂","CRO":"🙂","Regulator":"🙂"},
"Take calculated risks to accelerate growth":{"CEO":"😃","CRO":"😟","Regulator":"😠"},
"Maintain high buffers even if growth slows":{"CEO":"😐","CRO":"😃","Regulator":"😃"}
},
"Hidden Risk Bank": {
"Simplify structure even if profitability falls":{"CEO":"😟","CRO":"😃","Regulator":"😃"},
"Continue business as usual":{"CEO":"😃","CRO":"😠","Regulator":"😠"},
"Increase disclosure and risk visibility":{"CEO":"😐","CRO":"😃","Regulator":"😃"},
"Ring-fence risky entities":{"CEO":"😐","CRO":"😃","Regulator":"😃"}
},
"Capital-Starved Growth": {
"Raise capital immediately":{"CEO":"😟","CRO":"😃","Regulator":"😃"},
"Slow down lending":{"CEO":"😐","CRO":"🙂","Regulator":"🙂"},
"Hide losses to buy time":{"CEO":"😃","CRO":"😠","Regulator":"😠"},
"Depend on liquidity support":{"CEO":"😐","CRO":"😟","Regulator":"😟"}
},
"Regulator-Approved Bank": {
"Accept slower growth as the cost of safety":{"CEO":"😐","CRO":"🙂","Regulator":"😃"},
"Push the regulator for flexibility":{"CEO":"😃","CRO":"😟","Regulator":"😟"},
"Innovate within regulatory constraints":{"CEO":"🙂","CRO":"🙂","Regulator":"🙂"},
"Increase risk appetite selectively":{"CEO":"😃","CRO":"😟","Regulator":"😠"}
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
    "https://docs.google.com/spreadsheets/d/1iZJJMBwx6HRon73sKzbxoX99ocT6Fg0mS9RItGrve1U/edit"
).sheet1

# =================================================
# MODE
# =================================================
mode = st.sidebar.radio("Mode", ["Student View", "Instructor View"])

# =================================================
# STUDENT VIEW
# =================================================
if mode == "Student View":

    st.title("🏦 Banking Fragility Decision Lab-Designed by Prof.Shalini Velappan")
    participant = st.text_input("Participant ID")
    role = st.selectbox("Role", ["CEO","CRO","Regulator","HR"])
    bank = st.selectbox("Bank Archetype", list(QUESTION_BANK.keys()))
    q = QUESTION_BANK[bank]

    st.subheader(q["text"])

    with st.form("decision_form"):
        decision = st.radio("Decision", q["options"])
        confidence = st.slider("Confidence", 1, 5, 3)
        reflection = st.text_area("Why this decision?")
        round_no = st.selectbox("Round", [1,2])
        submit = st.form_submit_button("Submit")

    if submit:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            participant, role, bank, q["id"],
            decision, confidence, reflection, round_no
        ])
        st.success("Decision recorded")

# =================================================
# PROFESSOR / INSTRUCTOR VIEW
# =================================================
else:

    st.title("📊 Professor Dashboard — Banking Fragility Lab-Designed by Prof.Shalini Velappan")
    st_autorefresh(interval=4000)

    df = pd.DataFrame(sheet.get_all_records())
    if df.empty:
        st.warning("No responses yet.")
        st.stop()

    selected_bank = st.selectbox("Select Bank Archetype", df["Bank"].unique())
    bank_df = df[df["Bank"] == selected_bank]

    # 📊 Decision Distribution
    st.subheader("📊 Decision Distribution")
    st.bar_chart(bank_df["Decision"].value_counts())

    # 🔁 Round Comparison
    st.subheader("🔁 Round 1 vs Round 2")
    r1 = bank_df[bank_df["Round"] == 1]
    r2 = bank_df[bank_df["Round"] == 2]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Round 1")
        if not r1.empty:
            d1 = r1["Decision"].value_counts().idxmax()
            st.write("Dominant:", d1)
            st.write(SENTIMENT_MAP[selected_bank].get(d1, {}))
    with col2:
        st.markdown("### Round 2")
        if not r2.empty:
            d2 = r2["Decision"].value_counts().idxmax()
            st.write("Dominant:", d2)
            st.write(SENTIMENT_MAP[selected_bank].get(d2, {}))

    # 🎭 Role Tension Heatmap
    st.subheader("🎭 Role Tension Heatmap (Avg Confidence)")
    heat = pd.pivot_table(
        bank_df,
        values="Confidence",
        index="Role",
        columns="Decision",
        aggfunc="mean"
    )
    st.dataframe(heat, use_container_width=True)

    # 🔮 Fragility Signal
    st.subheader("🔮 Fragility Signal")
    dominant = bank_df["Decision"].value_counts().idxmax()
    if "growth" in dominant.lower() or "hide" in dominant.lower():
        st.error("⚠️ High Fragility: Delay + growth bias detected")
    elif "capital" in dominant.lower() or "pause" in dominant.lower():
        st.success("✅ Low Fragility: Early repair mindset")
    else:
        st.warning("🟡 Moderate Fragility: Mixed incentives")

    # 🧠 Auto Teaching Insight
    st.subheader("🧠 Teaching Insight (Auto)")
    st.info(
        "This pattern mirrors real crises: "
        "CEO comfort peaks early, CRO discomfort rises late, "
        "regulators react only after confidence breaks."
    )

    # 🎤 Auto Debrief Script
    st.subheader("🎤 Debrief Script")
    st.markdown(f"""
    **What happened here?**  
    The class converged on **{dominant}**.

    **Why this matters:**  
    This decision feels rational in isolation but dangerous system-wide.

    **Key lesson:**  
    Banks rarely fail due to one bad choice —  
    they fail because *reasonable decisions compound under pressure*.

    **Ask the class:**  
    *Who felt comfortable? Who felt uneasy? Who bears the cost if this fails?*
    """)

    # 🧾 Reflections
    st.subheader("🧾 Student Reflections")
    st.dataframe(bank_df[["Role","Decision","Reflection"]], use_container_width=True)
