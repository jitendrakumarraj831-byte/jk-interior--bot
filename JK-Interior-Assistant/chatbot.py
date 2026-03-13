"""
JK Interior - WhatsApp Auto Reply Bot
Business: JK Interior
Owner: Jitendra Kumar
Phone: +918651070831
Location: Forbesganj / Araria (Bihar)

A production-ready WhatsApp chatbot for interior design business
using Flask and Twilio.
"""

import re
import os
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JKInteriorBot')

app = Flask(__name__)

# ---------------------------------------------------------------------------
# BUSINESS CONSTANTS
# ---------------------------------------------------------------------------

BUSINESS_NAME = "JK Interior"
OWNER_NAME = "Jitendra Kumar"
OWNER_PHONE = "+918651070831"
BUSINESS_LOCATION = "Forbesganj / Araria (Bihar)"
GOOGLE_MAPS_LINK = "https://maps.google.com/?q=Forbesganj+Bihar"
INSTAGRAM = "@jkinterior"
WHATSAPP_LINK = f"https://wa.me/{OWNER_PHONE.replace('+', '')}"

# Price rates (per sq ft in INR)
PRICE_RATES = {
    "false_ceiling": {"min": 65, "max": 95, "unit": "sq ft", "label": "False Ceiling"},
    "pvc_ceiling": {"min": 55, "max": 80, "unit": "sq ft", "label": "PVC Ceiling"},
    "wpc_wall_panel": {"min": 90, "max": 130, "unit": "sq ft", "label": "WPC Wall Panel"},
    "partition_wall": {"min": 70, "max": 110, "unit": "sq ft", "label": "Partition Wall"},
    "tv_unit": {"min": 800, "max": 1500, "unit": "running foot", "label": "TV Unit Design"},
}

# Services list
SERVICES = [
    "False Ceiling",
    "PVC Ceiling",
    "WPC Wall Panel",
    "Partition Wall",
    "TV Unit Design",
    "Interior Design Consultation",
    "Room Design",
    "Wall Decoration",
    "Ceiling Lighting Design",
    "Modern Interior Ideas",
]

# Session state storage (in production use Redis or DB)
user_sessions: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# SESSION MANAGEMENT
# ---------------------------------------------------------------------------

def get_session(phone: str) -> Dict[str, Any]:
    """Get or create user session."""
    if phone not in user_sessions:
        user_sessions[phone] = {
            "state": "new",
            "name": None,
            "room_data": {},
            "site_visit_data": {},
            "last_interaction": datetime.now().isoformat(),
            "message_count": 0,
        }
    user_sessions[phone]["last_interaction"] = datetime.now().isoformat()
    user_sessions[phone]["message_count"] += 1
    return user_sessions[phone]


def update_session(phone: str, key: str, value: Any) -> None:
    """Update a field in user session."""
    if phone not in user_sessions:
        get_session(phone)
    user_sessions[phone][key] = value


def reset_session(phone: str) -> None:
    """Reset user session to new state."""
    if phone in user_sessions:
        user_sessions[phone]["state"] = "menu"
        user_sessions[phone]["room_data"] = {}
        user_sessions[phone]["site_visit_data"] = {}


# ---------------------------------------------------------------------------
# MENU SYSTEM
# ---------------------------------------------------------------------------

def get_welcome_message(name: Optional[str] = None) -> str:
    """Generate the welcome/intro message."""
    greeting = f"Namaste {name}! 🙏" if name else "Namaste! 🙏"
    return f"""{greeting}

*{BUSINESS_NAME}* mein aapka swagat hai! ✨
Interior Design ke Expert — *{OWNER_NAME}*

Aap hum se kya help chahte hain?

━━━━━━━━━━━━━━━━━━━━━
📋 *MAIN MENU*
━━━━━━━━━━━━━━━━━━━━━

*1️⃣* — Hamari Services dekhein
*2️⃣* — Price / Rate puchein
*3️⃣* — Room Size Calculator (Quote)
*4️⃣* — Site Visit Book karein
*5️⃣* — Design Photos dekhein
*6️⃣* — Contact / Location
*7️⃣* — Material Quality Info
*8️⃣* — Installation Time
*9️⃣* — Comparison (PVC vs Gypsum)
*0️⃣* — Seedha Call karein

━━━━━━━━━━━━━━━━━━━━━
Reply karein number ya apna sawaal likhein 👇"""

# MENU SYSTEM

def get_main_menu() -> str:
    """Return the main menu."""
    return """\
📋 *JK INTERIOR - MAIN MENU*

*1* - Hamari Services
*2* - Price List / Rates
*3* - Room Size Calculator
*4* - Site Visit Booking
*5* - Design Photos
*6* - Contact & Location
*7* - Material Quality
*8* - Installation Time
*9* - PVC vs Gypsum Comparison
*0* - Direct Call / WhatsApp

Koi bhi number type karein ya seedha sawaal poochein 👇"""

def calculate_room_price(length: float, width: float) -> str:
    """Calculate price estimates for a given room size."""
    sq_ft = length * width
    # Aapka f-string yahan sahi kiya gaya hai
    return f"""\
*Room Size: {int(length)} x {int(width)} ft = {int(sq_ft)} sq ft*

💰 *Estimated Price:*
_________________________"""

def get_thanks_response() -> str:
    """Thanks ka reply."""
    return """\
Ji, bahut bahut swagat hai aapka! 😊

Kya main aapki kisi aur tarah se madad kar sakta hoon?
Dobara menu dekhne ke liye kuch bhi type karein."""
    
# ---------------------------------------------------------------------------
# PRICE & CALCULATOR
# ---------------------------------------------------------------------------

