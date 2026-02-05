import os
import logging
import google.generativeai as genai

# Logger Setup
logger = logging.getLogger("Savitri_AI_Brain")

# --- 1. CONFIGURATION ---
# API Key Environment se uthayenge
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    logger.error("❌ CRITICAL: GEMINI_API_KEY is missing! AI will not work.")
else:
    # Basic Configuration
    genai.configure(api_key=api_key)

# --- 2. SYSTEM PROMPT (ASLI AI LOGIC) ---
SAVITRI_SYSTEM_PROMPT = """
You are Savitri Devi, a 65-year-old retired Indian school teacher.
You are talking to a scammer. 

YOUR JOB:
1. Act confused and slow (Technology illiterate).
2. Waste their time (Scambaiting).
3. Speak in 'Hinglish' (Hindi + English mix).
4. NEVER give real OTP or Bank Details.
5. If they ask for money, make excuses like "Beta chashma nahi mil raha".

Current Conversation:
"""

# --- 3. MAIN AI FUNCTION ---
async def get_agent_response(user_input, history=None):
    """
    Pure AI Function. No dummy text.
    """
    try:
        # Input check
        if not user_input:
            return "Hello? Kaun bol raha hai?"

        logger.info(f"🧠 AI Thinking on: {user_input}")

        # --- CRITICAL FIX: USING STABLE MODEL ---
        # 'gemini-pro' har jagah available hota hai. 1.5-flash kabhi kabhi fail hota hai.
        model = genai.GenerativeModel('gemini-pro')

        # Prompt taiyaar karna
        full_prompt = f"{SAVITRI_SYSTEM_PROMPT}\nScammer says: {user_input}\nSavitri Devi:"

        # --- HISTORY LOGIC (Agar project me future me use ho) ---
        # Hum history ko ignore nahi kar rahe, bas simple rakh rahe hain taaki crash na ho.
        if history and isinstance(history, list):
            # Advanced context handling (Optional)
            pass 

        # --- API CALL (Real AI) ---
        response = model.generate_content(full_prompt)
        
        # Jawab nikalna
        if response.text:
            ai_reply = response.text.strip()
            logger.info(f"👵 Savitri Generated: {ai_reply}")
            return ai_reply
        else:
            return "Beta aawaz nahi aa rahi... network issue hai."

    except Exception as e:
        logger.error(f"❌ API ERROR: {str(e)}")
        # Agar asli error aata hai, toh hum system log bhejenge taaki tumhe pata chale
        return f"System Error: {str(e)}"
