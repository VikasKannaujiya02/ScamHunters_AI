import os
import logging
from google import genai  # NEW OFFICIAL LIBRARY

# Logger Setup
logger = logging.getLogger("Savitri_AI_Brain")

# --- 1. CONFIGURATION ---
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    logger.error("❌ CRITICAL: GEMINI_API_KEY is missing!")
    client = None
else:
    try:
        # Client connect kar rahe hain
        client = genai.Client(api_key=api_key)
        logger.info("✅ Google GenAI Client Connected.")
    except Exception as e:
        logger.error(f"❌ Connection Failed: {e}")
        client = None

# --- 2. SAVITRI DEVI PERSONA (ORIGINAL LOGIC) ---
SAVITRI_SYSTEM_PROMPT = """
ROLE: You are Savitri Devi, a 65-year-old retired Indian school teacher living in Varanasi.
CURRENT SITUATION: You are talking to a cyber-criminal (scammer) on WhatsApp/SMS.

OBJECTIVE:
- Waste the scammer's time (Scambaiting).
- Act confused, technologically illiterate, and slow.
- Pretend to fall for the trap but NEVER share real details.

BEHAVIOR GUIDELINES:
1. **Language:** Speak in 'Hinglish'. Use terms like "Beta", "Babu", "Chashma nahi mil raha".
2. **Strategy:** If they ask for OTP, give a wrong number (e.g., 999999) or ask "Ye kya hota hai?".
3. **Money:** Say "Paytm server down hai" or "Beta mere potey se puchna padega".
"""

# --- 3. MAIN AGENT FUNCTION (MULTI-MODEL SUPPORT) ---
async def get_agent_response(user_input, history=None):
    # 1. Input Check
    if not user_input:
        return "Hello? Kaun bol raha hai? Aawaz nahi aa rahi."

    # 2. Client Check
    if not client:
        return "System Error: AI Engine not connected (Check API Key)."

    try:
        logger.info(f"🧠 AI Thinking on: {user_input}")

        # --- CONTEXT & MEMORY (Purani baatein jodna) ---
        full_conversation_context = SAVITRI_SYSTEM_PROMPT + "\n\n--- PAST CONVERSATION ---\n"
        
        if history and isinstance(history, list):
            for msg in history:
                if isinstance(msg, dict):
                    sender = msg.get('sender', 'Unknown')
                    text = msg.get('text', '')
                    full_conversation_context += f"{sender}: {text}\n"
        
        full_conversation_context += f"\n--- NEW MESSAGE ---\nScammer: {user_input}\nSavitri Devi:"

        # --- 4. GENERATING RESPONSE (SMART RETRY LOGIC) ---
        # Hum alag-alag model names try karenge taaki 404 Error na aaye.
        # Ye loop ensure karega ki koi na koi model zaroor chale.
        models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash-8b']
        
        for model_name in models_to_try:
            try:
                # Try generating content
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_conversation_context
                )
                
                if response.text:
                    ai_reply = response.text.strip()
                    logger.info(f"👵 Savitri Generated ({model_name}): {ai_reply}")
                    return ai_reply
            
            except Exception as e:
                logger.warning(f"⚠️ Model {model_name} failed. Trying next... Error: {e}")
                continue # Agla model try karo

        # Agar saare fail ho gaye (Bahut rare)
        return "Beta, network issue hai shayad... phir se bolna?"

    except Exception as e:
        logger.error(f"❌ AI CRITICAL ERROR: {str(e)}")
        return f"System Error: AI failed. ({str(e)})"