def calculate_room_price(length: float, width: float) -> str:
    """Calculate price estimates for a given room size."""
    sq_ft = length * width

    lines = [
        f"📐 *Room Size: {int(length)} x {int(width)} ft = {int(sq_ft)} sq ft*",
        "",
        "💰 *Estimated Price:*",
        "━━━━━━━━━━━━━━━━━━━━━",
    ]

    for key, rate in PRICE_RATES.items():
        if rate["unit"] == "sq ft":
            low = int(sq_ft * rate["min"])
            high = int(sq_ft * rate["max"])
            lines.append(
                f"🔹 *{rate['label']}*: ₹{low:,} – ₹{high:,}"
            )

    lines += [
        "━━━━━━━━━━━━━━━━━━━━━",
        "",
        "📝 *TV Unit* ke liye alag se batayein (running foot mein).",
        "",
        "⚠️ _Ye estimate hai. Final price site visit ke baad confirm hogi._",
        "",
        f"📞 Direct baat ke liye: {OWNER_PHONE}",
        "📅 Site visit book karein? Reply karein *VISIT*",
    ]

    return "\n".join(lines)


def get_price_list() -> str:
    """Return the full price list."""
    return f"""\
💰 *JK INTERIOR — PRICE LIST*
━━━━━━━━━━━━━━━━━━━━━

*Per Square Foot Rates:*

🔹 *False Ceiling (Gypsum)*
   ₹65 – ₹95 per sq ft

🔹 *PVC Ceiling*
   ₹55 – ₹80 per sq ft

🔹 *WPC Wall Panel*
   ₹90 – ₹130 per sq ft

🔹 *Partition Wall*
   ₹70 – ₹110 per sq ft

🔹 *TV Unit Design*
   ₹800 – ₹1500 per running foot

━━━━━━━━━━━━━━━━━━━━━

📐 *Room Size Calculator:*
Apne room ka size dein jaise:
`12x10` ya `10 by 12`

Hum automatic estimate nikalenge! ✅

⚠️ _Prices design, material, aur finishing ke hisaab se vary karti hain._
_Final price: site visit ke baad confirm hogi._

📅 Site visit ke liye reply karein: *VISIT*"""


# ---------------------------------------------------------------------------
# SERVICES
# ---------------------------------------------------------------------------

def get_services_menu() -> str:
    """Return the services menu."""
    lines = [
        "🏠 *JK INTERIOR — HAMARI SERVICES*",
        "━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    for i, svc in enumerate(SERVICES, 1):
        lines.append(f"*{i:02d}.* {svc}")

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━━",
        "🔍 Kisi bhi service ke baare mein jaankari ke liye",
        "uska naam likhein ya number type karein.",
        "",
        "Jaise: *False Ceiling* ya *PVC Ceiling price*",
    ]
    return "\n".join(lines)


