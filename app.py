import os
import requests
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify, send_from_directory
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def homepage():
    return send_from_directory('.', 'index.html')

@app.route('/health')
def health():
    return "OK", 200

# Env vars
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
APP_SECRET = os.environ.get("APP_SECRET")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

GRAPH_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"

def get_supabase():
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

@app.route('/api/lead', methods=['POST'])
def save_lead():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        business = data.get('business_name', '').strip()
        country = data.get('country', 'ZA')
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        supabase = get_supabase()
        if supabase:
            supabase.table("leads").insert({
                "email": email,
                "business_name": business,
                "country": country,
                "free_credits": 50,
                "status": "new_lead"
            }).execute()
            logger.info(f"Lead saved: {email} - {business}")
        
        return jsonify({"success": True, "credits": 50}), 200
    except Exception as e:
        logger.error(f"Lead save failed: {e}")
        return jsonify({"success": True, "credits": 50}), 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            if data and "entry" in data:
                for entry in data["entry"]:
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        for msg in value.get("messages", []):
                            from_num = msg.get("from")
                            text = msg.get("text", {}).get("body", "")
                            if from_num and text:
                                send_whatsapp_message(from_num, f"Howzit! You said: {text}\n\nI'm HowzitBot - Bot: +1 (555) 143-6700")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
        return jsonify({"status": "ok"}), 200

def send_whatsapp_message(to, text):
    if not WHATSAPP_TOKEN or not PHONE_ID:
        return
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    try:
        requests.post(GRAPH_API_URL, headers=headers, json=payload)
    except Exception as e:
        logger.error(f"Send failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
