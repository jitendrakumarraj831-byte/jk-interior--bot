from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. मेटा द्वारा वेरिफिकेशन (GET Request)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == 'my_secret_token_123':
            return challenge, 200
        else:
            return 'Forbidden', 403

    # 2. मैसेज रिसीव करना (POST Request)
    if request.method == 'POST':
        data = request.json
        print("मैसेज रिसीव हुआ:", data) # यह Render के Logs में दिखेगा
        
        # मेटा को 200 OK भेजना ज़रूरी है ताकि एरर न आए
        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(port=5000)
    