def get_service_detail(service_key: str) -> str:
    """Return detailed information about a specific service."""
    details = {
        "false_ceiling": f"""\
🏗️ *FALSE CEILING (Gypsum Board)*
━━━━━━━━━━━━━━━━━━━━━

*Kya hai?*
Gypsum board se banaya gaya ek alag ceiling jo original ceiling ke neeche lagaya jaata hai.

*Fayde:*
✅ Heat insulation — kamra thanda rehta hai
✅ Sound proof effect
✅ Sundar design options
✅ Hidden wiring & lighting possible
✅ Long lasting (10-15 saal)
✅ Fire resistant

*Design Options:*
• Simple flat ceiling
• Cove lighting ceiling
• Tray ceiling (stepped)
• Coffered (grid pattern)
• POP texture combinations

*Rate:* ₹65 – ₹95 per sq ft

*Best For:* Living Room, Bedroom, Office

📅 Free site visit ke liye: *VISIT* likhein""",

        "pvc_ceiling": f"""\
🔷 *PVC CEILING*
━━━━━━━━━━━━━━━━━━━━━

*Kya hai?*
PVC (Polyvinyl Chloride) se bani lightweight ceiling panels.

*Fayde:*
✅ Water resistant — bathroom mein bhi use hota hai
✅ Termite proof
✅ Easy to clean (sirf wipe karein)
✅ Low maintenance
✅ Affordable price
✅ Quick installation

*Colors & Designs:*
• Plain white / off-white
• Wood texture look
• Marble effect
• 3D embossed patterns

*Rate:* ₹55 – ₹80 per sq ft

*Best For:* Kitchen, Bathroom, Utility rooms

📅 Site visit: *VISIT* likhein""",

        "wpc_wall_panel": f"""\
🌿 *WPC WALL PANEL*
━━━━━━━━━━━━━━━━━━━━━

*Kya hai?*
WPC = Wood Plastic Composite. Ek modern wall cladding material jo wood jaisa dikhta hai par durability plastic jaisi hai.

*Fayde:*
✅ Water proof
✅ Termite proof
✅ Premium wood look (bina real wood ke)
✅ Long lasting
✅ Easy installation
✅ Low maintenance

*Design Options:*
• Vertical slat panels
• Horizontal cladding
• 3D textured panels
• Mix & match colors

*Rate:* ₹90 – ₹130 per sq ft

*Best For:* Feature walls, TV wall, Bedroom accent wall

📅 Site visit: *VISIT* likhein""",

        "partition_wall": f"""\
🚪 *PARTITION WALL*
━━━━━━━━━━━━━━━━━━━━━

*Kya hai?*
Ek room ko alag sections mein divide karne ke liye banaya jaata hai. Privacy aur aesthetics dono ka faida.

*Types:*
• Gypsum partition
• Glass + aluminum partition
• WPC + Glass combination
• Designer jali partition

*Fayde:*
✅ Space efficiently utilize hota hai
✅ Privacy milti hai
✅ Modern look
✅ Soundproofing option available

*Rate:* ₹70 – ₹110 per sq ft

*Best For:* Office, Study room, Bedroom divider

📅 Site visit: *VISIT* likhein""",

        "tv_unit": f"""\
📺 *TV UNIT DESIGN*
━━━━━━━━━━━━━━━━━━━━━

*Kya hai?*
Custom designed TV unit jo aapke living room ka centerpiece ban jaaye.

*Styles:*
• Modern floating TV unit
• Wall mounted with shelves
• Full wall entertainment unit
• LED backlit design
• Floor to ceiling unit

*Materials Used:*
• Ply + Laminate
• MDF + PU paint
• WPC + Glass
• Combination designs

*Rate:* ₹800 – ₹1500 per running foot

*Example:*
6 ft TV unit → ₹4,800 – ₹9,000

*Best For:* Living Room, Bedroom

📅 Design consultation: *VISIT* likhein""",

        "interior_consultation": f"""\
🎨 *INTERIOR DESIGN CONSULTATION*
━━━━━━━━━━━━━━━━━━━━━

*Hum kya karte hain:*
✅ Aapke ghar / office ka site visit
✅ Space planning aur layout design
✅ Color scheme selection
✅ Material aur finish recommendation
✅ 3D visualization (select projects)
✅ Budget planning

*Process:*
1️⃣ WhatsApp pe initial discussion
2️⃣ Site visit (free of charge)
3️⃣ Design proposal
4️⃣ Material selection
5️⃣ Work begin

*Consultation:* FREE (site visit ke saath)

📞 {OWNER_PHONE}

📅 Book karein: *VISIT* likhein""",

        "room_design": f"""\
🛋️ *ROOM DESIGN*
━━━━━━━━━━━━━━━━━━━━━

*Kaunse rooms design karte hain:*
🏠 Living Room
🛏️ Bedroom (Master + Kids)
🍳 Kitchen (Modular)
🛁 Bathroom
📚 Study Room
💼 Office / Cabin
🎉 Pooja Room

*Kya include hota hai:*
✅ Ceiling design
✅ Wall treatment
✅ Flooring recommendation
✅ Lighting design
✅ Furniture suggestion
✅ Color palette

*Start kaise karein:*
Apne room ka photo + size WhatsApp karein!

📅 Site visit: *VISIT* likhein""",

        "wall_decoration": f"""\
🎨 *WALL DECORATION*
━━━━━━━━━━━━━━━━━━━━━

*Wall decoration ke types:*

🔹 *Wallpaper / Wall Covering*
   Designer prints, textures, 3D wallpaper

🔹 *Texture Paint*
   Sand finish, sponge, metallic effects

🔹 *Accent Wall*
   WPC panel feature wall, stone cladding

🔹 *Stencil Design*
   Custom patterns, geometric designs

🔹 *Wall Mural*
   Custom artwork, nature themes

🔹 *PU Glossy Wall*
   High shine premium finish

*Rate varies* by design and area.

📸 Design photos ke liye likhein: *PHOTOS*
📅 Consultation: *VISIT* likhein""",

        "ceiling_lighting": f"""\
💡 *CEILING LIGHTING DESIGN*
━━━━━━━━━━━━━━━━━━━━━

*Lighting Types:*

🔦 *Cove Lighting*
   Ceiling ke andar LED strip — soft glow effect

🔦 *Recessed / Spot Lights*
   False ceiling mein hidden downlights

🔦 *Pendant Lights*
   Hanging decorative lights — dining, study

🔦 *Chandelier*
   Grand centerpiece for living room / hall

🔦 *LED Strip Lighting*
   Under cabinets, shelves, TV unit backlight

🔦 *Smart Lighting*
   Dimmer control, color changing, app control

*Included with Ceiling Work:*
✅ Light placement planning FREE

*Rate:*
Lighting work alag se quote hota hai.

📅 Site visit + lighting plan: *VISIT* likhein""",

        "modern_ideas": f"""\
✨ *MODERN INTERIOR IDEAS*
━━━━━━━━━━━━━━━━━━━━━

*2024-25 Ke Top Trends:*

🏆 *Japandi Style*
   Japanese + Scandinavian mix — minimal, calm

🏆 *Biophilic Design*
   Plants, natural materials, earthy tones

🏆 *Curved Furniture*
   Soft rounded edges, organic shapes

🏆 *Fluted / Reeded Panels*
   Vertical groove panels — modern classic

🏆 *Terrazzo Flooring*
   Spotted pattern — kitchen, bathroom

🏆 *Bold Color Accents*
   Deep green, navy, terracotta feature walls

🏆 *Smart Home Integration*
   Automated lighting, curtains, AC control

📸 Inspiration photos: *PHOTOS* likhein
📅 Consultation: *VISIT* likhein
📞 Call: {OWNER_PHONE}""",
    }

    return details.get(service_key, "")


# ---------------------------------------------------------------------------
# COMPARISON RESPONSES
# ---------------------------------------------------------------------------

def get_pvc_vs_gypsum_comparison() -> str:
    """Return PVC vs Gypsum ceiling comparison."""
    return """\
⚖️ *PVC CEILING vs GYPSUM / FALSE CEILING*
━━━━━━━━━━━━━━━━━━━━━

| Feature | PVC | Gypsum (False) |
|---------|-----|----------------|
| 💰 Cost | ₹55–80/sqft | ₹65–95/sqft |
| 💧 Water Resistant | ✅ Yes | ❌ No |
| 🌡️ Heat Insulation | Medium | Excellent |
| 🔊 Sound Proof | Low | High |
| 🎨 Design Options | Limited | Many |
| 🔧 Installation | Fast | Medium |
| 🧹 Maintenance | Very Low | Low |
| ⏳ Lifespan | 8–10 years | 10–15 years |

━━━━━━━━━━━━━━━━━━━━━

✅ *PVC Choose karein agar:*
• Bathroom, Kitchen area mein chahiye
• Budget tight ho
• Low maintenance chahiye
• Nami wala area ho

✅ *Gypsum/False Ceiling Choose karein agar:*
• Living room / bedroom ke liye
• Premium look chahiye
• Cove lighting ka plan ho
• Sound proof room chahiye

💡 *Expert Recommendation:*
_Living room → Gypsum False Ceiling_
_Kitchen/Bathroom → PVC Ceiling_
_Bedroom → Gypsum ya combination_

📅 Free consultation: *VISIT* likhein
📞 Call: +918651070831"""


