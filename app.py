import os
from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "HowzitBot LIVE - AI powered"

@app.route("/api/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # For Meta verification
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Wrong token", 403

    # POST - incoming WhatsApp
    data = request.json
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            from_num = msg["from"]
            text = msg["text"]["body"]

            # AI SMART REPLY - minimal code
            ai_reply = get_ai_reply(text)

            send_whatsapp(from_num, ai_reply)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

def get_ai_reply(user_text):
    # If no OpenAI key, use simple smart reply
    if not OPENAI_KEY:
        return f"Howzit! You said: {user_text}. I'm your AI assistant for Oudtshoorn - how can I help?"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are HowzitBot, a helpful assistant for a South African business in Oudtshoorn. Be friendly, short, use Afrikaans slang like 'Howzit', 'Lekker'."},
                {"role": "user", "content": user_text}
            ]
        )
        return res.choices[0].message.content
    except:
        return "Sorry, AI is sleeping. Try again!"

def send_whatsapp(to, text):
    if not WHATSAPP_TOKEN or not PHONE_ID:
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=data, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
