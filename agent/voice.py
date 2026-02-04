from gtts import gTTS
import os
import random

def generate_voice_note(text, persona):
    """
    Generates Human-Like Audio with Pauses and Fillers.
    """
    os.makedirs("assets", exist_ok=True)
    filename = f"voice_{persona}_{random.randint(1000,9999)}.mp3"
    filepath = os.path.join("assets", filename)
    
    # --- REALISM LOGIC: Adding "Fillers" ---
    # Text ko modify karte hain taaki AI "Atak" kar bole (More human)
    
    human_text = text
    
    if persona == "Savitri":
        # Dadi Maa: Bahut slow, Hindi accent, 'Ji' aur 'Beta' add karegi
        lang = 'hi'
        slow = True
        human_text = f"Ji beta... {text}... umm... mujhe samajh nahi aa raha."
        
    elif persona == "Rahul":
        # Angry Guy: English accent, Fast, Thoda rude
        lang = 'en'
        slow = False
        # No fillers, just sharp text
        human_text = text
        
    elif persona == "Priya":
        # Scared Student: Hindi accent, 'Sir' add karegi
        lang = 'hi'
        slow = False
        human_text = f"Sir please... {text}... sir mein darr gayi hu."
        
    elif persona == "Ramesh":
        # Uncle: Hindi, Normal speed
        lang = 'hi'
        slow = False
        human_text = f"Arre haan bhai... {text}... kar raha hu wait karo."
        
    else:
        # Fallback
        lang = 'en'
        slow = False

    try:
        # gTTS ko Hindi ('hi') me English text padhwane se "Indian Accent" aata hai!
        tts = gTTS(text=human_text, lang=lang, slow=slow)
        tts.save(filepath)
        return filename
    except Exception as e:
        print(f"Voice Error: {e}")
        return None