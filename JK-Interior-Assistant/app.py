import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# मेटा वेबहुक वेरिफिकेशन टोकन
VERIFY_TOKEN = "my_secret_token_123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. मेटा वेरिफिकेशन (GET Request)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Webhook Verified successfully!")
            return challenge, 200
        else:
            return 'Forbidden', 403

    # 2. मैसेज रिसीव करना (POST Request)
    if request.method == 'POST':
        data = request.json
        print("मैसेज रिसीव हुआ:", data)
        
        # मेटा को 200 OK भेजना अनिवार्य है
        return 'EVENT_RECEIVED', 200

# स्वास्थ्य जाँच (Health Check) के लिए एक रूट - यह Render के लिए अच्छा है
@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

if __name__ == '__main__':
    # Render का दिया हुआ पोर्ट इस्तेमाल करें, वरना 5000 पर चलाएं
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
