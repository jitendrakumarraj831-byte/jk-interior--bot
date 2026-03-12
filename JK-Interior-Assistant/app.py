import os
import requests
from flask import Flask, request
from chatbot import get_bot_reply   # chatbot.py से reply function

app = Flask(__name__)

# ----- Meta WhatsApp Credentials -----
ACCESS_TOKEN = "EAAMjzXE0bacBQZCIcbZAJvaNuFVJlEVKMGUCxWA2bKXv314cXgF3ZCpJcIcxGWrZAAnFT0abFAP3Eghwr3MiZCsZChk2cEdVchMynqcR2Rk70d4LuzUf9FSsJS5aWfIa4yZBnWZBtpW6Odso444lxTC1p5Vw6MxvRempY0lz7O4hnWaC0XIGoU1ZATpOcybpgQsdZA3iV7FSXBwiibF1cjZCzcEUI2WeOZCSy6m6qXX57BLN7qyWYIN8pzql2ieHfdLIOCoxlwmiUhEXNeqPgbktvgcD"
PHONE_NUMBER_ID = "1071239746066018"
VERIFY_TOKEN = "my_secret_token_123"


# -------- Send WhatsApp Message --------
def send_whatsapp_message(to, text):

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Send Status:", response.status_code)
    print(response.text)

    return response.json()


# -------- Webhook --------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Meta verification
    if request.method == "GET":

        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403


    # Receive message
    if request.method == "POST":

        data = request.get_json()

        try:
            if "messages" in data["entry"][0]["changes"][0]["value"]:

                message = data["entry"][0]["changes"][0]["value"]["messages"][0]

                sender = message["from"]

                user_text = message["text"]["body"]

                # chatbot.py से reply generate
                reply_text = get_bot_reply(user_text)

                # WhatsApp पर reply भेजें
                send_whatsapp_message(sender, reply_text)

        except Exception as e:
            print("Error:", e)

        return "EVENT_RECEIVED", 200


# -------- Home Route --------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running with Auto-Reply!", 200


# -------- Run Server --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
