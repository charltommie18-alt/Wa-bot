from flask import Flask, request
import requests
import os

app = Flask(__name__)

# These come from Railway Variables - don't change these lines
VERIFY_TOKEN = "capetownbot123" # You can change this if you want
ACCESS_TOKEN = os.getenv("TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

@app.route('/')
def home():
    return 'Cape Town Bot is running!'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Meta uses this to verify your bot
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verify token', 403
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            # Check if it's a WhatsApp message
            if data['entry'][0]['changes'][0]['value'].get('messages'):
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                from_number = message['from']
                msg_body = message['text']['body'].lower()
                
                # Bot logic - change these replies for your business
                if msg_body == '1':
                    reply = "Our prices:\nBasic: R200\nPro: R500\nDM us for custom quotes!"
                elif msg_body == '2':
                    reply = "We're open:\nMon-Fri: 9am-5pm SAST\nSat: 10am-2pm\nSun: Closed"
                elif msg_body == '3':
                    reply = "A human will reply soon. Or call us: +27 XX XXX XXXX"
                else:
                    reply = "Hi from Cape Town Bot Service! 👋\n\nReply:\n1 for Prices\n2 for Hours\n3 to talk to a human"
                
                send_whatsapp_message(from_number, reply)
        except:
            pass
        return 'OK', 200

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v25.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == '__main__':
    app.run(debug=True)
