from flask import Flask, request, jsonify
import chatbot  # Ye aapki purani file chatbot.py ko connect karega

app = Flask(__name__)

# WhatsApp jab message bheje ga, toh isi URL par aayega
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Yahan hum WhatsApp se aaya message nikal rahe hain
    user_message = data.get('message', '') 
    
    # Ye aapke chatbot.py ka function call karega
    reply = chatbot.get_response(user_message)
    
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(port=5000)
