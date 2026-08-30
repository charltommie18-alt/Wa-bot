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
    return send_from_directory(".", "index.html")

@app.route("/api/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode")=="subscribe" and request.args.get("hub.verify_token")==VERIFY_TOKEN:
        return Response(request.args.get("hub.challenge"), status=200, mimetype="text/plain")
    return Response("Verification failed", status=403)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    data=request.get_json()
    print("INCOMING:", data)
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value:
            return jsonify({"status":"ok"})
        msg = value['messages'][0]
        from_num = msg['from']
        user_text = msg.get('text', {}).get('body', '')
        if not user_text:
            return jsonify({"status":"ok"})

        answer = None
        try:
            r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data", params={"select":"answer","question":f"ilike.*{user_text}*","limit":"1"}, headers=headers, timeout=10)
            if r.status_code==200 and r.json():
                answer = r.json()[0]['answer']
        except Exception as e:
            print("Supabase search error:", e)

        if not answer:
            try:
                r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data", params={"select":"question,answer","limit":"20"}, headers=headers, timeout=10)
                training = r.json() if r.status_code==200 else []
                context = "\n".join([f"Q: {x['question']}\nA: {x['answer']}" for x in training])
                prompt = f"You are HowzitBot SA business staff. Training:\n{context}\n\nCustomer: {user_text}\nReply friendly SA English:"
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
                answer = resp.choices[0].message.content
            except Exception as e:
                print("OpenAI error:", e)
                answer = "Howzit! I'm offline now, try again just now."

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
