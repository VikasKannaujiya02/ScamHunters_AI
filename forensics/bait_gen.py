import os
import random
import logging
from datetime import datetime

# Logger setup
logger = logging.getLogger("Forensics_Trap")

# --- REAL IMAGE GENERATION LOGIC ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("⚠️ PIL library not found. Install 'Pillow' in requirements.txt")

def generate_fake_payment_screenshot(amount="5000"):
    """
    Generates a 100% Realistic PhonePe Screenshot using PIL.
    """
    # Safety Check: Agar Render par Pillow install nahi hua to crash nahi hoga
    if not PIL_AVAILABLE:
        return "assets/error_missing_pillow.jpg"

    try:
        os.makedirs("assets", exist_ok=True)
        filename = f"payment_proof_{random.randint(1000,9999)}.png"
        filepath = os.path.join("assets", filename)
        
        # Standard Android Resolution
        W, H = 1080, 2400
        
        # Colors
        PHONEPE_GREEN = (32, 185, 95)
        BG_COLOR = (245, 245, 245)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREY = (100, 100, 100)
        
        img = Image.new('RGB', (W, H), color=BG_COLOR)
        d = ImageDraw.Draw(img)
        
        # --- 1. ANDROID STATUS BAR ---
        d.rectangle([(0, 0), (W, 80)], fill=PHONEPE_GREEN)
        curr_time = datetime.now().strftime("%H:%M")
        
        # Font Handling (Smart Fallback)
        try:
            font_time = ImageFont.truetype("arial.ttf", 35)
            font_main = ImageFont.truetype("arial.ttf", 60)
            font_amt = ImageFont.truetype("arial.ttf", 110)
            font_sm = ImageFont.truetype("arial.ttf", 40)
        except:
            font_time = ImageFont.load_default()
            font_main = ImageFont.load_default()
            font_amt = ImageFont.load_default()
            font_sm = ImageFont.load_default()

        d.text((50, 20), curr_time, fill=WHITE, font=font_time)
        
        # Battery/Wifi Indicators
        d.rectangle([(W-150, 25), (W-100, 55)], outline=WHITE, width=3)
        d.rectangle([(W-148, 27), (W-110, 53)], fill=WHITE)
        
        # --- 2. GREEN SUCCESS HEADER ---
        d.rectangle([(0, 80), (W, 600)], fill=PHONEPE_GREEN)
        
        # --- 3. ANIMATED TICK MARK ---
        cx, cy = W//2, 300
        r = 100
        d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=WHITE)
        points = [(cx-40, cy), (cx-10, cy+40), (cx+60, cy-50)]
        d.line(points, fill=PHONEPE_GREEN, width=15, joint="curve")
        
        # --- 4. TEXT DETAILS ---
        def draw_center(text, y, font, fill):
            bbox = d.textbbox((0, 0), text, font=font)
            w_text = bbox[2] - bbox[0]
            d.text(((W - w_text)/2, y), text, font=font, fill=fill)

        draw_center("Payment Successful", 450, font_main, WHITE)
        
        txn_id = f"T{random.randint(230000000000, 239999999999)}"
        draw_center(f"Txn ID: {txn_id}", 530, font_sm, (220, 255, 220))
        
        # --- 5. AMOUNT CARD ---
        d.rounded_rectangle([(50, 550), (W-50, 900)], radius=30, fill=WHITE)
        draw_center(f"Paid to", 600, font_sm, GREY)
        draw_center("Scammer Account", 650, font_main, BLACK)
        draw_center(f"₹{amount}", 750, font_amt, BLACK)
        
        # --- 6. DETAILS LIST ---
        start_y = 1000
        d.rounded_rectangle([(0, start_y), (W, start_y+600)], radius=0, fill=WHITE)
        
        d.text((80, start_y+50), "Paid On", fill=GREY, font=font_sm)
        d.text((W-450, start_y+50), datetime.now().strftime("%d %b %Y"), fill=BLACK, font=font_sm)
        d.line([(50, start_y+150), (W-50, start_y+150)], fill=(230,230,230), width=2)
        
        # Save Image
        img.save(filepath)
        logger.info(f"✅ Generated Real Bait Image: {filename}")
        return filepath

    except Exception as e:
        logger.error(f"❌ Failed to generate screenshot: {e}")
        return None   
