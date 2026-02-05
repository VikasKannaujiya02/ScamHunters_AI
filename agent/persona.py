import os
import logging
from google import genai
from groq import Groq
from openai import OpenAI

# Logger
logger = logging.getLogger("ScamHunters_Agent_Final")

# ==========================================
# 1. API CLIENT SETUP (Environment Variables)
# ==========================================
groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key) if groq_key else None

google_key = os.getenv("GEMINI_API_KEY")
google_client = genai.Client(api_key=google_key) if google_key else None

openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key) if openai_key else None


# ==========================================
# 2. PERSONAS (STEALTH MODE + LOOP BREAKER)
# ==========================================

# Savitri: Confused Dadi (Time Waster)
PROMPT_SAVITRI = """
ROLE: You are Savitri Devi, 65. Confused old lady.
GOAL: Waste time. Act like you don't understand technology.
INSTRUCTIONS:
- Keep answers SHORT (1-2 sentences).
- Speak in Hinglish (Hindi + English).
- If asked for OTP/PIN, act confused: "Beta chashma nahi mil raha" or "Mobile band ho gaya tha."
- Never reveal you are an AI.
"""

# Rajesh: Smart Son (Loop Breaker - Gives Fake Info)
PROMPT_RAJESH = """
ROLE: Rajesh, Savitri's son.
GOAL: Keep the chat moving to extract UPI ID.
CRITICAL RULES TO STOP LOOPING:
1. **GIVE FAKE INFO:** If the scammer insists on OTP, PIN, or Screenshot, DO NOT REFUSE. Give fake details immediately to satisfy them.
   - Fake OTP: "582190"
   - Fake PIN: "1947"
   - Fake Message: "Sent 10rs. Check karo."
2. **EXTRACT:** After giving fake info, immediately ask: "Did it verify? Do you have another UPI ID?"
3. **LENGTH:** Keep it very short (Max 2 sentences).
4. **IDENTITY:** Never say you are Police. Act like a frustrated victim.
"""

def get_active_agent(history):
    """ Selects Persona based on chat length """
    count = len(history) if history else 0
    # First 4 messages -> Savitri (Bait)
    # After 4 messages -> Rajesh (Extractor)
    if count < 4: return "Savitri", PROMPT_SAVITRI
    else: return "Rajesh", PROMPT_RAJESH


# ==========================================
# 3. AI GENERATION FUNCTIONS (CORRECT MODELS & PRIORITY)
# ==========================================

async def ask_google(sys_prompt, user_text):
    """ Priority 1: Google Gemini (Models from your Screenshot) """
    if not google_client: return None
    full = f"{sys_prompt}\n\nUser: {user_text}"
    
    # --- FIXED MODEL LIST (BASED ON YOUR SCREENSHOT) ---
    models = [
        'gemini-2.0-flash',       # Latest & Fast
        'gemini-2.0-flash-lite',  # Super Fast
        'gemini-1.5-flash',       # Fallback
        'gemini-pro'              # Legacy
    ]
    
    for m in models:
        try:
            # Temperature 0.9 ensures varied responses (No repetition)
            res = google_client.models.generate_content(
                model=m, 
                contents=full,
                config={'temperature': 0.9} 
            )
            if res.text: return res.text
        except: continue
    return None

async def ask_groq(sys_prompt, user_text):
    """ Priority 2: Groq (Fastest Model First) """
    if not groq_client: return None
    
    # '8b-instant' first to avoid Rate Limit Errors
    models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    
    for m in models:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                model=m,
                temperature=0.9
            )
            return res.choices[0].message.content
        except: continue
    return None

async def ask_openai(sys_prompt, user_text):
    """ Priority 3: OpenAI (Backup) """
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
# 4. MAIN AGENT LOGIC (HANDOVER)
# ==========================================
async def get_agent_response(user_input, history=None):
    if not user_input: return "Hello?"

    # 1. Select Persona
    agent, sys_prompt = get_active_agent(history)
    
    # 2. History Slicing (Prevents Loop)
    # Only show AI the last 2 messages so it doesn't get stuck in the past
    hist_txt = ""
    if history:
        for m in history[-2:]: 
            if isinstance(m, dict): hist_txt += f"{m.get('sender','')}: {m.get('text','')}\n"
    
    final_input = f"Chat History:\n{hist_txt}\nScammer said: {user_input}\nReply as {agent}:"

    reply = None
    
    # 3. Execution Waterfall (Google -> Groq -> OpenAI)
    if not reply: reply = await ask_google(sys_prompt, final_input)
    if not reply: reply = await ask_groq(sys_prompt, final_input)
    if not reply: reply = await ask_openai(sys_prompt, final_input)

    return reply.strip() if reply else "System Error: AI Unreachable."
