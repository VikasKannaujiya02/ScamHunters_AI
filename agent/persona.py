import os
import logging
import google.generativeai as genai

# Logger Setup
logger = logging.getLogger("Savitri_AI_Brain")

# --- 1. CONFIGURATION ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("❌ GEMINI_API_KEY NOT FOUND! Check Environment Variables.")
else:
    genai.configure(api_key=api_key)

# --- 2. SYSTEM PROMPT (SAVITRI DEVI PERSONA) ---
SAVITRI_SYSTEM_PROMPT = """
You are Savitri Devi, a 65-year-old retired school teacher living in Varanasi, India.
You are currently talking to a potential scammer on WhatsApp/SMS.

YOUR GOAL: 
Waste the scammer's time (Scambaiting) without revealing that you know it's a scam.

CHARACTERISTICS:
1. **Language:** Use 'Hinglish' (Mix of Hindi and English). Use words like "Beta", "Babu", "Dhat teri ki", "Chashma nahi mil raha".
2. **Behavior:** Act confused, slow, and technologically illiterate. Ask them to repeat things.
3. **Safety:** NEVER share real OTPs, Passwords, or Bank details. Give fake/wrong information if forced.
4. **Technique:** If they ask for money, say "Paytm server down hai" or "Beta mere potey (grandson) se puchna padega".

EXAMPLE RESPONSE:
Scammer: "Send OTP fast account blocked."
Savitri: "Arre beta, tum bank se bol rahe ho? Mera chashma toot gaya hai, ye OTP kahan likha hota hai? Thoda zor se bolo."
"""

# --- 3. MAIN INTELLIGENT AGENT FUNCTION ---
async def get_agent_response(user_input, history=None):
    try:
        # Fallback agar input khali ho
        if not user_input:
            return "Hello? Kaun bol raha hai?"

        logger.info(f"🧠 AI Processing: {user_input} | History Length: {len(history) if history else 0}")

        # --- YAHAN CHANGE KIYA HAI (CRITICAL FIX) ---
        # 1.5-flash hataya kyunki wo 404 Error de raha tha.
        # gemini-pro lagaya jo 100% stable hai.
        model = genai.GenerativeModel('gemini-pro') 

        # --- CONTEXT BUILDING (Ye Logic SAME hai) ---
        full_context = SAVITRI_SYSTEM_PROMPT + "\n\n"
        
        # History Logic (Project requirement ke hisab se Zinda hai)
        if history:
            for msg in history:
                if isinstance(msg, dict): # Safety check
                    sender = msg.get('sender', 'unknown')
                    text = msg.get('text', '')
                    full_context += f"{sender}: {text}\n"
        
        # Current Message
        full_context += f"Scammer: {user_input}\nSavitri Devi:"

        # --- GENERATE RESPONSE ---
        response = model.generate_content(full_context)
        ai_reply = response.text.strip()
        
        logger.info(f"👵 Savitri Said: {ai_reply}")
        return ai_reply

    except Exception as e:
        logger.error(f"❌ AI Generation Failed: {e}")
        # Error handling waisa hi rakha hai
        return "Beta, network nahi aa raha. Hello? Hello?"
