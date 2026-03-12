import re

def get_response(user_input):
    user_input = user_input.lower()

    # MENU NUMBER LOGIC
    if user_input == "1":
        return "Gypsum / PVC / Grid False Ceiling ka price ₹80 - ₹120 per sq ft hota hai."

    elif user_input == "2":
        return "PVC Ceiling ka price ₹60 - ₹100 per sq ft hota hai."

    elif user_input == "3":
        return "WPC Wall Panel ka price ₹200 - ₹400 per sq ft hota hai."

    elif user_input == "4":
        return "Partition Wall ka price ₹120 - ₹200 per sq ft hota hai."

    elif user_input == "5":
        return "Hum custom TV Unit design aur install karte hain. Design aur size ke hisaab se price vary karta hai."

    elif user_input == "6":
        return "False Ceiling price ₹80 - ₹120 per sq ft se start hota hai. Exact price room size aur design par depend karta hai."

    elif user_input == "7":
        return "📞 Contact: +918651070831\nOwner: Jitendra Kumar\nLocation: Forbesganj / Araria"

    # TEXT BASED RESPONSES
    responses = {

        r"\b(hi|hello|hey|namaste)\b":
        ("Namaste 🙏\n"
         "Welcome to JK Interior.\n\n"
         "Hum interior aur ceiling design ka kaam karte hain.\n\n"
         "Aap kya kaam karwana chahte hain?\n\n"
         "1️⃣ False Ceiling\n"
         "2️⃣ PVC Ceiling\n"
         "3️⃣ WPC Wall Panel\n"
         "4️⃣ Partition Wall\n"
         "5️⃣ TV Unit Design\n"
         "6️⃣ Price Information\n"
         "7️⃣ Contact / Visit"),

        r"\b(price|rate|cost|kitna|paisa)\b":
        ("JK Interior gypsum false ceiling ka design aur installation karta hai.\n\n"
         "Price ₹80 - ₹120 per sq ft se start hota hai.\n\n"
         "Agar aap room size bhej denge to hum exact estimate bata sakte hain."),

        r"\b(location|address|kahan|where)\b":
        ("Hum Forbesganj aur Araria area me interior work karte hain.\n\n"
         "Site visit bhi available hai."),

        r"\b(contact|number|call|phone|baat)\b":
        ("Aap direct WhatsApp ya call kar sakte hain:\n\n"
         "📞 +918651070831\n"
         "Owner: Jitendra Kumar"),

        r"\b(false ceiling|gypsum)\b":
        ("Gypsum False Ceiling ka price lagbhag ₹80 - ₹120 per sq ft hota hai.\n"
         "Isme hum modern aur attractive designs provide karte hain."),

        r"\b(pvc|pvc ceiling)\b":
        ("PVC Ceiling ka price lagbhag ₹60 - ₹100 per sq ft hota hai.\n"
         "Ye waterproof aur termite-proof hota hai aur isme kaafi colours available hote hain."),

        r"\b(grid ceiling)\b":
        ("Grid Ceiling ka price lagbhag ₹70 - ₹120 per sq ft hota hai.\n"
         "Ye mostly offices aur commercial spaces ke liye best hota hai."),

        r"\b(wpc|louver|fluted panel)\b":
        ("WPC Louvers / Fluted Panels ka price ₹200 - ₹400 per sq ft hota hai.\n"
         "Ye walls ko ek premium wooden finish look deta hai."),

        r"\b(uv marble|marble sheet)\b":
        ("UV Marble Sheet installation ka price ₹150 - ₹300 per sq ft hota hai.\n"
         "Ye real marble jaisa look deta hai aur maintain karna aasan hai."),

        r"\b(partition|partition wall)\b":
        ("Gypsum Board Partition Wall ka price ₹120 - ₹200 per sq ft hota hai.\n"
         "Ye rooms ko divide karne ka ek quick aur neat solution hai."),

        r"\b(tv unit)\b":
        ("Hum custom TV Unit design aur install karte hain.\n"
         "Design aur size ke hisaab se price vary karta hai.\n"
         "Aap apna requirement share karein ya hume call karein."),

        r"\b(artificial grass|grass)\b":
        ("Artificial Grass installation indoor aur outdoor dono jagah ke liye available hai.\n"
         "Aap apne space ka size batayein exact estimate ke liye."),

        r"\b(services|service|kaam)\b":
        ("Hamari main services hain:\n"
         "1. Gypsum False Ceiling\n"
         "2. PVC Ceiling\n"
         "3. Grid Ceiling\n"
         "4. WPC Louvers / Fluted Panels\n"
         "5. UV Marble Sheet Installation\n"
         "6. Gypsum Board Partition Wall\n"
         "7. TV Unit Design & Installation\n"
         "8. Artificial Grass Installation\n"
         "9. PVC Wall Panels Decoration")
    }

    for pattern, response in responses.items():
        if re.search(pattern, user_input):
            return response

    return ("Maaf kijiyega, mujhe ye samajh nahi aaya.\n\n"
            "JK Interior mainly in services me deal karta hai:\n"
            "- False Ceiling (Gypsum/PVC/Grid)\n"
            "- Wall Paneling (WPC/UV Marble/PVC)\n"
            "- Partition Walls & TV Units\n\n"
            "Aap direct humse sampark kar sakte hain:\n"
            "📞 +918651070831 (Jitendra Kumar)")