def get_material_quality_info() -> str:
    """Return material quality information."""
    return """\
🔬 *MATERIAL QUALITY — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

Hum sirf *branded aur tested materials* use karte hain:

🏗️ *Gypsum Board*
• Brand: Saint-Gobain / Gyproc / USG
• 12mm standard, 15mm moisture resistant
• ISI certified
• Fire rating: Class A

🔷 *PVC Panels*
• Premium imported PVC
• Termite + moisture proof
• UV resistant coating
• Thickness: 8mm standard

🌿 *WPC Panels*
• Interior grade WPC
• Zero formaldehyde
• Water + termite proof
• Texture: wood realistic

🪵 *Ply & MDF*
• BWR grade marine ply
• MDF: E0/E1 emission grade
• Interior grade laminate (Merino/Century/Greenlam)

🔩 *Framework*
• GI (Galvanized Iron) channels
• 0.5mm thickness minimum
• Rust resistant galvanized finish

━━━━━━━━━━━━━━━━━━━━━
✅ *5 Year Work Warranty*
✅ Genuine material guarantee
✅ All work supervised personally by {owner}

📅 Site visit book: *VISIT* likhein
📞 Call: +918651070831""".format(owner=OWNER_NAME)


def get_installation_time_info() -> str:
    """Return installation time information."""
    return """\
⏱️ *INSTALLATION TIME — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

*Kitne din lagenge? (Approx)*

🔹 *False Ceiling (1 room)*
   → 2–3 din

🔹 *PVC Ceiling (1 room)*
   → 1–2 din

🔹 *WPC Wall Panel*
   → 1–3 din (area ke hisaab se)

🔹 *Partition Wall*
   → 2–4 din

🔹 *TV Unit*
   → 3–5 din

🔹 *Full Room Interior*
   → 7–15 din

🔹 *Full Home Interior (2BHK)*
   → 20–35 din

━━━━━━━━━━━━━━━━━━━━━

⚠️ *Time factors:*
• Room size
• Design complexity
• Material availability
• Finishing requirements

✅ *Hum daily progress update dete hain*
✅ *Site pe senior carpenter always present*
✅ *Clean work — dust minimized*

📅 Start date fix: *VISIT* likhein
📞 Direct: +918651070831"""


# ---------------------------------------------------------------------------
# CONTACT, LOCATION, SITE VISIT
# ---------------------------------------------------------------------------

def get_contact_info() -> str:
    """Return contact information."""
    return f"""\
📞 *CONTACT — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

👤 *Owner:* {OWNER_NAME}
📱 *Mobile / WhatsApp:* {OWNER_PHONE}
🏢 *Business:* {BUSINESS_NAME}

📍 *Location:* {BUSINESS_LOCATION}

⏰ *Timing:*
Somvar – Shanivaar: 8:00 AM – 8:00 PM
Ravivar: 10:00 AM – 5:00 PM

━━━━━━━━━━━━━━━━━━━━━

📱 *WhatsApp pe Message:*
{WHATSAPP_LINK}

🗺️ *Google Maps:*
{GOOGLE_MAPS_LINK}

━━━━━━━━━━━━━━━━━━━━━
📅 Site visit book karein: *VISIT* likhein"""


def get_location_info() -> str:
    """Return location details."""
    return f"""\
📍 *LOCATION — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

🏢 *{BUSINESS_NAME}*
📌 {BUSINESS_LOCATION}

*Kaam karte hain:*
✅ Forbesganj
✅ Araria
✅ Jogbani
✅ Kishanganj
✅ Purnia (selected projects)
✅ Katihar (selected projects)

━━━━━━━━━━━━━━━━━━━━━

🗺️ Google Maps:
{GOOGLE_MAPS_LINK}

📞 Direction ke liye call karein:
{OWNER_PHONE}

━━━━━━━━━━━━━━━━━━━━━
📅 Free site visit: *VISIT* likhein"""


def get_site_visit_form() -> str:
    """Return site visit booking prompt."""
    return """\
📅 *SITE VISIT BOOKING — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

Hamare expert aapke ghar aakar FREE mein:
✅ Measurement lenge
✅ Design suggestions denge
✅ Material explain karenge
✅ Accurate quote denge

*No Obligation — Bilkul FREE!*

━━━━━━━━━━━━━━━━━━━━━

Kripya neeche ki jaankari dijiye:

*1.* Aapka naam kya hai?
Reply karein apna naam 👇"""


def get_design_photos_response() -> str:
    """Return design photos information."""
    return f"""\
📸 *DESIGN PHOTOS — JK INTERIOR*
━━━━━━━━━━━━━━━━━━━━━

Hamare completed projects ki photos dekhne ke liye:

📱 *WhatsApp pe request karein:*
{OWNER_PHONE}

📌 *Instagram:*
{INSTAGRAM}

💬 *Directly hamare WhatsApp pe message karein:*
{WHATSAPP_LINK}

━━━━━━━━━━━━━━━━━━━━━

*Available Photo Categories:*
🔹 False Ceiling designs
🔹 PVC Ceiling work
🔹 WPC Wall Panel projects
🔹 TV Unit designs
🔹 Full room makeovers
🔹 Partition wall work
🔹 Ceiling lighting effects
🔹 Wall decoration

━━━━━━━━━━━━━━━━━━━━━
📅 Design discuss karein: *VISIT* likhein
📞 Call: {OWNER_PHONE}"""


def get_direct_call_info() -> str:
    """Return direct call option."""
    return f"""\
📞 *DIRECT CALL / WHATSAPP*
━━━━━━━━━━━━━━━━━━━━━

*{BUSINESS_NAME}*
👤 {OWNER_NAME}

📱 *Mobile:* {OWNER_PHONE}

*Timing:*
⏰ 8:00 AM – 8:00 PM (Mon–Sat)
⏰ 10:00 AM – 5:00 PM (Sun)

━━━━━━━━━━━━━━━━━━━━━

📲 *WhatsApp pe click karein:*
{WHATSAPP_LINK}

━━━━━━━━━━━━━━━━━━━━━
Hum aapki call ka wait kar rahe hain! 😊"""


