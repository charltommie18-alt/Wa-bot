import os
import requests
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify

# Configure logging so you can see what's happening in Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load Environment Variables (Set these in Render)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
APP_SECRET = os.environ.get("APP_SECRET") # Crucial for security

# Meta Graph API URL (Using a recent stable version)
GRAPH_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"

def verify_signature(request):
    """Verify the request signature to ensure it's actually from Meta"""
    if not APP_SECRET:
        logger.warning("APP_SECRET not set, skipping signature verification.")
        return True
        
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        return False
        
    expected_signature = "sha256=" + hmac.new(
        APP_SECRET.encode('utf-8'),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def send_message(recipient_id, message_text):
    """Helper function to send a text message via WhatsApp Cloud API"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    
    try:
        response = requests.post(GRAPH_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent to {recipient_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Bot is live", "version": "1.1.0"}), 200

@app.route("/webhook", methods=["GET"])
def verify():
    """Meta uses this to verify your webhook URL"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logger.warning("Verification failed. Tokens do not match.")
            return "Forbidden", 403
    return "Bad Request", 400

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming WhatsApp messages"""
    # 1. Security: Verify the request is from Meta
    if not verify_signature(request):
        logger.warning("Invalid webhook signature")
        return "Unauthorized", 401

    # 2. Parse the incoming JSON payload
    data = request.get_json()
    if not data:
        return "OK", 200

    try:
        # Navigate the complex Meta payload structure
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        # Check if this event is a new message
        if changes.get("field") == "messages":
            messages = value.get("messages", [])
            
            for message in messages:
                sender_id = message.get("from")
                msg_type = message.get("type")
                
                # For now, we only process text messages
                if msg_type == "text":
                    message_text = message.get("text", {}).get("body", "")
                    logger.info(f"Received text from {sender_id}: {message_text}")
                    
                    # ==========================================
                    # 🧠 AI & DATABASE LOGIC WILL GO HERE LATER
                    # ==========================================
                    
                    # Temporary auto-reply to prove it works
                    reply_text = f"Thanks for your message! You said: '{message_text}'. (AI integration coming soon!)"
                    send_message(sender_id, reply_text)
                    
                else:
                    logger.info(f"Received non-text message of type: {msg_type}")
                    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")

    # Meta requires a 200 OK response within 20 seconds, or it will retry
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
