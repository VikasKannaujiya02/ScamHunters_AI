import os
import logging
import uvicorn
import sqlite3
import datetime
import requests
import re
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- IMPORT AGENT MODULES ---
from agent.persona import get_agent_response, detect_scam_with_ai
from forensics.bait_gen import generate_fake_payment_screenshot

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScamHunters_Core_Pro")

app = FastAPI(title="ScamHunters Agentic Honeypot")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. DATABASE INITIALIZATION ---
def init_db():
    try:
        conn = sqlite3.connect('scamhunters.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS logs 
                     (id INTEGER PRIMARY KEY, session_id TEXT, 
                      input TEXT, reply TEXT, risk_score INTEGER, timestamp TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Init Error: {e}")

init_db()

# --- 2. INTELLIGENCE EXTRACTION (UPDATED: HISTORY SCAN) 🕵️‍♂️ ---
def extract_intelligence(current_text, history):
    """
    Extracts entities from BOTH current text AND full conversation history.
    Fixes the issue where data sent in previous messages was ignored.
    """
    # 1. Combine all Scammer messages into one big text block
    full_text = current_text + " "
    if history:
        for msg in history:
            if isinstance(msg, dict) and msg.get('sender') == 'scammer':
                full_text += msg.get('text', '') + " "
    
    # 2. Normalize: "9 8 7 6" -> "9876" (Catch spaced numbers)
    normalized_text = re.sub(r'\s+', '', full_text)
    
    extracted = {
        # Catch standard (+91...) and spaced formats via Normalized text
        "phoneNumbers": re.findall(r"(\+91|91)?[6-9]\d{9}", normalized_text),
        
        # Standard Extraction (Relaxed Regex for UPI)
        "upiIds": re.findall(r"[a-zA-Z0-9\.\-_]+@[a-zA-Z0-9]+", full_text),
        
        "phishingLinks": re.findall(r"(https?://[^\s]+)|(www\.[^\s]+)", full_text),
        "bankAccounts": re.findall(r"\b\d{9,18}\b", normalized_text)
    }
    
    # Filter Valid Phone Numbers (Length check)
    extracted["phoneNumbers"] = list(set([p for p in extracted["phoneNumbers"] if len(p) >= 10]))
    extracted["upiIds"] = list(set(extracted["upiIds"])) # Remove duplicates
    
    # Social Engineering Keywords (Scan only current text for intent)
    keywords = ["urgent", "police", "block", "verify", "kyc", "otp", "expiry", "jail", "cbi"]
    extracted["suspiciousKeywords"] = [w for w in keywords if w in current_text.lower()]
    
    return extracted

# --- 3. HANDOVER LOGIC & AI DETECTION ---
async def handover_to_agent_and_report(session_id, user_text, history):
    """
    Hands over control to AI Agent AND Performs AI-based Scam Detection.
    """
    # 1. GENERATE RESPONSE
    ai_reply = await get_agent_response(user_text, history)
    
    # 2. DETECT SCAM USING AI (NLP MODEL)
    risk_score = await detect_scam_with_ai(user_text)
    
    # 3. REPORT TO GUVI (Rule 12 Callback)
    try:
        # --- FIX: PASS HISTORY TO EXTRACTION ---
        extracted = extract_intelligence(user_text, history)
        
        # Guvi Payload
        url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        payload = {
            "sessionId": session_id,
            "scamDetected": True if risk_score > 60 else False,
            "totalMessagesExchanged": len(history) + 1,
            "extractedIntelligence": extracted,
            "agentNotes": f"AI Risk Analysis Score: {risk_score}/100. NLP Detection Active."
        }
        
        # Send Request (Timeout 5s)
        try: 
            requests.post(url, json=payload, timeout=5)
            logger.info(f"📡 Callback Sent. Risk: {risk_score} | Data Found: {len(extracted['upiIds'])} UPIs")
        except: 
            pass
        
        # Save to Local DB
        conn = sqlite3.connect('scamhunters.db')
        c = conn.cursor()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO logs (session_id, input, reply, risk_score, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (session_id, user_text, ai_reply, risk_score, ts))
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Handover/Reporting Error: {e}")

    return ai_reply, risk_score

# --- 4. MAIN API ENDPOINT ---
@app.api_route("/api/chat", methods=["GET", "POST"])
async def chat_endpoint(request: Request, background_tasks: BackgroundTasks):
    if request.headers.get("x-api-key") != "12345": 
        pass 

    try:
        try: data = await request.json()
        except: data = dict(await request.form())
        
        logger.info(f"📩 Incoming Data: {data}")
        
        session_id = data.get("sessionId", f"sess_{datetime.datetime.now().timestamp()}")
        
        user_text = "Hello"
        if "message" in data and isinstance(data["message"], dict):
            user_text = data["message"].get("text", "")
        elif "text" in data: user_text = data["text"]
        elif "input" in data: user_text = data["input"]

        history = data.get("conversationHistory", [])

        # --- CALL HANDOVER LOGIC ---
        ai_reply, risk_score = await handover_to_agent_and_report(session_id, user_text, history)

        # Trigger Bait (Only if high risk detected by AI)
        if risk_score > 75:
            background_tasks.add_task(generate_fake_payment_screenshot, "5000")

        return {
            "status": "success",
            "reply": ai_reply,
            "risk_score": risk_score,
            "sessionId": session_id
        }

    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

# --- 5. DASHBOARD ENDPOINT ---
@app.get("/api/logs")
def get_logs():
    try:
        conn = sqlite3.connect('scamhunters.db')
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return {"logs": df.to_dict(orient="records")}
    except: return {"logs": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