# ---------------------------------------------------------------------------
# KEYWORD DETECTION ENGINE
# ---------------------------------------------------------------------------

class KeywordDetector:
    """Advanced keyword detection for Hindi + English messages."""

    # Room size patterns: 12x10, 12*10, 12 x 10, 12 by 10, 12X10
    ROOM_SIZE_PATTERNS = [
        r'(\d+(?:\.\d+)?)\s*[xX×*]\s*(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*by\s*(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*se\s*(\d+(?:\.\d+)?)',
    ]

    KEYWORDS = {
        # Main menu triggers
        "menu": [
            "menu", "start", "hello", "hi", "hii", "hey", "namaste", "namaskar",
            "help", "main menu", "home", "shuru", "back", "wapas", "restart",
            "options", "choices", "kya karte ho", "kaisa hai"
        ],
        # Service keywords (digits handled separately in Phase 4b)
        "services": [
            "service", "services", "kaam", "kya kaam", "kya karte", "work",
            "aap kya karte", "interior", "interior work",
        ],
        "price": [
            "price", "cost", "rate", "rates", "kitna", "kitne paise", "amount",
            "charges", "fees", "paisa", "rupee", "rupees", "₹", "budget",
            "quote", "estimate", "kitna lagega", "kharcha", "pricing",
            "paise", "lagat", "kharch"
        ],
        "calculator": [
            "calculator", "calculate", "room size", "room ka size",
            "calculate karo", "sqft", "sq ft", "square", "area", "kamra",
            "size estimate", "size price", "measure", "measurement"
        ],
        "site_visit": [
            "site visit", "visit", "ghar aao", "ghar aaoge", "ghar dekhna",
            "aake dekho", "free visit", "site pe aao", "booking",
            "book", "appointment", "milna", "visit book", "site inspection",
            "ghar dekhne", "ghar aayenge", "ghar aana"
        ],
        "photos": [
            "photo", "photos", "design photo", "pics", "pictures", "image",
            "images", "dikhaiye", "dikhao", "show", "gallery",
            "portfolio", "samples", "sample", "work photo",
            "kaam ka photo", "previous work"
        ],
        "contact": [
            "contact", "number", "phone", "call number", "contact number",
            "mobile", "reach", "connect", "touch", "whatsapp number",
            "contact karo", "phone number", "mob number"
        ],
        "material": [
            "material", "quality", "kaunsa material", "best material",
            "kya use karte", "brand", "which material", "material quality",
            "konsa material", "materials", "specification", "specs", "kitna mazbut",
            "durable", "long lasting", "teekha", "pakka"
        ],
        "installation_time": [
            "kitne din", "days", "how long", "duration", "kitna time",
            "kab tak", "schedule", "kab hoga", "din lagenge",
            "install time", "completion time", "finish kab", "when complete",
            "kaafi din", "jaldi", "fast", "time lagega", "time lage",
            "kab complete", "kab taiyar"
        ],
        "comparison": [
            "comparison", "compare", "vs", "versus", "better", "best",
            "difference", "fark", "better hai", "konsa better", "pvc vs",
            "gypsum vs", "which better", "konsa accha", "kaun sa best",
            "pvc ceiling vs", "false ceiling vs", "pvc better", "gypsum better",
            "which ceiling", "ceiling comparison", "konsa ceiling"
        ],
        "direct_call": [
            "direct call", "talk", "baat karna", "seedha baat",
            "phone karo", "call karo", "owner", "jitendra", "contact owner"
        ],
        # Service-specific
        "false_ceiling": [
            "false ceiling", "gypsum ceiling", "gypsum", "false", "pop ceiling",
            "pop", "plaster of paris", "designer ceiling"
        ],
        "pvc_ceiling": [
            "pvc ceiling", "pvc", "plastic ceiling", "pvc panel ceiling"
        ],
        "wpc": [
            "wpc", "wpc panel", "wall panel", "wpc wall", "wood panel",
            "wooden panel", "wood plastic", "wall cladding"
        ],
        "partition": [
            "partition", "partition wall", "divider", "wall divide", "room divider",
            "cabin", "separate room"
        ],
        "tv_unit": [
            "tv unit", "tv", "television unit", "tv wall", "entertainment unit",
            "tv stand", "lcd unit", "tv cabinet", "tv panel"
        ],
        "interior_consultation": [
            "consultation", "consult", "advice", "suggest", "recommendation",
            "interior advice", "design advice", "planning"
        ],
        "room_design": [
            "room design", "bedroom design", "living room", "hall design",
            "kitchen design", "bathroom design", "study room", "room makeover",
            "complete room", "full room", "pooja room"
        ],
        "wall_decoration": [
            "wall decoration", "wall design", "wall decor", "diwar", "diwar design",
            "diwar decoration", "wallpaper", "texture paint", "paint", "wall treatment",
            "feature wall", "accent wall"
        ],
        "ceiling_lighting": [
            "lighting", "light", "led", "cove light", "cove lighting", "downlight",
            "chandelier", "pendant", "ceiling light", "hidden light", "light design"
        ],
        "modern_ideas": [
            "modern", "latest", "new design", "trending", "2024", "2025",
            "trend", "contemporary", "ideas", "inspiration", "latest design",
            "naya design", "modern interior"
        ],
        "location": [
            "location", "address", "kahan", "kaha", "where", "aap kahan",
            "aap kaha hai", "office", "shop", "where are you", "kahan hai",
            "bihar", "forbesganj", "araria", "city", "area"
        ],
        "greetings": [
            "good morning", "good afternoon", "good evening", "good night",
            "subah", "dopahar", "shaam", "raat", "jai hind", "jai bharat"
        ],
        # Price-related specific
        "false_ceiling_price": [
            "false ceiling price", "false ceiling cost", "false ceiling rate",
            "gypsum price", "gypsum cost", "pop ceiling price", "false ceiling kitna"
        ],
        "pvc_ceiling_price": [
            "pvc price", "pvc cost", "pvc rate", "pvc ceiling price",
            "pvc ceiling cost", "pvc kitna", "pvc kitne"
        ],
        "wpc_price": [
            "wpc price", "wpc cost", "wpc rate", "wall panel price",
            "wpc panel price", "wpc kitna"
        ],
        # Affirmation / Site visit confirmations
        "yes_confirm": [
            "yes", "ha", "haan", "haa", "ji", "ji haan", "bilkul", "zaroor",
            "ok", "okay", "theek hai", "sahi hai", "agree", "confirm", "sure"
        ],
        "no_cancel": [
            "no", "nahi", "na", "naa", "band karo", "cancel", "not now",
            "baad mein", "later", "abhi nahi", "skip"
        ],
    }

    @classmethod
    def detect(cls, message: str) -> str:
        """
        Detect intent from user message.
        Returns the matched intent key or 'unknown'.
        """
        msg = message.lower().strip()

        # Check for room size first (highest priority)
        for pattern in cls.ROOM_SIZE_PATTERNS:
            if re.search(pattern, msg, re.IGNORECASE):
                return "room_size"

        # ----------------------------------------------------------------
        # Phase 1: Price-specific compound queries (must check BEFORE generic)
        # ----------------------------------------------------------------
        price_indicators = ["price", "cost", "rate", "kitna", "paise", "lagega", "charges"]
        has_price_word = any(p in msg for p in price_indicators)

        if has_price_word:
            if "false ceiling" in msg or "gypsum ceiling" in msg:
                return "false_ceiling_price"
            if "pvc ceiling" in msg or "pvc panel" in msg:
                return "pvc_ceiling_price"
            if "wpc" in msg or "wall panel" in msg:
                return "wpc_price"

        # ----------------------------------------------------------------
        # Phase 2: Comparison queries
        # ----------------------------------------------------------------
        comparison_phrases = [
            "vs", "versus", "compare", "better", "konsa better", "konsa accha",
            "which better", "which ceiling", "ceiling comparison", "fark kya",
            "difference between", "pvc vs", "gypsum vs", "kaun sa best"
        ]
        if any(p in msg for p in comparison_phrases):
            return "comparison"

        # ----------------------------------------------------------------
        # Phase 3: Specific service names (exact compound match)
        # ----------------------------------------------------------------
        if "false ceiling" in msg or "gypsum ceiling" in msg or "pop ceiling" in msg:
            return "false_ceiling"
        if "pvc ceiling" in msg:
            return "pvc_ceiling"
        if "wpc" in msg and ("wall" in msg or "panel" in msg):
            return "wpc"
        if "wpc" in msg:
            return "wpc"

        # ----------------------------------------------------------------
        # Phase 4: Location — specific check before services
        # ----------------------------------------------------------------
        location_indicators = ["kahan", "kaha", "where", "location", "address",
                               "forbesganj", "araria", "kahan hai", "kahan kaam",
                               "aap kahan", "aap kaha"]
        if any(p in msg for p in location_indicators):
            return "location"

        # ----------------------------------------------------------------
        # Phase 4b: Numeric single-digit menu selection
        # ----------------------------------------------------------------
        stripped = msg.strip()
        digit_map = {
            "1": "services",
            "2": "price",
            "3": "calculator",
            "4": "site_visit",
            "5": "photos",
            "6": "contact",
            "7": "material",
            "8": "installation_time",
            "9": "comparison",
            "0": "direct_call",
        }
        if stripped in digit_map:
            return digit_map[stripped]

        # ----------------------------------------------------------------
        # Phase 5: Standard keyword matching (ordered by specificity)
        # ----------------------------------------------------------------
        # Process in a fixed priority order
        priority_order = [
            "menu", "greetings", "site_visit", "photos", "contact",
            "material", "installation_time", "direct_call",
            "tv_unit", "partition", "interior_consultation",
            "room_design", "wall_decoration", "ceiling_lighting", "modern_ideas",
            "false_ceiling", "pvc_ceiling", "wpc",
            "services", "price", "calculator",
            "yes_confirm", "no_cancel",
            "false_ceiling_price", "pvc_ceiling_price", "wpc_price",
        ]

        for intent in priority_order:
            keywords = cls.KEYWORDS.get(intent, [])
            for kw in keywords:
                if kw.lower() in msg:
                    return intent

        return "unknown"

    @classmethod
    def extract_room_size(cls, message: str) -> Optional[Tuple[float, float]]:
        """
        Extract room dimensions from message.
        Returns (length, width) or None.
        """
        msg = message.strip()
        for pattern in cls.ROOM_SIZE_PATTERNS:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                try:
                    l = float(match.group(1))
                    w = float(match.group(2))
                    # Validate reasonable room sizes (2ft to 100ft)
                    if 2 <= l <= 100 and 2 <= w <= 100:
                        return (l, w)
                except (ValueError, IndexError):
                    pass
        return None


