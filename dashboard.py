import streamlit as st
import pandas as pd
import sqlite3
import os
import random

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="ScamHunters Intelligence", page_icon="🛡️", layout="wide")

# --- 2. LOAD DATA FROM SQLITE (Fixed) ---
def load_data():
    db_file = 'scamhunters.db'
    if not os.path.exists(db_file):
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(db_file)
        # Select important columns from logs
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

df = load_data()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    st.divider()
    st.caption("SYSTEM STATUS")
    if not df.empty:
        st.success("🟢 DB Connected")
        st.info(f"Total Records: {len(df)}")
    else:
        st.warning("🔴 Waiting for Data")

# --- 4. MAIN DASHBOARD ---
st.title("🛡️ SCAMHUNTERS: LIVE FORENSICS")

# Metrics
c1, c2, c3 = st.columns(3)
total = len(df)
high_risk = len(df[df['risk_score'] > 80]) if not df.empty and 'risk_score' in df.columns else 0
c1.metric("Total Intercepts", total)
c2.metric("High Risk Scams", high_risk, delta="Critical")
c3.metric("AI Status", "Active", delta="Multi-Model")

st.divider()

# --- 5. LIVE LOGS TABLE ---
st.subheader("📡 Live Communication Logs")
if not df.empty:
    # Rename columns for better display if needed
    display_df = df.rename(columns={
        "session_id": "Session ID",
        "input": "Scammer Message",
        "reply": "AI Agent Reply",
        "risk_score": "Risk %",
        "timestamp": "Time"
    })
    
    st.dataframe(
        display_df,
        column_config={
            "Risk %": st.column_config.ProgressColumn("Risk Level", format="%d", min_value=0, max_value=100),
            "Scammer Message": st.column_config.TextColumn("Scammer", width="medium"),
            "AI Agent Reply": st.column_config.TextColumn("Honeypot Agent", width="medium"),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Waiting for incoming scammer messages via API...")

# --- 6. INTELLIGENCE VIEW ---
if not df.empty and 'input' in df.columns:
    st.subheader("🕵️ Extracted Intelligence")
    # Simple regex visual filter
    scammer_msgs = " ".join(df['input'].astype(str).tolist())
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown("#### 📞 Phone Numbers Identified")
        # Extract basic patterns for display
        import re
        phones = set(re.findall(r"(\+91[\-\s]?)?[6789]\d{9}", scammer_msgs))
        if phones:
            for p in phones: st.code(p)
        else:
            st.caption("No phones extracted yet.")
            
    with c_b:
        st.markdown("#### 💸 UPI / Accounts")
        upis = set(re.findall(r"[\w\.\-_]+@[\w\.\-_]+", scammer_msgs))
        if upis:
            for u in upis: st.code(u)
        else:
            st.caption("No UPIs extracted yet.")
