import os
from flask import Flask, request, jsonify, Response
import requests
from supabase import create_client
from openai import OpenAI

app = Flask(__name__)

# --- ENV VARS from Render ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")

PAYPAL_LINK = "https://www.paypal.com/ncp/payment/Z73J76V7HHXN8"
WA_NUMBER = "27662860184"
WA_LINK = f"https://wa.me/{WA_NUMBER}?text=Hi%20HowzitBot%20I%20want%20to%20get%20started"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HowzitBot - AI Staff on WhatsApp</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
*{font-family:Inter,sans-serif;margin:0;padding:0;box-sizing:border-box}
body{background:#FAFFFE;color:#0B141A}
.hero{max-width:1120px;margin:0 auto;padding:60px 24px;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
@media(max-width:900px){.hero{grid-template-columns:1fr}}
h1{font-size:48px;line-height:0.95;letter-spacing:-0.03em;font-weight:800}
.btn{display:inline-flex;height:48px;align-items:center;justify-content:center;padding:0 28px;border-radius:999px;font-weight:600;text-decoration:none;transition:.2s;cursor:pointer;border:none}
.btn-green{background:#25D366;color:#0B141A;box-shadow:0 8px 24px rgba(37,211,102,.35)}
.btn-black{background:#0B141A;color:white}
.card{background:white;border:1px solid rgba(0,0,0,.06);border-radius:24px;padding:24px;box-shadow:0 8px 32px rgba(0,0,0,.04)}
input{width:100%;height:48px;border-radius:999px;border:1px solid rgba(0,0,0,.1);padding:0 16px;margin-top:8px;font-size:14px}
.float-wa{position:fixed;bottom:20px;right:20px;background:#25D366;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 28px rgba(37,211,102,.5);z