# ---------------------------------------------------------------------------
# RESPONSE BUILDER
# ---------------------------------------------------------------------------

class ResponseBuilder:
    """Build appropriate responses based on intent and session state."""

    @staticmethod
    def handle_site_visit_flow(phone: str, message: str, session: Dict) -> str:
        """Handle multi-step site visit booking flow."""
        state = session.get("state", "")
        sv_data = session.get("site_visit_data", {})

        if state == "sv_name":
            sv_data["name"] = message.strip().title()
            update_session(phone, "site_visit_data", sv_data)
            update_session(phone, "state", "sv_address")
            return f"""\
✅ Shukriya, *{sv_data['name']}*! 😊

📍 *Apna address / location dijiye:*
(Ghar ka pata, mohalla, ya landmark)

Reply karein 👇"""

        elif state == "sv_address":
            sv_data["address"] = message.strip()
            update_session(phone, "site_visit_data", sv_data)
            update_session(phone, "state", "sv_date")
            return """\
✅ Address note kar liya!

📅 *Kaunsa din aapko suit karega?*

Reply mein likhein:
• Date (jaise: 15 March, kal, parso)
• Ya koi bhi preferred day

👇"""

        elif state == "sv_date":
            sv_data["preferred_date"] = message.strip()
            update_session(phone, "site_visit_data", sv_data)
            update_session(phone, "state", "sv_work_type")
            return """\
✅ Date noted!

🏗️ *Konsa kaam karwana chahte hain?*

Jaise:
• False Ceiling
• PVC Ceiling
• TV Unit
• Full Room Interior
• Ya kuch aur

Reply karein 👇"""

        elif state == "sv_work_type":
            sv_data["work_type"] = message.strip()
            update_session(phone, "site_visit_data", sv_data)
            update_session(phone, "state", "sv_complete")

            # Build confirmation message
            name = sv_data.get("name", "aap")
            address = sv_data.get("address", "-")
            date = sv_data.get("preferred_date", "-")
            work = sv_data.get("work_type", "-")

            confirm = f"""\
🎉 *SITE VISIT BOOKING CONFIRMED!*
━━━━━━━━━━━━━━━━━━━━━

✅ *Name:* {name}
📍 *Address:* {address}
📅 *Preferred Date:* {date}
🏗️ *Work Required:* {work}

━━━━━━━━━━━━━━━━━━━━━

Hum aapko jald confirm karenge! ⏰

📞 *{OWNER_NAME}* personally aapko call karenge:
{OWNER_PHONE}

━━━━━━━━━━━━━━━━━━━━━
*JK Interior* — Quality ka vaada! 🏆

_Kuch aur sawaal?_ Main menu ke liye likhein: *MENU*"""

            # Reset state after booking
            update_session(phone, "state", "menu")
            return confirm

        return ""

    @staticmethod
    def build(phone: str, message: str) -> str:
        """Main response builder — routes to appropriate handler."""
        session = get_session(phone)
        msg_lower = message.lower().strip()

        # Handle ongoing site visit flow first
        if session.get("state", "").startswith("sv_"):
            # Allow cancel during flow
            intent = KeywordDetector.detect(message)
            if intent == "no_cancel":
                update_session(phone, "state", "menu")
                return "❌ Site visit cancel kar diya.\n\n" + get_main_menu()
            return ResponseBuilder.handle_site_visit_flow(phone, message, session)

        # Detect intent
        intent = KeywordDetector.detect(message)

        # Handle room size detection (highest priority after flow states)
        if intent == "room_size":
            dims = KeywordDetector.extract_room_size(message)
            if dims:
                return calculate_room_price(dims[0], dims[1])

        # Route based on intent
        handlers = {
            "menu": lambda: get_main_menu(),
            "greetings": lambda: get_main_menu(),
            "services": lambda: get_services_menu(),
            "price": lambda: get_price_list(),
            "calculator": lambda: _room_size_prompt(),
            "site_visit": lambda: _start_site_visit(phone),
            "photos": lambda: get_design_photos_response(),
            "contact": lambda: get_contact_info(),
            "material": lambda: get_material_quality_info(),
            "installation_time": lambda: get_installation_time_info(),
            "comparison": lambda: get_pvc_vs_gypsum_comparison(),
            "direct_call": lambda: get_direct_call_info(),
            "location": lambda: get_location_info(),
            # Specific services
            "false_ceiling": lambda: get_service_detail("false_ceiling"),
            "false_ceiling_price": lambda: _single_service_price("false_ceiling"),
            "pvc_ceiling": lambda: get_service_detail("pvc_ceiling"),
            "pvc_ceiling_price": lambda: _single_service_price("pvc_ceiling"),
            "wpc": lambda: get_service_detail("wpc_wall_panel"),
            "wpc_price": lambda: _single_service_price("wpc_wall_panel"),
            "partition": lambda: get_service_detail("partition_wall"),
            "tv_unit": lambda: get_service_detail("tv_unit"),
            "interior_consultation": lambda: get_service_detail("interior_consultation"),
            "room_design": lambda: get_service_detail("room_design"),
            "wall_decoration": lambda: get_service_detail("wall_decoration"),
            "ceiling_lighting": lambda: get_service_detail("ceiling_lighting"),
            "modern_ideas": lambda: get_service_detail("modern_ideas"),
            # Yes/No for menu numbers
            "yes_confirm": lambda: get_main_menu(),
            "no_cancel": lambda: get_main_menu(),
        }

        handler = handlers.get(intent)
        if handler:
            return handler()

        # Handle numeric menu selection
        if msg_lower in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            menu_map = {
                "1": get_services_menu,
                "2": get_price_list,
                "3": _room_size_prompt,
                "4": lambda: _start_site_visit(phone),
                "5": get_design_photos_response,
                "6": get_contact_info,
                "7": get_material_quality_info,
                "8": get_installation_time_info,
                "9": get_pvc_vs_gypsum_comparison,
                "0": get_direct_call_info,
            }
            fn = menu_map.get(msg_lower)
            if fn:
                return fn()

        # Unknown message — smart fallback
        return _smart_fallback(message)


