import os
import requests
from flask import Flask, request
from chatbot import get_response

app = Flask(__name__)

# Environment variables
ACCESS_TOKEN = os.environ.get("EAAMjzXE0bacBQzOZCozZB4CVIjTFt9n1g67vZBrvBpPzer4DHRoZCd672S1EIBCJdwXasuELGe70XveN6UAQx0hBzYWzwLiLQ18cpYXkKRWYln91UhZAasoFuJirwxuw1ZADEPLNz6ZAn4l96VA6rO1ca6TZAXuaPUZA7ZByRZCgIrack3MmQDQ5U1z7QNaV6uPuwLk27z9VoAYv70ZBO79KQzAyRPjD3BynHTbFq3gT3jEyDhYvxWVZB2sL8F4AWhd8LSuuIRmSfC2Sl6WflCdCJHF24")
PHONE_NUMBER_ID = "1071239746066018"
VERIFY_TOKEN = "my_secret_token_123"

# Duplicate message filter
processed_messages = set()


# WhatsApp message send function
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

    # API response log
    print("WhatsApp API Response:", response.text)


# Webhook route
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Verification
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Forbidden", 403

    # Receive messages
    if request.method == "POST":

        data = request.get_json()

        try:
            value = data["entry"][0]["changes"][0]["value"]

            if "messages" in value:

                message = value["messages"][0]
                message_id = message["id"]

                # Duplicate message check
                if message_id in processed_messages:
                    return "duplicate", 200

                processed_messages.add(message_id)

                sender = message["from"]

                # Only handle text messages
                if message.get("type") == "text":

                    user_message = message["text"]["body"]

                    # chatbot.py reply
                    reply = get_response(user_message)

                    send_whatsapp_message(sender, reply)

        except Exception as e:
            print("Error:", e)

        return "EVENT_RECEIVED", 200


# Home route
@app.route("/")
def home():
    return "Bot running successfully"


# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
