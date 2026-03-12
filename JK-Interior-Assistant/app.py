import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- आपकी मेटा जानकारी (जो आपने दी थी) ---
ACCESS_TOKEN = "EAAMjzXE0bacBQ7zqDNhMhZBV4Jo0EQtA77OvZChZCfdYc7ys5cehZCAZBPsJhym4aGVuOtxbWoZClGnTZCvsKS1SpTNeOoxWroZCasfvIaahwiQcICAML9gbwI1zDe1t9VHZAmFJZA7ga81vgxuqlFSzR8pKHNwgZCyUwg7iPKL0avsoWThXuwwN4qDycEbhl2WO2unxpUA6B2PGnj8UYDcG2B8HsWidc9JKEXeF73GFjMJXH3lkpjOkSeCDEXFcpzJHx1SjjgIOVizwDZBmrg6okXH5"
PHONE_NUMBER_ID = "1071239746066018"
VERIFY_TOKEN = "my_secret_token_123"

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"रिप्लाई स्टेटस: {response.status_code}")
    return response.json()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. वेरिफिकेशन (मेटा के लिए)
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        return 'Forbidden', 403

    # 2. मैसेज रिसीव और ऑटो-रिप्लाई
    if request.method == 'POST':
        data = request.json
        
        # चेक करें कि क्या वाकई में कोई मैसेज आया है (Status Update नहीं)
        try:
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                incoming_msg = data['entry'][0]['changes'][0]['value']['messages'][0]
                user_number = incoming_msg['from']
                
                # ऑटो-रिप्लाई का टेक्स्ट यहाँ बदल सकते हैं
                reply_text = "नमस्ते! JK Interior Assistant में आपका स्वागत है। हमें आपका मैसेज मिल गया है, हम जल्द ही आपसे संपर्क करेंगे।"
                
                # जवाब भेजें
                send_whatsapp_message(user_number, reply_text)
        except:
            pass
            
        return 'EVENT_RECEIVED', 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is running with Auto-Reply!", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
