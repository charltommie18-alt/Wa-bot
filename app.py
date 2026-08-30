import os
from flask import Flask, request, jsonify, Response, send_from_directory
import requests, httpx, openai

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    if os.path.exists("index.html"):
        return send_from_directory(".", "index.html")
    return "<h1>HowzitBot Live - Upload index.html</h1>"

@app.route("/hero.mp4")
def hero():
    if os.path.exists("hero.mp4"):
        return send_from_directory(".", "hero.mp4")
    if os.path.exists(".devcontainer/hero.mp4"):
        return send_from_directory(".devcontainer", "hero.mp4")
    return Response(status=302, headers={"Location":"https://cdn.coverr.co/videos/coverr-a-man-using-his-phone-in-an-office-1578/1080p.mp4"})

@app.route("/api/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode=="subscribe" and token==VERIFY_TOKEN:
        return Response(challenge, status=200)
    return Response("Verification failed", status=403)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    data=request.get_json()
    print("INCOMING:", data)
    try:
        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        if 'messages' not in value:
            return jsonify({"status":"ok"})
        
        msg = value['messages'][0]
        from_num = msg['from']
        user_text = msg.get('text', {}).get('body', '')
        if not user_text:
            return jsonify({"status":"ok"})

        # 1. Supabase exact/fuzzy match
        answer = None
        try:
            # simple ilike search
            r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data", params={"select":"answer","question":"ilike.*"+user_text+"*","limit":"1"}, headers=headers, timeout=10)
            if r.status_code==200 and r.json():
                answer = r.json()[0]['answer']
        except Exception as e:
            print("Supabase search error:", e)

        # 2. Fallback to OpenAI with training context
        if not answer:
            try:
                r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data", params={"select":"question,answer","limit":"20"}, headers=headers, timeout=10)
                training = r.json() if r.status_code==200 else []
                context = "\n".join([f"Q: {x.get('question')}\nA: {x.get('answer')}" for x in training])
                prompt = f"You are HowzitBot, an AI staff for SA businesses in Cape Town. Use this training data:\n{context}\n\nCustomer says: {user_text}\nReply helpfully in friendly South African English (Howzit style), short and WhatsApp friendly:"

                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
                answer = resp.choices[0].message.content
            except Exception as e:
                print("OpenAI error:", e)
                answer = "Howzit! I'm a bit offline now, but I'll be back just now. Please try again."

        # 3. Send via WhatsApp Cloud API - FREE within 24h window
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        wa_headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type":"application/json"}
        payload = {"messaging_product":"whatsapp","to":from_num,"type":"text","text":{"body":answer[:4000]}}
        resp = requests.post(url, json=payload, headers=wa_headers)
        print("WA SEND:", resp.status_code, resp.text)

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return jsonify({"status":"ok"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
