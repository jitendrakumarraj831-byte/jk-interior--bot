"""
JK Interior WhatsApp Auto-Reply Bot
====================================
Owner  : Jitendra Kumar
Business: JK Interior
Phone  : +918651070831
Location: Forbesganj / Araria (Bihar)

HOW TO DEPLOY
-------------
1. Install dependencies:
       pip install flask twilio

2. Set your Twilio credentials as environment variables:
       export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
       export TWILIO_AUTH_TOKEN="your_auth_token"

3. Run the server:
       python jk_interior_whatsapp_bot.py

4. Expose the server using ngrok (for testing):
       ngrok http 5000

5. Set the Twilio WhatsApp sandbox webhook URL to:
       https://<your-ngrok-url>/webhook

Note: For production, deploy this script on a VPS/cloud server with a
      real domain and HTTPS certificate (e.g., using Nginx + Gunicorn).
"""

import re
import os
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Business Configuration ────────────────────────────────────────────────────
BUSINESS_NAME = "JK Interior"
OWNER_NAME = "Jitendra Kumar"
PHONE = "+918651070831"
LOCATION = "Forbesganj / Araria (Bihar)"

# ── Price Rates (₹ per sq ft) ────────────────────────────────────────────────
PRICE_RATES = {
    "false_ceiling": {
        "min": 65,
        "max": 95
    },
    "pvc_ceiling": {
        "min": 55,
        "max": 80
    },
    "wpc_panel": {
        "min": 90,
        "max": 130
    },
    "partition": {
        "min": 70,
        "max": 110
    },
    "tv_unit": {
        "min": 800,
        "max": 1500
    },  # per running foot
}


# ── Welcome Menu ──────────────────────────────────────────────────────────────
def get_welcome_menu() -> str:
    return ("🙏 *Namaste! Welcome to JK Interior* 🏠\n\n"
            "Hum interior aur ceiling design ka kaam karte hain.\n\n"
            "1️⃣  False Ceiling\n"
            "2️⃣  PVC Ceiling\n"
            "3️⃣  WPC Wall Panel\n"
            "4️⃣  Partition Wall\n"
            "5️⃣  TV Unit Design\n"
            "6️⃣  Price / Estimate\n"
            "7️⃣  Design Photos\n"
            "8️⃣  Contact / Site Visit\n\n"
            "💡 Room size bhej kar estimate paayein\n"
            "    Example: *12x10*")


# ── Service Detail Responses ──────────────────────────────────────────────────
def get_false_ceiling_info() -> str:
    r = PRICE_RATES["false_ceiling"]
    return ("🏠 *False Ceiling (Gypsum / POP)*\n\n"
            "✅ Gypsum Board Ceiling\n"
            "✅ POP False Ceiling\n"
            "✅ LED Cove Lighting\n"
            "✅ Modern & Classic Designs\n\n"
            f"💰 *Price Range:* ₹{r['min']} – ₹{r['max']} per sq ft\n\n"
            "📐 Room size bhej kar exact estimate paayein.\n"
            "    Example: *12x10*\n\n"
            "📞 Contact: +918651070831")


def get_pvc_ceiling_info() -> str:
    r = PRICE_RATES["pvc_ceiling"]
    return ("🏠 *PVC Ceiling*\n\n"
            "✅ Waterproof & Long-lasting\n"
            "✅ Low Maintenance\n"
            "✅ Bathroom / Kitchen ke liye Perfect\n"
            "✅ 3D & Printed Designs Available\n\n"
            f"💰 *Price Range:* ₹{r['min']} – ₹{r['max']} per sq ft\n\n"
            "📐 Room size bhej kar exact estimate paayein.\n"
            "    Example: *12x10*\n\n"
            "📞 Contact: +918651070831")


def get_wpc_panel_info() -> str:
    r = PRICE_RATES["wpc_panel"]
    return ("🧱 *WPC Wall Panel*\n\n"
            "✅ Wood Plastic Composite – Premium Look\n"
            "✅ Moisture & Termite Resistant\n"
            "✅ Drawing Room & Bedroom ke liye Best\n"
            "✅ Easy Installation\n\n"
            f"💰 *Price Range:* ₹{r['min']} – ₹{r['max']} per sq ft\n\n"
            "📐 Wall size bhej kar exact estimate paayein.\n"
            "    Example: *12x10*\n\n"
            "📞 Contact: +918651070831")


