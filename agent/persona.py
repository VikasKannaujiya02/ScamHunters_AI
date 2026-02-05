import os
import logging
from google import genai
from groq import Groq
from openai import OpenAI

# Logger
logger = logging.getLogger("ScamHunters_Finalv2")

# ==========================================
# 1. API CLIENT SETUP
# ==========================================

# A. Groq (Priority 1: Fastest)
groq_key = os.getenv("GROQ_API_KEY")
groq_client = None
if groq_key:
    try:
        groq_client = Groq(api_key=groq_key)
        logger.info("✅ Groq Connected.")
    except: logger.error("❌ Groq Failed.")

# B. Google Gemini (Priority 2: Reliable)
google_key = os.getenv("GEMINI_API_KEY")
google_client = None
if google_key:
    try:
        google_client = genai.Client(api_key=google_key)
        logger.info("✅ Gemini Connected.")
    except: logger.error("❌ Gemini Failed.")

# C. OpenAI (Priority 3: Backup)
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if openai_key:
    try:
        openai_client = OpenAI(api_key=openai_key)
        logger.info("✅ OpenAI Connected.")
    except: logger.error("❌ OpenAI Failed.")


# ==========================================
# 2. MULTI-AGENT PERSONAS
# ==========================================
PERSONAS = {
    "Savitri": "You are Savitri Devi, 65. Confused old lady. Speak Hinglish. Waste time. Ask stupid questions. NEVER share OTP.",
    "Rajesh": "You are Rajesh, Savitri's son. Angry. Abuse the scammer. 'Tu kaun hai?', 'Police bulaunga'.",
    "Police": "You are Inspector Vijay. Cyber Cell. 'Call Traced', 'Location Locked', 'Surrender immediately'."
}

def get_active_agent(history):
    count = len(history) if history else 0
    if count < 4: return "Savitri", PERSONAS["Savitri"]
    elif count < 8: return "Rajesh", PERSONAS["Rajesh"]
    else: return "Police", PERSONAS["Police"]


# ==========================================
# 3. AI GENERATION FUNCTIONS (UPDATED MODELS)
# ==========================================

async def ask_groq(sys_prompt, user_text):
    if not groq_client: return None
    
    # --- UPDATED MODEL LIST (OLD WALA EXPIRE HO GAYA THA) ---
    models = [
        "llama-3.3-70b-versatile",  # Latest & Best
        "llama-3.1-70b-versatile",  # Backup
        "llama-3.1-8b-instant",     # Fastest
        "mixtral-8x7b-32768"        # Alternative
    ]
    
    for m in models:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                model=m
            )
            return res.choices[0].message.content
        except Exception as e:
            logger.warning(f"⚠️ Groq Model {m} Failed: {e}")
            continue # Try next model
            
    return None

async def ask_google(sys_prompt, user_text):
    if not google_client: return None
    full_prompt = f"{sys_prompt}\n\nUser: {user_text}"
    
    # Google Models List (Retry Logic)
    models = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-001',
        'gemini-2.0-flash-exp',
        'gemini-pro',
        'gemini-1.0-pro'
    ]
    
    for m in models:
        try:
            res = google_client.models.generate_content(model=m, contents=full_prompt)
            if res.text: return res.text
        except: continue
    return None

async def ask_openai(sys_prompt, user_text):
    if not openai_client: return None
    try:
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}]
        )
        return res.choices[0].message.content
    except: return None


# ==========================================
# 4. MAIN AGENT LOGIC
# ==========================================
async def get_agent_response(user_input, history=None):
    if not user_input: return "Hello?"

    # 1. Identify Agent
    agent_name, sys_prompt = get_active_agent(history)
    logger.info(f"🎭 Speaking as: {agent_name}")

    # 2. History Context
    hist_txt = ""
    if history:
        for m in history: 
            if isinstance(m, dict): hist_txt += f"{m.get('sender','')}: {m.get('text','')}\n"
    
    final_input = f"Chat History:\n{hist_txt}\nScammer said: {user_input}\nReply as {agent_name}:"

    reply = None
    source = "None"

    # Attempt 1: Groq (Updated Models)
    if not reply:
        reply = await ask_groq(sys_prompt, final_input)
        source = "Groq"

    # Attempt 2: Google (Backup)
    if not reply:
        reply = await ask_google(sys_prompt, final_input)
        source = "Google"

    # Attempt 3: OpenAI (Last Resort)
    if not reply:
        reply = await ask_openai(sys_prompt, final_input)
        source = "OpenAI"

    if reply:
        logger.info(f"🗣️ Generated via {source}")
        return reply.strip()
    else:
        return "System Error: All AI Models Failed."
