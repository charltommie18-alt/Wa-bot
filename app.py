import os
import requests
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# === EMAILJS - AUTO EMAIL TO YOU ===
EMAILJS_SERVICE_ID = "service_r58xvdz"
EMAILJS_TEMPLATE_ID = "template_bp7wufo"
EMAILJS_PUBLIC_KEY = "2lEmbRRtEMVwbX5SU"

def send_auto_email(phone, customer_message, bot_reply):
    try:
        url = "https://api.emailjs.com/api/v1.0/email/send"
        data = {
            "service_id": EMAILJS_SERVICE_ID,
            "template_id": EMAILJS_TEMPLATE_ID,
            "user_id": EMAILJS_PUBLIC_KEY,
            "template_params": {
                "phone": phone,
                "message": customer_message,
                "bot_reply": bot_reply,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S SA")
            }
        }
        r = requests.post(url, json=data, timeout=10)
        print(f"✅ EmailJS: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
# === END EMAILJS ===

@app.route("/")
def home():
    return "HowzitBot FREE AI LIVE - 100% Free + Auto Email"

@app.route("/api/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Forbidden", 403

    data = request.get_json()
    if not data:
        return "OK", 200

    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            user_text = message["text"]["body"]

            ai_text = get_free_ai(user_text)
            send_whatsapp(from_number, ai_text)

            # AUTO EMAIL YOU INSTANTLY
            send_auto_email(from_number, user_text, ai_text)

    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

def get_free_ai(user_text):
    if not GROQ_KEY:
        return f"Howzit! You said: {user_text}. My free AI is not connected yet - add GROQ_API_KEY in Render."

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are HowzitBot, a friendly, helpful AI assistant for a small business in Oudtshoorn, South Africa. Use casual SA slang like Howzit, Lekker, Eish. Keep answers short (under 3 sentences)."},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Eish! My free brain is thinking too hard. Try again now?"

def send_whatsapp(to, text):
    if not WHATSAPP_TOKEN or not PHONE_ID:
        print("Missing WHATSAPP_TOKEN or PHONE_ID")
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:3900]}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
