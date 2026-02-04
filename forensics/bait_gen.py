from PIL import Image, ImageDraw, ImageFont
import random
import os
from datetime import datetime

def generate_fake_payment(amount_text="5000"):
    """
    Generates a 100% Realistic PhonePe Screenshot with Android Status Bar.
    """
    os.makedirs("assets", exist_ok=True)
    filename = f"payment_proof_{random.randint(1000,9999)}.png"
    filepath = os.path.join("assets", filename)
    
    # Standard Android Resolution
    W, H = 1080, 2400
    
    # Colors
    PHONEPE_GREEN = (32, 185, 95) # Exact Hex Color
    BG_COLOR = (245, 245, 245)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (100, 100, 100)
    
    img = Image.new('RGB', (W, H), color=BG_COLOR)
    d = ImageDraw.Draw(img)
    
    # --- 1. ANDROID STATUS BAR (Top) ---
    d.rectangle([(0, 0), (W, 80)], fill=PHONEPE_GREEN)
    # Time
    curr_time = datetime.now().strftime("%H:%M")
    d.text((50, 20), curr_time, fill=WHITE, font_size=35)
    # Battery/Wifi/Signal (Simulated with simple shapes)
    d.rectangle([(W-150, 25), (W-100, 55)], outline=WHITE, width=3) # Battery
    d.rectangle([(W-148, 27), (W-110, 53)], fill=WHITE) # Battery Fill
    d.arc([(W-250, 20), (W-200, 60)], start=45, end=135, fill=WHITE, width=3) # Wifi arc
    
    # --- 2. GREEN SUCCESS HEADER ---
    d.rectangle([(0, 80), (W, 600)], fill=PHONEPE_GREEN)
    
    # --- 3. ANIMATED TICK MARK (Circle + Check) ---
    cx, cy = W//2, 300
    r = 100
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=WHITE)
    # Draw Tick manually for thickness
    points = [(cx-40, cy), (cx-10, cy+40), (cx+60, cy-50)]
    d.line(points, fill=PHONEPE_GREEN, width=15, joint="curve")
    
    # --- 4. TEXT DETAILS ---
    try:
        font_main = ImageFont.truetype("arial.ttf", 60)
        font_amt = ImageFont.truetype("arial.ttf", 110)
        font_sm = ImageFont.truetype("arial.ttf", 40)
    except:
        font_main = ImageFont.load_default()
        font_amt = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # Helper to center text
    def draw_center(text, y, font, fill):
        bbox = d.textbbox((0, 0), text, font=font)
        w_text = bbox[2] - bbox[0]
        d.text(((W - w_text)/2, y), text, font=font, fill=fill)

    draw_center("Payment Successful", 450, font_main, WHITE)
    
    # Transaction ID (Top small)
    txn_id = f"T{random.randint(230000000000, 239999999999)}"
    draw_center(f"Txn ID: {txn_id}", 530, font_sm, (220, 255, 220))
    
    # --- 5. AMOUNT & RECEIVER ---
    # White Card Effect
    d.rounded_rectangle([(50, 550), (W-50, 900)], radius=30, fill=WHITE)
    
    draw_center(f"Paid to", 600, font_sm, GREY)
    draw_center("Scammer Account", 650, font_main, BLACK)
    draw_center(f"₹{amount_text}", 750, font_amt, BLACK)
    
    # --- 6. BANKING DETAILS (Bottom List) ---
    # White Box for Details
    start_y = 1000
    d.rounded_rectangle([(0, start_y), (W, start_y+600)], radius=0, fill=WHITE)
    
    # Row 1: Paid On
    d.text((80, start_y+50), "Paid On", fill=GREY, font_size=40)
    d.text((W-450, start_y+50), datetime.now().strftime("%d %b %Y, %I:%M %p"), fill=BLACK, font_size=40)
    d.line([(50, start_y+150), (W-50, start_y+150)], fill=(230,230,230), width=2)
    
    # Row 2: UTR/Ref
    d.text((80, start_y+200), "Bank Ref No", fill=GREY, font_size=40)
    d.text((W-450, start_y+200), str(random.randint(100000000000, 999999999999)), fill=BLACK, font_size=40)
    d.line([(50, start_y+300), (W-50, start_y+300)], fill=(230,230,230), width=2)
    
    # Row 3: Message
    d.text((80, start_y+350), "Message", fill=GREY, font_size=40)
    d.text((W-450, start_y+350), "Payment from Victim", fill=BLACK, font_size=40)

    # --- 7. BOTTOM FOOTER ---
    # PhonePe Logo placeholder text
    draw_center("Powered by UPI & PSP Bank", H-150, font_sm, GREY)
    
    img.save(filepath)
    return filename