def get_partition_wall_info() -> str:
    r = PRICE_RATES["partition"]
    return ("🚪 *Partition Wall*\n\n"
            "✅ Gypsum / Glass / PVC Partition\n"
            "✅ Office & Home Partition\n"
            "✅ Sliding Door Partition Available\n"
            "✅ Custom Size & Design\n\n"
            f"💰 *Price Range:* ₹{r['min']} – ₹{r['max']} per sq ft\n\n"
            "📐 Area size bhej kar exact estimate paayein.\n"
            "    Example: *10x8*\n\n"
            "📞 Contact: +918651070831")


def get_tv_unit_info() -> str:
    r = PRICE_RATES["tv_unit"]
    return ("📺 *TV Unit Design*\n\n"
            "✅ Modern & Contemporary Designs\n"
            "✅ With LED Backlight Option\n"
            "✅ Wall-mounted & Floor Units\n"
            "✅ PVC / Laminate / Wood Finish\n\n"
            f"💰 *Price Range:* ₹{r['min']} – ₹{r['max']} per running foot\n\n"
            "📐 Wall width bhej kar exact estimate paayein.\n"
            "    Example: *10x0* (sirf width zaroor hai)\n\n"
            "📞 Contact: +918651070831")


def get_estimate_prompt() -> str:
    return ("📐 *Price Estimate*\n\n"
            "Apne room ka size bhejiye:\n"
            "    Format: *LengthxWidth*\n"
            "    Example: *12x10*  ya  *15x12*\n\n"
            "Hum aapko turant estimate de denge! 🙂")


def get_design_photos_info() -> str:
    return ("📸 *Design Photos*\n\n"
            "Hamari design photos dekhne ke liye:\n\n"
            "📱 WhatsApp pe message karein:\n"
            "    👉 +918651070831\n\n"
            "Hum aapko latest design photos bhej denge.\n\n"
            "Ya seedha call karein:\n"
            f"    📞 {PHONE}")


def get_contact_info() -> str:
    return ("📞 *Contact & Site Visit*\n\n"
            f"👤 Owner  : {OWNER_NAME}\n"
            f"🏢 Business: {BUSINESS_NAME}\n"
            f"📱 Phone  : {PHONE}\n"
            f"📍 Location: {LOCATION}\n\n"
            "🕐 Working Hours: 9 AM – 7 PM (Mon – Sat)\n\n"
            "Site visit ke liye call ya WhatsApp karein.\n"
            "Hum free estimate dete hain! 😊")


# ── Room Size Estimator ───────────────────────────────────────────────────────
ROOM_SIZE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*[xX×*]\s*(\d+(?:\.\d+)?)")


def calculate_estimate(length: float, width: float) -> str:
    sqft = length * width

    fc_min = round(sqft * PRICE_RATES["false_ceiling"]["min"])
    fc_max = round(sqft * PRICE_RATES["false_ceiling"]["max"])
    pvc_min = round(sqft * PRICE_RATES["pvc_ceiling"]["min"])
    pvc_max = round(sqft * PRICE_RATES["pvc_ceiling"]["max"])
    wpc_min = round(sqft * PRICE_RATES["wpc_panel"]["min"])
    wpc_max = round(sqft * PRICE_RATES["wpc_panel"]["max"])
    par_min = round(sqft * PRICE_RATES["partition"]["min"])
    par_max = round(sqft * PRICE_RATES["partition"]["max"])

    return (
        f"📐 *Room Size: {length:.0f} × {width:.0f} ft = {sqft:.0f} sq ft*\n\n"
        "💰 *Estimated Price:*\n\n"
        f"🏠 False Ceiling  : ₹{fc_min:,} – ₹{fc_max:,}\n"
        f"🏠 PVC Ceiling    : ₹{pvc_min:,} – ₹{pvc_max:,}\n"
        f"🧱 WPC Wall Panel : ₹{wpc_min:,} – ₹{wpc_max:,}\n"
        f"🚪 Partition Wall : ₹{par_min:,} – ₹{par_max:,}\n\n"
        "⚠️  Yeh estimate approximate hai.\n"
        "    Final price site visit ke baad confirm hogi.\n\n"
        f"📞 Call / WhatsApp: {PHONE}\n"
        f"📍 {LOCATION}")


def parse_room_size(text: str):
    match = ROOM_SIZE_PATTERN.search(text)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None


