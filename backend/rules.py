import re

# Comprehensive Rule categories with Indian context
RULES = {
    "urgency_threat": [
        "urgent", "immediately", "last warning", "block ho jayega", "suspend", "expire",
        "action required", "within 24 hours", "final notice",
        "legal action", "penalty", "police complaint", "disconnected", "arrested",
        "fine", "warrant", "court"
    ],
    "authority": [
        "bank", "sbi", "rbi", "kyc", "atm", "customs", "police",
        "tax", "income tax", "hdfc", "icici", "trai", "jio", "airtel", "electricity board"
    ],
    "money_link": [
        "pay now", "click here", "reward", "parcel charge", "refund", "fee",
        "jackpot", "lottery", "prize", "cash", "loan pre-approved", "credit card limit", "recharge",
        "win", "gift", "claim"
    ]
}

SAFE_SIGNALS = {
    "transaction": [
        "debited", "credited", "txn", "a/c", "account ending", "upi to", "available balance",
        "payment successful", "received rs", "spent rs", "avl bal"
    ],
    "customer_care": [
        "toll free", "call customer care", "helpline", "support at"
    ]
}

def check_otp_intent(text: str) -> str:
    """
    Analyzes the text to determine the intent regarding OTPs or verification codes.
    Returns "scam" if asking to share, "safe" if warning not to share, or "neutral".
    """
    text_lower = text.lower()
    
    # Safe patterns (Warning not to share)
    safe_patterns = [
        "do not share otp", "never share otp", "bank never asks for otp", "bank never asks otp",
        "dont share otp", "no bank asks otp", "do not share your otp", "never share your otp",
        "please don't share otp", "don't share", "nobody will ask for your otp"
    ]
    
    # Scam patterns (Requesting OTP)
    scam_patterns = [
        "share otp", "send otp", "tell otp", "provide otp", "enter otp", "verify otp", 
        "confirm otp", "give otp", "forward otp", "verification code is required",
        "share code", "enter code", "send code"
    ]
    
    for pattern in safe_patterns:
        if pattern in text_lower:
            return "safe"
            
    for pattern in scam_patterns:
        if pattern in text_lower:
            return "scam"
            
    # Fallback checking if it just mentions OTP without explicit intent
    if "otp" in text_lower or "one time password" in text_lower or "verification code" in text_lower:
        # If it says 'is your otp' it's likely a standard login SMS, which is safe/neutral
        if "is your otp" in text_lower or "is your one time password" in text_lower:
            return "safe"
        # If the word OTP is just standing alone and didn't hit safe patterns, it could be a scam attempt or neutral
        # Let's consider it neutral to avoid false positives on simple transactional messages
    
    return "neutral"

def analyze_rules(text: str):
    text_lower = text.lower()
    reasons = []
    safe_signals_list = []
    highlighted_words = []
    risk_score = 0
    
    # 1. Check OTP Intent
    otp_intent = check_otp_intent(text)
    if otp_intent == "scam":
        risk_score += 3
        reasons.append("Requesting to share OTP/Verification Code (+3)")
    elif otp_intent == "safe":
        risk_score -= 3
        safe_signals_list.append("Warning not to share OTP (-3)")
    
    # 2. Check Scam Rule Categories
    for category, keywords in RULES.items():
        found_in_category = False
        for keyword in keywords:
            if category != "money_link" and keyword not in ["rs", "₹", "fee"]:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    highlighted_words.append(keyword)
                    found_in_category = True
            else:
                if keyword in text_lower:
                    highlighted_words.append(keyword)
                    found_in_category = True
        
        if found_in_category:
            if category == "money_link":
                risk_score += 2
                reasons.append("Payment link/request or suspicious money keywords (+2)")
            elif category == "urgency_threat":
                risk_score += 2
                reasons.append("Using urgency or threat language (+2)")
            elif category == "authority":
                risk_score += 2
                reasons.append("Impersonating authority or bank (+2)")
                
    # 3. Check Safe Signals
    for category, keywords in SAFE_SIGNALS.items():
        found_in_category = False
        for keyword in keywords:
            if keyword in text_lower:
                highlighted_words.append(keyword)
                found_in_category = True
                
        if found_in_category:
            if category == "transaction":
                risk_score -= 2
                safe_signals_list.append("Genuine transaction alert detected (-2)")
            elif category == "customer_care":
                risk_score -= 1
                safe_signals_list.append("Official customer care format detected (-1)")

    return risk_score, reasons, safe_signals_list, list(set(highlighted_words))
