import pandas as pd
import os

# Database File Name
DB_FILE = "scam_dataset.csv"

def log_to_excel(dossier, user_msg, bot_reply, agent):
    """
    Saves detailed forensic data to CSV.
    Strictly follows the schema required by Dashboard and Guidelines.
    """
    
    # 1. Prepare the Record (Dictionary)
    # Hum sure karte hain ki har column wahi ho jo Dashboard dhund raha hai
    record = {
        "timestamp": dossier.get('timestamp', 'N/A'),
        "session_id": dossier.get('session_id', 'Unknown'),
        "risk_score": dossier.get('risk_score', 0),
        "scammer_msg": user_msg,
        "bot_reply": bot_reply,
        "agent": agent,
        
        # --- Deep Forensic Columns (New) ---
        "ip_address": dossier.get('ip_address', 'Hidden'),
        "carrier": dossier.get('carrier', 'Unknown ISP'),
        "device": dossier.get('device', 'Unknown Device'),
        "location": dossier.get('location', 'Unknown Node'),
        "tone": dossier.get('tone', 'Neutral'),
        
        # --- Entities (Extracted Info) ---
        "phone": dossier.get('phone', 'None'),
        "upi": dossier.get('upi', 'None'),
        "email": dossier.get('email', 'None'),
        "url": dossier.get('url', 'None'),
        "amount_asked": dossier.get('amount_asked', '0')
    }

    # 2. Convert to DataFrame
    df = pd.DataFrame([record])

    # 3. Save Logic (Append Mode)
    # Agar file nahi hai toh Header ke sath banao, nahi toh bas data jodo
    if not os.path.exists(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        # Ensure correct column order by reading existing columns if needed
        # But appending strictly is faster and safer for now
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

    # 4. Success Log (Terminal me dikhega)
    print(f"✅ LOGGED: Session {dossier.get('session_id')} | Risk: {dossier.get('risk_score')}%")