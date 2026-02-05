import os
import logging
import random
from google import genai
from groq import Groq
from openai import OpenAI

# Logger
logger = logging.getLogger("ScamHunters_Priority")

# ==========================================
# 1. SETUP ALL 3 CLIENTS
# ==========================================

# A. Groq (Fastest)
groq_key = os.getenv("GROQ_API_KEY")
groq_client = None
if groq_key:
    try:
        groq_client = Groq(api_key=groq_key)
        logger.info("✅ Groq Connected.")
    except: logger.error("❌ Groq Failed.")

# B. Google (New Library)
google_key = os.getenv("GEMINI_API_KEY")
google_client = None
if google_key:
    try:
        google_client = genai.Client(api_key=google_key)
        logger.info("✅ Gemini Connected.")
    except: logger.error("❌ Gemini Failed.")

# C. OpenAI (Last Backup)
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if openai_key:
    try:
        openai_client = OpenAI(api_key=openai_key)
        logger.info("✅ OpenAI Connected.")
    except: logger.error("❌ OpenAI Failed.")

# ==========================================
# 2. MULTI-AGENT PERSONAS (3 Log)
# ==========================================
PERSONAS = {
    "Savitri": "You are Savitri Devi, 65. Confused old lady. Speak Hinglish. Waste time. NEVER give real OTP.",
    "Rajesh": "You are Rajesh, Savitri's son. Angry. Abuse the scammer. 'Tu kaun hai?', 'Police bulaunga'.",
    "Police": "You are Inspector Vijay. Cyber Cell. 'Call Traced', 'Location Locked', 'Surrender now'."
}

def get_active_agent(history):
    count = len(history) if history else 0
    if count < 4: return "Savitri", PERSONAS["Savitri"]
    elif count < 8: return "Rajesh", PERSONAS["Rajesh"]
    else: return "Police", PERSONAS["Police"]

# ==========================================
# 3. LOCAL FALLBACK (Safety Net)
# ==========================================
def get_local_fallback(agent_name, user_text):
    txt = user_text.lower()
    if agent_name == "Savitri":
        if "otp" in txt: return "Beta, OTP toh mobile ke peeche nahi likha..."
        return "Beta aawaz kat rahi hai... hello?"
    if agent_name == "Rajesh":
        return "Oye! Dobara phone kiya toh taange tod dunga!"
    if agent_name == "Police":
        return "This number is under surveillance. Disconnect immediately."
    return "..."

# ==========================================
# 4. AI CALL FUNCTIONS
# ==========================================
async def ask_groq(sys_prompt, user_text):
    if not groq_client: return None
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
            model="llama3-8b-8192"
        )
        return res.choices[0].message.content
    except: return None

async def ask_google(sys_prompt, user_text):
    if not google_client: return None
    full = f"{sys_prompt}\n\nUser: {user_text}"
    models = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-pro']
    for m in models:
        try:
            res = google_client.models.generate_content(model=m, contents=full)
            if res.text: return res.text
        except: continue
    return None

async def ask_openai(sys_prompt, user_text):
    if not openai_client: return None
    try:
        # OpenAI ko last me rakha hai, agar 429 aaye toh catch karke ignore karega
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}]
        )
        return res.choices[0].message.content
    except: return None

# ==========================================
# 5. MAIN AGENT LOGIC (WATERFALL)
# ==========================================
async def get_agent_response(user_input, history=None):
    if not user_input: return "Hello?"

    # 1. Choose Agent
    agent_name, sys_prompt = get_active_agent(history)
    logger.info(f"🎭 Active: {agent_name}")

    # Build Context
    hist_txt = ""
    if history:
        for m in history: 
            if isinstance(m, dict): hist_txt += f"{m.get('sender','')}: {m.get('text','')}\n"
    
    final_input = f"History:\n{hist_txt}\nScammer: {user_input}\nReply as {agent_name}:"

    reply = None
    source = "None"

    # Priority 1: Groq (Fastest)
    if not reply:
        reply = await ask_groq(sys_prompt, final_input)
        source = "Groq"

    # Priority 2: Google (Reliable)
    if not reply:
        reply = await ask_google(sys_prompt, final_input)
        source = "Google"

    # Priority 3: OpenAI (Last Option - Jaise tumne bola)
    if not reply:
        reply = await ask_openai(sys_prompt, final_input)
        source = "OpenAI"

    # Final Safety: Local Script
    if not reply:
        logger.warning("⚠️ All AI Failed. Using Local.")
        reply = get_local_fallback(agent_name, user_input)
        source = "Local"

    logger.info(f"🗣️ Answer via {source}")
    return reply.strip()
