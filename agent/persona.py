import os
import logging
from google import genai
from groq import Groq
from openai import OpenAI

# Logger
logger = logging.getLogger("ScamHunters_Stealth")

# ==========================================
# 1. API CLIENT SETUP (SAME AS BEFORE)
# ==========================================
groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key) if groq_key else None

google_key = os.getenv("GEMINI_API_KEY")
google_client = genai.Client(api_key=google_key) if google_key else None

openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key) if openai_key else None

# ==========================================
# 2. STEALTH PERSONAS (NO POLICE - ONLY VICTIMS)
# ==========================================

# 1. Savitri (The Bait): Confused, keeps asking "Kaise karu?"
PROMPT_SAVITRI = """
ROLE: You are Savitri Devi, 65-year-old retired woman.
GOAL: Act extremely confused and technically illiterate. Keep the scammer engaged.
STRATEGY:
- Never say "No". Say "I am trying but it's not working".
- Ask them to repeat details (forces them to reveal UPI/Bank info again).
- Speak in Hinglish: "Beta, chashma nahi mil raha", "Button kaunsa dabana hai?".
- NEVER reveal that you know it is a scam.
"""

# 2. Rajesh (The Extractor): Pretends to help mom, asks for specific payment details.
PROMPT_RAJESH = """
ROLE: Rajesh, Savitri's son. You are skeptical but willing to pay if verified.
GOAL: Extract more Bank Accounts and UPI IDs from the scammer.
STRATEGY:
- Do NOT threaten them. Act like a busy man who just wants to finish this.
- Say things like: "Maa se nahi ho raha. Send me the UPI ID again, I will do it from my phone."
- Say: "This server is down. Do you have another bank account number?"
- Keep asking for "Alternative Payment Methods" to collect more intelligence.
- NEVER say you are Police. Pretend you are falling for the trap.
"""

def get_active_agent(history):
    """
    Decides WHO speaks based on conversation length.
    Maintains stealth mode.
    """
    count = len(history) if history else 0
    
    # Pehle 5 message tak Savitri (Time Waste)
    if count < 5:
        return "Savitri", PROMPT_SAVITRI
    
    # Uske baad Rajesh (Intelligence Extraction)
    # Rajesh scammer se aur details maangega "Pay" karne ke bahane.
    else:
        return "Rajesh (Son)", PROMPT_RAJESH


# ==========================================
# 3. AI GENERATION FUNCTIONS (Unchanged)
# ==========================================

async def ask_groq(sys_prompt, user_text):
    if not groq_client: return None
    # Updated Models List
    models = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
    for m in models:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                model=m
            )
            return res.choices[0].message.content
        except: continue
    return None

async def ask_google(sys_prompt, user_text):
    if not google_client: return None
    full = f"{sys_prompt}\n\nUser: {user_text}"
    models = ['gemini-1.5-flash', 'gemini-1.5-flash-001', 'gemini-2.0-flash-exp', 'gemini-pro', 'gemini-1.0-pro']
    for m in models:
        try:
            res = google_client.models.generate_content(model=m, contents=full)
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

    # 1. Identify Agent (Savitri or Rajesh) - NO POLICE
    agent_name, sys_prompt = get_active_agent(history)
    logger.info(f"🎭 Speaking as: {agent_name} (Stealth Mode)")

    # 2. History Context
    hist_txt = ""
    if history:
        for m in history: 
            if isinstance(m, dict): hist_txt += f"{m.get('sender','')}: {m.get('text','')}\n"
    
    final_input = f"Chat History:\n{hist_txt}\nScammer said: {user_input}\nReply as {agent_name}:"

    reply = None
    source = "None"

    # Execution Strategy
    if not reply: reply = await ask_groq(sys_prompt, final_input)
    if not reply: reply = await ask_google(sys_prompt, final_input)
    if not reply: reply = await ask_openai(sys_prompt, final_input)

    return reply.strip() if reply else "System Error: AI Unreachable."
