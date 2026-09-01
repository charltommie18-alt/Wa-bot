from flask import Flask, request
import os, requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return "HowzitBot FREE AI LIVE - 100% Free + Auto Email", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' not in entry:
            return "OK", 200

        msg = entry['messages'][0]
        from_number = msg['from']
        text = msg['text']['body']

        # Groq FREE AI
        groq_res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": text}]
            }
        )
        reply = groq_res.json()['choices'][0]['message']['content']

        # Send WhatsApp reply
        requests.post(
            f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": reply}
            }
        )

        # EmailJS - FIXED IDS + TO EMAIL FROM CODE
        requests.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            headers={"Content-Type": "application/json"},
            json={
                "service_id": "service_m3wpi6m",
                "template_id": "template_fsp6946",
                "user_id": "wro1MTGjT1a2eQy7t",
                "template_params": {
                    "to_email": "charltommie18@gmail.com",
                    "phone": from_number,
                    "message": text,
                    "bot_reply": reply,
                    "name": "WhatsApp Lead",
                    "time": "now"
                }
            }
        )
        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
