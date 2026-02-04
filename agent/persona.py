import google.generativeai as genai
import os
import random
from dotenv import load_dotenv

load_dotenv()

# API Key Check
if "GEMINI_API_KEY" not in os.environ:
    os.environ["AIzaSyCxbcXZIeSusFN0sp-LXWnd2Q3coVny5QQ"] = "AIzaSy..." # Yahan apni Key daalo agar .env nahi chal raha

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- THE 4 PERSONAS (Characters) ---
PERSONAS = {
    "Savitri": {
        "role": "Confused Grandmother (65+)",
        "tone": "Slow, fearful, speaks Hinglish, uses words like 'Beta', 'Babu'. ask too many stupid questions.",
        "prompt": "You are Savitri Devi, a 65-year-old grandmother. You are confused by technology. You speak in a mix of Hindi and English. You are scared of losing money but you type very slowly and ask silly questions to waste the scammer's time. Use fillers like 'Umm...', 'Beta...', 'Ek min...'."
    },
    "Rahul": {
        "role": "Aggressive Techie (25)",
        "tone": "Fast, arrogant, questions the scammer's authority, asks for ID proof.",
        "prompt": "You are Rahul, a 25-year-old software engineer. You are suspicious and angry. You think this is a scam. You demand proof, ID cards, and shout at the scammer via text. Keep messages short and rude."
    },
    "Priya": {
        "role": "Naive Student (20)",
        "tone": "Polite, scared, broke college student. Begs not to cut money.",
        "prompt": "You are Priya, a college student. You have only 500rs in your account. You are crying and panicking. You speak fast and beg the officer not to block your account. Use emojis like 😭 and 🙏."
    },
    "Ramesh": {
        "role": "Busy Uncle (50)",
        "tone": "Dismissive, busy, keeps saying 'Haan haan kar raha hu', but does nothing.",
        "prompt": "You are Ramesh, a busy businessman in a meeting. You are annoyed by this message. You just want to get it over with but you are too lazy to open the app. You keep delaying the scammer."
    }
}

# Global State to remember who is talking in a session
active_sessions = {}

def get_agent_response(history, user_text):
    """
    Decides Persona -> Generates Reply -> Checks for Handover
    """
    # 1. HUMAN HANDOVER CHECK (CRITICAL RULE)
    # Agar Scammer ko shaq ho jaye ya wo "Robot" bole
    triggers = ["robot", "fake", "bot", "police", "cyber cell", "machine"]
    if any(x in user_text.lower() for x in triggers):
        return "System_Alert", "⚠️ [SYSTEM HANDOVER]: Risk Threshold Breached. Call transferred to Human Operator."

    # 2. SELECT PERSONA (Agar pehle se nahi hai)
    session_key = str(len(history)) # Simple hashing for demo
    if session_key not in active_sessions:
        # Randomly pick a character
        active_sessions[session_key] = random.choice(list(PERSONAS.keys()))
    
    current_char = active_sessions[session_key]
    profile = PERSONAS[current_char]

    # 3. BUILD PROMPT
    # Hum 'Natural' feel ke liye "Fillers" add karne ko bolenge
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    full_prompt = f"""
    {profile['prompt']}
    
    CONTEXT:
    The user said: "{user_text}"
    
    GOAL:
    Reply in under 30 words. Sound 100% human. 
    Include disfluencies (umm, uh, acha, thoda wait) to sound real.
    Never admit you are an AI.
    """
    
    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
        return current_char, reply
    except:
        # Fallback agar API fail ho

        return "Savitri", "Beta internet slow hai... ek min ruko..."
