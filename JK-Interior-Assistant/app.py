from flask import Flask, request, jsonify
import chatbot

app = Flask(__name__)

# META VERIFICATION (Ye step bahut zaroori hai)
@app.route('/webhook', methods=['GET'])
def verify():
    # Meta yahan ek token bhejega, humein wahi vapas bhejna hai
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Yahan 'my_secret_token_123' ki jagah wahi token daalein jo aap Meta Dashboard mein dalenge
    if mode == "subscribe" and token == "my_secret_token_123":
        return challenge, 200
    else:
        return "Verification failed", 403

# MESSAGE HANDLING
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # WhatsApp se aaya message
    try:
        user_message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        reply = chatbot.get_response(user_message)
        # Yahan se hum WhatsApp ko reply bhejenge (Agla step)
        return jsonify({"status": "received", "reply": reply})
    except:
        return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(port=5000)
