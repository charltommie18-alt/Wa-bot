import os
import requests
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify, send_from_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def homepage():
    return send_from_directory('.', 'index.html')

@app.route('/health')
def health():
    return "OK", 200

# Load Environment Variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
APP_SECRET = os.environ.get("APP_SECRET")

GRAPH_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"

def verify_signature(request):
    if not APP_SECRET:
        logger.warning("APP_SECRET not set, skipping verification")
        return True
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        return False
    try:
        expected = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature.split("=")[1], expected)
    except:
        return False

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
