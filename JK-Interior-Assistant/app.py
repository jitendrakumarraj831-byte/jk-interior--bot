import os
import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = "EAAMjzXE0bacBQZCIcbZAJvaNuFVJlEVKMGUCxWA2bKXv314cXgF3ZCpJcIcxGWrZAAnFT0abFAP3Eghwr3MiZCsZChk2cEdVchMynqcR2Rk70d4LuzUf9FSsJS5aWfIa4yZBnWZBtpW6Odso444lxTC1p5Vw6MxvRempY0lz7O4hnWaC0XIGoU1ZATpOcybpgQsdZA3iV7FSXBwiibF1cjZCzcEUI2WeOZCSy6m6qXX57BLN7qyWYIN8pzql2ieHfdLIOCoxlwmiUhEXNeqPgbktvgcD"
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

    requests.post(url, headers=headers, json=data)


@app.route("/webhook", methods=["GET","POST"])
def webhook():

    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Forbidden", 403

    if request.method == "POST":

        data = request.get_json()

        try:
            if "messages" in data["entry"][0]["changes"][0]["value"]:

                message = data["entry"][0]["changes"][0]["value"]["messages"][0]

                sender = message["from"]

                from chatbot import get_response

               user_message = message["text"]["body"]
               reply = get_response(user_message)

              send_whatsapp_message(sender, reply)

        except:
            pass

        return "EVENT_RECEIVED", 200


@app.route("/")
def home():
    return "Bot running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