def _room_size_prompt() -> str:
    """Prompt user to enter room size."""
    return """\
📐 *ROOM SIZE CALCULATOR*
━━━━━━━━━━━━━━━━━━━━━

Apne room ka size dijiye:

*Format examples:*
• 12x10
• 10x12
• 15*12
• 10 by 15
• 12 se 10

Bas size type karein aur hum estimate nikalenge! ✅

━━━━━━━━━━━━━━━━━━━━━
👇 Room size yahan type karein:"""


def _start_site_visit(phone: str) -> str:
    """Start the site visit booking flow."""
    update_session(phone, "state", "sv_name")
    update_session(phone, "site_visit_data", {})
    return get_site_visit_form()


def _single_service_price(service_key: str) -> str:
    """Return price information for a single service."""
    rate = PRICE_RATES.get(service_key)
    if not rate:
        return get_price_list()

    prompt = f"""\
💰 *{rate['label'].upper()} — PRICE*
━━━━━━━━━━━━━━━━━━━━━

*Rate:* ₹{rate['min']} – ₹{rate['max']} per {rate['unit']}

*Example:*"""

    if rate["unit"] == "sq ft":
        examples = [(100, "10x10"), (120, "12x10"), (150, "15x10")]
        for sqft, size in examples:
            low = sqft * rate["min"]
            high = sqft * rate["max"]
            prompt += f"\n• {size} ft room ({sqft} sqft) → ₹{low:,} – ₹{high:,}"
    else:
        prompt += f"\n• 6 ft unit → ₹{6*rate['min']:,} – ₹{6*rate['max']:,}"
        prompt += f"\n• 8 ft unit → ₹{8*rate['min']:,} – ₹{8*rate['max']:,}"

    prompt += f"""

━━━━━━━━━━━━━━━━━━━━━
📐 Apne room ka size dijiye exact estimate ke liye.
Jaise: *12x10* ya *15 by 12*

⚠️ _Final price site visit ke baad confirm hogi._
📅 Free site visit: *VISIT* likhein"""

    return prompt


