import os
import logging
import random
from google import genai
from groq import Groq
from openai import OpenAI

# Logger
logger = logging.getLogger("ScamHunters_Final_Engine")

# ==========================================
# 1. API CLIENT SETUP
# ==========================================
# Keys check kar rahe hain
groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key) if groq_key else None

google_key = os.getenv("GEMINI_API_KEY")
google_client = genai.Client(api_key=google_key) if google_key else None

openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key) if openai_key else None


# ==========================================
# 2. PERSONAS (ANTI-LOOP FIX) 🧠
# ==========================================

# Savitri: Confused, Slow, Short sentences.
PROMPT_SAVITRI = """
ROLE: You are Savitri Devi, 65. Confused old lady.
GOAL: Waste time. Act like you don't understand technology.
INSTRUCTIONS:
- Keep answers SHORT (1-2 sentences).
- Speak in Hinglish (Hindi + English).
- Say things like: "Beta, chashma nahi mil raha", "Button kaunsa dabana hai?".
- NEVER list technical terms.
"""

# Rajesh: Skeptical Son. (STRICT NO-LOOP INSTRUCTIONS)
PROMPT_RAJESH = """
ROLE: Rajesh, Savitri's son. Skeptical but helpful.
GOAL: Extract UPI ID or Bank Account details.
CRITICAL RULES (DO NOT IGNORE):
1. KEEP IT SHORT: Max 2 sentences.
2. NO LISTS: Do NOT list multiple banks (like HDFC, ICICI, PayPal, etc.) in one message. Never do this.
3. VARY RESPONSES:
   - Ask for a new UPI ID.
   - OR Ask for a QR code.
   - OR Ask if they accept a bank transfer.
   - Do NOT repeat the previous message.
4. TONE: Frustrated but willing to pay.
"""

def get_active_agent(history):
    count = len(history) if history else 0
    # Pehle 4 message Savitri, uske baad Rajesh
    if count < 4: return "Savitri", PROMPT_SAVITRI
    else: return "Rajesh", PROMPT_RAJESH


# ==========================================
# 3. AI GENERATION FUNCTIONS (LIGHT -> HEAVY) ⚡🐢
# ==========================================

async def ask_google(sys_prompt, user_text):
    """ Priority 1: Google Gemini """
    if not google_client: return None
    full = f"{sys_prompt}\n\nUser: {user_text}"
    
    # LIST: Pehle 'Fast' (Flash), Fir 'Smart' (Pro), Fir 'Legacy' (1.0)
    models = [
        'gemini-1.5-flash',       # Light & Fast
        'gemini-1.5-flash-8b',    # Super Light
        'gemini-1.5-pro',         # Heavy & Smart
        'gemini-pro',             # Stable Backup
        'gemini-1.0-pro'          # Legacy Backup
    ]
    
    for m in models:
        try:
            # High Temperature (0.9) = Creative/Random responses (No Loop)
            res = google_client.models.generate_content(
                model=m, 
                contents=full,
                config={'temperature': 0.9} 
            )
            if res.text: return res.text
        except: continue
    return None

async def ask_groq(sys_prompt, user_text):
    """ Priority 2: Groq (Agar Google fail ho) """
    if not groq_client: return None
    
    # LIST: Pehle 'Instant' (Fast), Fir 'Versatile' (Heavy)
    models = [
        "llama-3.1-8b-instant",     # Light & Super Fast (No Rate Limit)
        "llama-3.3-70b-versatile",  # Heavy & Smart
        "mixtral-8x7b-32768"        # Balanced
    ]
    
    for m in models:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                model=m,
                temperature=0.9
            )
            return res.choices[0].message.content
        except: continue # Try next model
    return None

async def ask_openai(sys_prompt, user_text):
    """ Priority 3: OpenAI (Last Resort) """
    if not openai_client: return None
    try:
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
            temperature=0.9
        )
        return res.choices[0].message.content
    except: return None


# ==========================================
# 4. MAIN AGENT LOGIC (WATERFALL)
# ==========================================
async def get_agent_response(user_input, history=None):
    if not user_input: return "Hello?"

    agent, sys_prompt = get_active_agent(history)
    logger.info(f"🎭 Agent Active: {agent}")

    # --- HISTORY SLICING (LOOP KILLER) ---
    # Hum AI ko puri history nahi, sirf LAST 3 MESSAGES denge.
    # Isse wo purani baatein bhool jayega aur 'Repeat' nahi karega.
    hist_txt = ""
    if history:
        recent_history = history[-3:] # Only last 3
        for m in recent_history: 
            if isinstance(m, dict): hist_txt += f"{m.get('sender','')}: {m.get('text','')}\n"
    
    final_input = f"Recent Chat:\n{hist_txt}\nScammer said: {user_input}\nReply as {agent}:"

    reply = None
    
    # --- ORDER: GEMINI -> GROQ -> OPENAI ---
    
    # 1. Google Gemini (Pehle)
    if not reply: 
        reply = await ask_google(sys_prompt, final_input)

    # 2. Groq (Agar Google fail)
    if not reply: 
        reply = await ask_groq(sys_prompt, final_input)

    # 3. OpenAI (Agar dono fail)
    if not reply: 
        reply = await ask_openai(sys_prompt, final_input)

    return reply.strip() if reply else "System Error: AI Unreachable."