# ── Keyword Classifier ────────────────────────────────────────────────────────
GREETINGS = {
    "hi", "hello", "hlo", "hii", "hey", "namaste", "namaskar", "jai hind",
    "ram ram", "assalamu alaikum", "salam", "start", "menu"
}

KEYWORD_MAP = {
    "false ceiling": "1",
    "gypsum": "1",
    "pop ceiling": "1",
    "pvc ceiling": "2",
    "pvc": "2",
    "wpc": "3",
    "wall panel": "3",
    "partition": "4",
    "wall partition": "4",
    "tv unit": "5",
    "tv design": "5",
    "price": "6",
    "cost": "6",
    "estimate": "6",
    "rate": "6",
    "kitna": "6",
    "kitne": "6",
    "photo": "7",
    "photos": "7",
    "design": "7",
    "portfolio": "7",
    "contact": "8",
    "number": "8",
    "address": "8",
    "location": "8",
    "visit": "8",
}


def classify_message(text: str) -> str:
    """
    Returns a normalized key:
      '1'–'8'  for menu options
      'greeting' for welcome messages
      'room_size' for size inputs
      'unknown'  for unrecognized input
    """
    cleaned = text.strip().lower()

    # 1. Greeting check
    if cleaned in GREETINGS:
        return "greeting"

    # 2. Room size check
    if parse_room_size(cleaned):
        return "room_size"

    # 3. Direct numeric menu option
    if cleaned in {"1", "2", "3", "4", "5", "6", "7", "8"}:
        return cleaned

    # 4. Keyword matching (longest match first)
    for keyword in sorted(KEYWORD_MAP, key=len, reverse=True):
        if keyword in cleaned:
            return KEYWORD_MAP[keyword]

    # 5. Fallback — treat any first message as a greeting
    return "unknown"


# ── Response Builder ──────────────────────────────────────────────────────────
OPTION_HANDLERS = {
    "1": get_false_ceiling_info,
    "2": get_pvc_ceiling_info,
    "3": get_wpc_panel_info,
    "4": get_partition_wall_info,
    "5": get_tv_unit_info,
    "6": get_estimate_prompt,
    "7": get_design_photos_info,
    "8": get_contact_info,
}


def build_reply(incoming_message: str) -> str:
    """
    Core logic: maps an incoming message to the correct reply string.
    """
    intent = classify_message(incoming_message)
    logger.info("Message: %r → Intent: %s", incoming_message, intent)

    if intent == "greeting":
        return get_welcome_menu()

    if intent == "room_size":
        dims = parse_room_size(incoming_message)
        if dims:
            length, width = dims
            return calculate_estimate(length, width)

    if intent in OPTION_HANDLERS:
        return OPTION_HANDLERS[intent]()

    # Unknown message — send welcome menu
    return ("🙏 Namaste! Aapka swagat hai *JK Interior* mein.\n\n"
            "Kripya niche se option chunein:\n\n" + get_welcome_menu())


# ── Flask Webhook ─────────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio WhatsApp webhook endpoint.
    Twilio sends a POST with 'Body' and 'From' fields.
    """
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "unknown")

    logger.info("Received from %s: %r", sender, incoming_msg)

    reply_text = build_reply(incoming_msg)

    response = MessagingResponse()
    response.message(reply_text)

    logger.info("Replied: %r", reply_text[:80])
    return str(response), 200, {"Content-Type": "text/xml"}


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "bot": BUSINESS_NAME}, 200


# ── Local Test Helper (CLI) ───────────────────────────────────────────────────
def run_cli_test():
    """
    Quick CLI test — run: python jk_interior_whatsapp_bot.py test
    """
    test_cases = [
        "hi",
        "hello",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "12x10",
        "15 x 12",
        "price",
        "false ceiling",
        "pvc",
        "contact",
        "design photos",
        "estimate",
        "kitna lagega",
        "kuch bhi",
    ]

    separator = "=" * 60
    for msg in test_cases:
        print(separator)
        print(f"USER: {msg}")
        print("BOT :")
        print(build_reply(msg))
    print(separator)


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_cli_test()
    else:
        port = int(os.environ.get("PORT", 5000))
        logger.info("Starting %s WhatsApp bot on port %d", BUSINESS_NAME, port)
        app.run(host="0.0.0.0", port=port, debug=False)
    
def get_response(user_input):
    return build_reply(user_input)
