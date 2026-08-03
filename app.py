from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL")  # you already have this in Render
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if os.path.exists(path) and "." in path:  # only serve real files
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

@app.route('/api/lead', methods=['POST'])
def lead():
    try:
        data = request.get_json()
        email = data.get("email")
        business = data.get("business", "")
        
        print(f"NEW LEAD: {email} - {business}")

        # Save to Supabase leads table
        if SUPABASE_URL and SUPABASE_KEY:
            url = f"{SUPABASE_URL}/rest/v1/leads"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            payload = {
                "email": email,
                "business_name": business,
                "phone": "0662860184",
                "created_at": datetime.utcnow().isoformat()
            }
            r = requests.post(url, json=payload, headers=headers)
            print("Supabase response:", r.status_code, r.text)
        
        return jsonify({"status":"ok","saved":True})
    except Exception as e:
        print("Lead error:", str(e))
        return jsonify({"status":"error","msg":str(e)}), 500

@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    # KEEP YOUR EXISTING WHATSAPP WEBHOOK CODE HERE
    # This is just placeholder so we don't break it
    if request.method == 'GET':
        # Verify token logic
        if request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    # POST - handle WhatsApp messages (keep your old code)
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
