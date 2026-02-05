import os
import logging
from google import genai  # NEW OFFICIAL LIBRARY (Fixes 404 Error)

# Logger Setup
logger = logging.getLogger("Savitri_AI_Brain")

# --- 1. MULTI-AGENT CONFIGURATION ---
# Hum check kar rahe hain ki API key hai ya nahi
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    logger.error("❌ CRITICAL: GEMINI_API_KEY is missing! Agent cannot function.")
    client = None
else:
    try:
        # Connecting to Google's New GenAI Client
        client = genai.Client(api_key=api_key)
        logger.info("✅ Google GenAI Client Connected Successfully.")
    except Exception as e:
        logger.error(f"❌ Client Connection Failed: {e}")
        client = None

# --- 2. AGENT PERSONA: SAVITRI DEVI (The Brain) ---
SAVITRI_SYSTEM_PROMPT = """
ROLE: You are Savitri Devi, a 65-year-old retired Indian school teacher living in Varanasi.
CURRENT SITUATION: You are talking to a cyber-criminal (scammer) on WhatsApp/SMS.

OBJECTIVE:
- Waste the scammer's time (Scambaiting) as much as possible.
- Act confused, technologically illiterate, and slow.
- Pretend to fall for the trap but never actually give the correct details.

BEHAVIOR GUIDELINES:
1. **Language:** Speak in 'Hinglish' (Hindi + English mix). Use terms like "Beta", "Babu", "Chashma nahi mil raha".
2. **Strategy:** If they ask for OTP, give a wrong 6-digit number (e.g., 123456) or ask "Ye OTP kahan likha hai?".
3. **Money:** If they ask for payment, say "Paytm server down hai" or "Mere bete se poochna padega".
4. **Safety:** NEVER reveal real personal information.

EXAMPLE INTERACTION:
Scammer: "Send OTP immediately or account blocked."
Savitri: "Arre beta, itni jaldi kyun? Main abhi chai bana rahi hu. Ye OTP mobile ke peeche likha hota hai kya?"
"""

# --- 3. MAIN INTELLIGENT AGENT FUNCTION ---
async def get_agent_response(user_input, history=None):
    """
    Main entry point for the AI Agent.
    Supports Conversation History and Multi-turn context.
    """
    # 1. Input Validation
    if not user_input:
        return "Hello? Kaun bol raha hai? Aawaz nahi aa rahi."

    # 2. Client Check
    if not client:
        return "System Error: AI Engine not connected (Check API Key)."

    try:
        logger.info(f"🧠 AI Thinking on: {user_input}")

        # --- CONTEXT & MEMORY MANAGEMENT ---
        # Hum purani baatein (History) jod rahe hain taaki Savitri bhool na jaye
        full_conversation_context = SAVITRI_SYSTEM_PROMPT + "\n\n--- PAST CONVERSATION ---\n"
        
        if history and isinstance(history, list):
            for msg in history:
                if isinstance(msg, dict):
                    sender = msg.get('sender', 'Unknown')
                    text = msg.get('text', '')
                    full_conversation_context += f"{sender}: {text}\n"
        
        # Adding current message
        full_conversation_context += f"\n--- NEW MESSAGE ---\nScammer: {user_input}\nSavitri Devi:"

        # --- 4. GENERATING RESPONSE (NEW ENGINE) ---
        # Using 'gemini-1.5-flash' because it is fast and supports the new library.
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_conversation_context
        )
        
        # 5. Extracting and Returning Reply
        if response.text:
            ai_reply = response.text.strip()
            logger.info(f"👵 Savitri Generated: {ai_reply}")
            return ai_reply
        else:
            return "Beta, network issue hai shayad... phir se bolna?"

    except Exception as e:
        logger.error(f"❌ AI CRITICAL ERROR: {str(e)}")
        # Fail-safe logic to prevent server crash
        return f"System Error: AI failed to generate response. ({str(e)})"
