import os
import logging
from google import genai        # New Google Library
from openai import OpenAI       # OpenAI Library
from groq import Groq           # Groq Library

# Logger Setup
logger = logging.getLogger("ScamHunters_Ultimate")

# ==========================================
# 1. SETUP ALL AI CLIENTS (MULTI-MODEL)
# ==========================================

# A. Groq Setup (Priority 1 - Fastest)
groq_key = os.getenv("GROQ_API_KEY")
groq_client = None
if groq_key:
    try:
        groq_client = Groq(api_key=groq_key)
        logger.info("✅ Groq Connected.")
    except: logger.error("❌ Groq Failed.")

# B. OpenAI Setup (Priority 2 - Smartest)
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if openai_key:
    try:
        openai_client = OpenAI(api_key=openai_key)
        logger.info("✅ OpenAI Connected.")
    except: logger.error("❌ OpenAI Failed.")

# C. Google Gemini Setup (Priority 3 - Backup)
# Using NEW library 'google-genai' to fix 404 errors
google_key = os.getenv("GEMINI_API_KEY")
google_client = None
if google_key:
    try:
        google_client = genai.Client(api_key=google_key)
        logger.info("✅ Google Gemini Connected.")
    except: logger.error("❌ Gemini Failed.")


# ==========================================
# 2. MULTI-AGENT PERSONAS (3 CHARACTERS)
# ==========================================

PROMPT_SAVITRI = """
ROLE: Savitri Devi (65 yr old woman).
TONE: Confused, slow, Hinglish.
GOAL: Waste time, ask stupid questions about OTP/Bank.
"""

PROMPT_RAJESH = """
ROLE: Rajesh (Savitri's Angry Son).
TONE: Aggressive, suspicious, Hindi.
GOAL: Scold the scammer. "Tu kaun hai?", "Phone rakh!".
"""

PROMPT_POLICE = """
ROLE: Inspector Vijay (Cyber Cell).
TONE: Strict, Legal, Authoritative.
GOAL: Threaten the scammer. "Call Traced.", "Location Locked.".
"""

def get_active_persona(history):
    """
    Decides WHO speaks based on conversation length.
    0-3 msgs: Savitri (Timepass)
    4-7 msgs: Rajesh (Aggression)
    8+ msgs: Police (Threat)
    """
    count = len(history) if history else 0
    if count < 4:
        return PROMPT_SAVITRI, "Savitri Devi"
    elif count < 8:
        return PROMPT_RAJESH, "Rajesh (Son)"
    else:
        return PROMPT_POLICE, "Inspector Vijay"


# ==========================================
# 3. HELPER FUNCTIONS (CALLING AI MODELS)
# ==========================================

async def ask_groq(system_prompt, user_text):
    if not groq_client: return None
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
            model="llama3-70b-8192"
        )
        return res.choices[0].message.content
    except: return None

async def ask_openai(system_prompt, user_text):
    if not openai_client: return None
    try:
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}]
        )
        return res.choices[0].message.content
    except: return None

async def ask_google(system_prompt, user_text):
    if not google_client: return None
    # Google needs combined prompt
    full_text = system_prompt + "\n\nUser: " + user_text
    # Retry Logic for 404 Errors
    models = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-pro']
    for m in models:
        try:
            res = google_client.models.generate_content(model=m, contents=full_text)
            if res.text: return res.text
        except: continue
    return None


# ==========================================
# 4. MAIN AGENT FUNCTION (THE BRAIN)
# ==========================================
async def get_agent_response(user_input, history=None):
    if not user_input: return "Hello?"

    # Step 1: Decide WHO is speaking (Multi-Agent)
    persona_prompt, agent_name = get_active_persona(history)
    logger.info(f"🎭 Active Agent: {agent_name}")

    # Step 2: Build Context (Memory)
    history_text = ""
    if history and isinstance(history, list):
        for msg in history:
            if isinstance(msg, dict):
                s = msg.get('sender', '')
                t = msg.get('text', '')
                history_text += f"{s}: {t}\n"
    
    final_input = f"History:\n{history_text}\nScammer says: {user_input}\nReply as {agent_name}:"

    # Step 3: Waterfall AI Call (Multi-Model)
    reply = None
    source = "None"

    # Priority 1: Groq
    if not reply:
        reply = await ask_groq(persona_prompt, final_input)
        source = "Groq"
    
    # Priority 2: OpenAI
    if not reply:
        reply = await ask_openai(persona_prompt, final_input)
        source = "OpenAI"

    # Priority 3: Google (Fixes 404)
    if not reply:
        reply = await ask_google(persona_prompt, final_input)
        source = "Google"

    # Step 4: Final Output
    if reply:
        logger.info(f"🗣️ {agent_name} ({source}): {reply}")
        return reply.strip()
    else:
        return "Network Error... Hello?"
