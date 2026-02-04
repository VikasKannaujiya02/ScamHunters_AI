import os
import random

def generate_tracking_link(file_type="apk"):
    """
    Generates a realistic looking phishing link bait.
    """
    os.makedirs("assets", exist_ok=True)
    
    # Scammer ke interest ke hisaab se fake files
    baits = [
        "SBI_KYC_Update_v2.apk",
        "Refund_Form_2026.pdf",
        "Video_Proof_Leaked.mp4",
        "Claim_Bonus_Reward.html"
    ]
    
    # Select random bait
    chosen_file = random.choice(baits)
    
    # Real file create karo taaki 404 error na aaye agar wo click kare
    filepath = os.path.join("assets", chosen_file)
    with open(filepath, "w") as f:
        f.write("<html><h1>System Error: IP Logged... Just kidding, you are caught!</h1></html>")
        
    return chosen_file