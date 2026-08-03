
import os
from flask import Flask, request, jsonify, Response, send_from_directory
import requests

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")

@app.route("/")
def home():
    # Serve your index.html file
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
    if request.args.get("hub.mode")=="subscribe" and request.args.get("hub.verify_token")==VERIFY_TOKEN:
        return Response(request.args.get("hub.challenge"), status=200)
    return Response("Failed", status=403)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    data=request.get_json()
    print(data)
    return jsonify({"status":"ok"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
