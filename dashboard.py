import streamlit as st
import pandas as pd
import os
import random
import graphviz # Streamlit me inbuilt hota hai

# --- 1. PAGE SETUP (OLD FEATURE PRESERVED) ---
st.set_page_config(
    page_title="ScamHunters Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LOAD DATA (OLD & NEW COMPATIBLE) ---
csv_file = "scam_dataset.csv"
if os.path.exists(csv_file):
    try:
        df = pd.read_csv(csv_file)
        # Compatibility Fix: Handle both 'Threat_Score' (Old) and 'risk_score' (New)
        if 'Threat_Score' not in df.columns and 'risk_score' in df.columns:
            df['Threat_Score'] = df['risk_score']
        if 'Geo_Location' not in df.columns and 'location' in df.columns:
            df['Geo_Location'] = df['location']
    except:
        df = pd.DataFrame()
else:
    df = pd.DataFrame()

# --- 3. SIDEBAR (OLD + NEW FEATURES MIXED) ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # --- OLD FEATURE: LIGHT/DARK MODE ---
    dark_mode = st.toggle("🌙 Enable Dark Mode", value=True)
    
    # --- NEW FEATURE: SESSION SELECTOR ---
    if not df.empty:
        st.divider()
        st.subheader("🕵️ Inspect Suspect")
        # Reverse list to show latest first
        session_list = df['session_id'].unique()[::-1]
        selected_session = st.selectbox("Active ID:", session_list)
        # Get data for selected user
        user_data = df[df['session_id'] == selected_session].iloc[0]
    else:
        user_data = None
        
    st.divider()
    
    # --- OLD FEATURES: SETTINGS ---
    st.selectbox("Operation Mode", ["Active Interception", "Passive Analysis"])
    st.slider("Risk Sensitivity", 0, 100, 95)
    
    st.caption("SYSTEM HEALTH")
    st.success("API: ONLINE")
    st.info("DB: CONNECTED")
    
    if st.button("🗑️ RESET DATABASE"):
        if os.path.exists("scam_dataset.csv"):
            os.remove("scam_dataset.csv")
            st.rerun()

# --- 4. DYNAMIC CSS (LIGHT/DARK LOGIC RESTORED) ---
if dark_mode:
    # DARK THEME
    bg_color = "#0E1117"
    text_color = "#FAFAFA"
    card_bg = "#1f1f1f"
    metric_bg = "#262730"
    heading_color = "#FF4B4B"
else:
    # LIGHT THEME
    bg_color = "#FFFFFF"
    text_color = "#000000"
    card_bg = "#F0F2F6"
    metric_bg = "#FFFFFF"
    heading_color = "#D32F2F"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stDataFrame {{ border: 1px solid #444; }}
    h1, h2, h3 {{ color: {heading_color} !important; }}
    div[data-testid="stMetric"] {{
        background-color: {metric_bg};
        border-radius: 8px;
        padding: 10px;
        border-left: 4px solid {heading_color};
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    /* NEW FEATURE STYLING: PROFILE CARD */
    .profile-info {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 10px;
        border: 1px solid {heading_color};
        margin-bottom: 20px;
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER: GLOBAL COORDINATES (NEW FEATURE) ---
def get_coordinates(location_name):
    loc_map = {
        "Delhi": [28.70, 77.10], "Mumbai": [19.07, 72.87], "Jamtara": [23.96, 86.80],
        "New York": [40.71, -74.00], "USA": [37.09, -95.71],
        "London": [51.50, -0.12], "UK": [55.37, -3.43],
        "Lagos": [6.52, 3.37], "Nigeria": [9.08, 8.67],
        "Dubai": [25.20, 55.27], "Russia": [61.52, 105.31],
        "Unknown": [20.59, 78.96]
    }
    for city, coords in loc_map.items():
        if city.lower() in str(location_name).lower():
            return [coords[0] + random.uniform(-0.5, 0.5), coords[1] + random.uniform(-0.5, 0.5)]
    return [20.59 + random.uniform(-1, 1), 78.96 + random.uniform(-1, 1)]

# --- 5. MAIN UI LAYOUT ---
st.title("🛡️ SCAMHUNTERS: FORENSIC DASHBOARD")
st.markdown("### 📡 Real-time Data Extraction & Network Analysis")

# TABS (OLD LAYOUT PRESERVED)
tab1, tab2, tab3 = st.tabs(["📊 Live Monitor", "🕵️ Deep Forensics (Evidence)", "🕸️ Network Graph"])

# --- TAB 1: LIVE MONITOR (UPDATED WITH GLOBAL MAP) ---
with tab1:
    c1, c2, c3 = st.columns(3)
    count = len(df) if not df.empty else 0
    c1.metric("Total Intercepts", count)
    
    # Critical Threats
    critical = len(df[df['Threat_Score'] > 85]) if not df.empty and 'Threat_Score' in df.columns else 0
    c2.metric("Critical Threats", critical, delta="High Risk")
    
    # NEW METRIC: IP Count
    ip_count = df['ip_address'].nunique() if not df.empty and 'ip_address' in df.columns else 0
    c3.metric("IPs Tracked", ip_count)

    st.subheader("📍 Live Global Geo-Tracing")
    if not df.empty:
        map_data = []
        for index, row in df.iterrows():
            lat, lon = get_coordinates(row.get('Geo_Location', 'Unknown'))
            map_data.append({'lat': lat, 'lon': lon})
        st.map(pd.DataFrame(map_data))
    else:
        st.info("No location data available yet.")

# --- TAB 2: EVIDENCE LOG (UPDATED WITH PROFILE CARD) ---
with tab2:
    st.subheader("📂 Extracted Intelligence")
    
    if user_data is not None:
        # --- NEW FEATURE: CRIMINAL PROFILE CARD ---
        st.markdown(f"""
        <div class="profile-info">
            <h3>🚫 SUSPECT DOSSIER: {user_data.get('phone', 'Unknown')}</h3>
            <p><b>📍 Location:</b> {user_data.get('Geo_Location', 'Unknown')} | <b>🌐 IP:</b> {user_data.get('ip_address', 'Hidden')}</p>
            <p><b>📱 Carrier:</b> {user_data.get('carrier', 'Unknown')} | <b>🤖 Device:</b> {user_data.get('device', 'Unknown')}</p>
            <p><b>🗣️ Tone:</b> {user_data.get('tone', 'Neutral')} | <b>⚠️ Risk:</b> {user_data.get('Threat_Score', 0)}%</p>
            <hr style="border-color: #555;">
            <p><b>💬 Scammer Said:</b> <i>"{user_data.get('scammer_msg', 'N/A')}"</i></p>
            <p><b>🤖 Agent Replied:</b> <i>"{user_data.get('bot_reply', 'N/A')}"</i></p>
        </div>
        """, unsafe_allow_html=True)

        # Check for Traps
        reply = str(user_data.get('bot_reply', ''))
        c_a, c_b = st.columns(2)
        if "Proof:" in reply:
            c_a.warning("📸 Fake Screenshot Deployed")
        if "Voice:" in reply:
            c_b.warning("🎤 Voice Trap Deployed")

    st.divider()

    # --- MAIN TABLE (WITH ALL NEW COLUMNS) ---
    if not df.empty:
        # Show all new columns like IP, Carrier, Tone
        display_cols = ["timestamp", "session_id", "Threat_Score", "phone", "upi", "ip_address", "carrier", "tone", "device"]
        available_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(
            df[available_cols],
            use_container_width=True,
            column_config={
                "Threat_Score": st.column_config.ProgressColumn("Risk", format="%d%%", min_value=0, max_value=100),
                "phone": st.column_config.TextColumn("📞 Phone"),
                "upi": st.column_config.TextColumn("💸 UPI"),
                "url": st.column_config.LinkColumn("Phishing Link"),
            }
        )
    else:
        st.warning("No Evidence Found. Waiting for attacks...")

# --- TAB 3: NETWORK GRAPH (OLD FEATURE KEPT) ---
with tab3:
    st.subheader("🕸️ Scammer-Victim Connection Graph")
    
    if not df.empty:
        try:
            graph = graphviz.Digraph()
            # Dynamic Colors based on Dark Mode
            node_color = '#FF4B4B' if dark_mode else '#D32F2F'
            font_color = 'white' if dark_mode else 'black'
            graph_bg = '#0E1117' if dark_mode else '#FFFFFF'
            
            graph.attr(rankdir='LR', bgcolor=graph_bg)
            graph.attr('node', shape='box', style='filled', color=node_color, fontcolor='white')
            
            # Central Node
            graph.node('AI_SYSTEM', 'ScamHunters AI', shape='ellipse', color='#00CC96')
            
            # Add Scammer Nodes
            for index, row in df.tail(8).iterrows():
                label = row.get('phone', 'Unknown')
                if label in ["Not Found", "None", "Unknown"]:
                    label = row.get('ip_address', row['session_id'][:8])
                
                graph.edge(f"Scammer_{index}", 'AI_SYSTEM', label=f"Attack: {label}")
            
            st.graphviz_chart(graph)
        except Exception as e:
            st.error(f"Graph Error: {e}")
            st.info("Install graphviz to see visualization.")
    else:
        st.info("Waiting for data to build graph...")