def _smart_fallback(message: str) -> str:
    """Smart fallback for unrecognized messages."""
    msg = message.lower()

    # Check if it might be a partial/typo keyword
    suggestions = []

    if any(c.isdigit() for c in msg):
        suggestions.append("Room size ke liye likhein jaise: *12x10*")

    if len(message.strip()) < 3:
        suggestions.append("Kripya apna sawaal thoda detail mein likhein")

    fallback = f"""\
🤔 *Mujhe samajh nahi aaya...*

Aapne likha: _{message}_

━━━━━━━━━━━━━━━━━━━━━

*Aap pooch sakte hain:*
• Price / rate
• False ceiling / PVC ceiling
• Room size (jaise: 12x10)
• Site visit
• Photos
• Contact
• Location

Ya phir *MENU* likhein main menu ke liye 👇

━━━━━━━━━━━━━━━━━━━━━
📞 Direct: {OWNER_PHONE}"""

    return fallback


# ---------------------------------------------------------------------------
# TWILIO WEBHOOK
# ---------------------------------------------------------------------------

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages via Twilio."""
    try:
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '')
        profile_name = request.values.get('ProfileName', '')

        logger.info(f"Message from {sender} ({profile_name}): {incoming_msg}")

        # Get or init session
        session = get_session(sender)

        # First-time welcome
        if session.get("message_count", 0) == 1:
            response_text = get_welcome_message(profile_name if profile_name else None)
        else:
            response_text = ResponseBuilder.build(sender, incoming_msg)

        logger.info(f"Response to {sender}: {response_text[:100]}...")

        resp = MessagingResponse()
        msg = resp.message()
        msg.body(response_text)

        return Response(str(resp), content_type='application/xml')

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        resp = MessagingResponse()
        resp.message("Sorry, kuch technical issue hua. Kripya dobaara try karein ya call karein: +918651070831")
        return Response(str(resp), content_type='application/xml')


@app.route('/webhook/whatsapp/status', methods=['POST'])
def whatsapp_status():
    """Handle Twilio message status callbacks."""
    message_sid = request.values.get('MessageSid', '')
    message_status = request.values.get('MessageStatus', '')
    logger.info(f"Message {message_sid} status: {message_status}")
    return Response('', status=204)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'bot': BUSINESS_NAME, 'version': '1.0.0'}, 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with bot info."""
    return {
        'bot': f'{BUSINESS_NAME} WhatsApp Bot',
        'owner': OWNER_NAME,
        'status': 'running',
        'endpoints': {
            'whatsapp_webhook': '/webhook/whatsapp',
            'status_callback': '/webhook/whatsapp/status',
            'health': '/health',
        }
    }, 200


# ---------------------------------------------------------------------------
# COMMAND LINE TESTING
# ---------------------------------------------------------------------------

def run_cli_demo():
    """Run an interactive CLI demo of the chatbot."""
    print("\n" + "="*60)
    print(f"  {BUSINESS_NAME} — WhatsApp Chatbot CLI Demo")
    print(f"  Owner: {OWNER_NAME}")
    print(f"  Location: {BUSINESS_LOCATION}")
    print("="*60)
    print("\nType your message (type 'quit' to exit)\n")

    test_phone = "whatsapp:+919999999999"

    # Welcome message
    session = get_session(test_phone)
    print(f"BOT:\n{get_welcome_message()}\n")
    print("-"*60)

    while True:
        try:
            user_input = input("YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ('quit', 'exit', 'bye'):
            print("BOT: Dhanyawad! JK Interior ko choose karne ke liye shukriya 🙏")
            break

        if not user_input:
            continue

        response = ResponseBuilder.build(test_phone, user_input)
        print(f"\nBOT:\n{response}\n")
        print("-"*60)
        

# ---------------------------------------------------------
# Bridge function for app.py
# ---------------------------------------------------------

def get_response(user_input):
    """
    This function is used by app.py
    It forwards the message to the existing ResponseBuilder system
    """
    test_phone = "whatsapp:+918651070831"
    return ResponseBuilder.build(test_phone, user_input)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    import sys

    if '--cli' in sys.argv or (len(sys.argv) > 1 and sys.argv[1] == 'cli'):
        run_cli_demo()
    else:
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'

        print(f"\n🏠 {BUSINESS_NAME} WhatsApp Bot starting...")
        print(f"🚀 Running on port {port}")
        print(f"🔗 Webhook URL: https://your-domain.com/webhook/whatsapp\n")

        app.run(host='0.0.0.0', port=port, debug=debug)
    
