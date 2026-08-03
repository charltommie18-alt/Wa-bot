
import os
from flask import Flask, request, jsonify, Response, send_from_directory
import requests
from supabase import create_client
from openai import OpenAI

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot123")

PAYPAL_LINK = "https://www.paypal.com/ncp/payment/Z73J76V7HHXN8"
WA_NUMBER = "27662860184"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- SERVE hero.mp4 from anywhere ---
@app.route("/hero.mp4")
def serve_hero():
    # Try root first, then .devcontainer
    if os.path.exists("hero.mp4"):
        return send_from_directory(".", "hero.mp4")
    if os.path.exists(".devcontainer/hero.mp4"):
        return send_from_directory(".devcontainer", "hero.mp4")
    # fallback to coverr video
    return Response(status=302, headers={"Location":"https://cdn.coverr.co/videos/coverr-a-man-using-his-phone-in-an-office-1578/1080p.mp4"})

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>HowzitBot - AI Staff on WhatsApp | R299/mo</title>
<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');*{font-family:Inter,sans-serif;margin:0;padding:0;box-sizing:border-box}body{background:#FAFFFE;color:#0B141A}.hero{max-width:1120px;margin:0 auto;padding:60px 24px;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}@media(max-width:900px){.hero{grid-template-columns:1fr}}h1{font-size:48px;line-height:0.95;font-weight:800}.btn{display:inline-flex;height:48px;align-items:center;justify-content:center;padding:0 28px;border-radius:999px;font-weight:600;text-decoration:none;cursor:pointer;border:none}.btn-green{background:#25D366;color:#0B141A;box-shadow:0 8px 24px rgba(37,211,102,.35)}.btn-black{background:#0B141A;color:white}.card{background:white;border:1px solid rgba(0,0,0,.06);border-radius:24px;padding:24px}input{width:100%;height:48px;border-radius:999px;border:1px solid rgba(0,0,0,.1);padding:0 16px;margin-top:8px}.float-wa{position:fixed;bottom:20px;right:20px;background:#25D366;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;z-index:999}}</style>
</head><body>
<div style="background:#0B141A;color:white;text-align:center;padding:10px;font-size:13px">Launch Special - <span style="color:#25D366;font-weight:700">50 FREE AI replies</span> - No card needed</div>
<header style="max-width:1120px;margin:0 auto;padding:16px 24px;display:flex;justify-content:space-between"><div style="font-weight:800">HowzitBot <span style="background:#25D3661A;border:1px solid #25D36633;padding:2px 8px;border-radius:999px;font-size:11px;color:#128C7E">AI Staff on WhatsApp</span></div><div style="display:flex;gap:12px"><a href="https://wa.me/27662860184" style="text-decoration:none;color:#0B141A;font-weight:600;font-size:14px">066 286 0184</a><a href="#pricing" class="btn btn-black" style="height:36px">Get Started</a></div></header>
<section class="hero"><div><div style="display:inline-flex;border:1px solid #25D36633;background:#25D3661A;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:600;margin-bottom:16px">50 Free Credits • Cancel anytime</div><h1>Tired of answering <span style="background:linear-gradient(to bottom,transparent 60%,#25D36655 60%)">the same</span> WhatsApps?</h1><p style="margin-top:20px;color:rgba(0,0,0,.6);font-size:17px;line-height:1.6;max-width:520px">HowzitBot trains on <b>YOUR business</b> and answers customers automatically on WhatsApp. 24/7 - on 066 286 0184.</p><div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap"><a href="https://wa.me/27662860184?text=Hi%20HowzitBot%20I%20want%2050%20free%20credits" target="_blank" class="btn btn-green">Try on WhatsApp - Free</a><a href="#how" class="btn btn-black">How it works</a></div></div><div><div class="card" style="padding:0;overflow:hidden"><video autoplay loop muted playsinline style="width:100%;height:420px;object-fit:cover;display:block"><source src="/hero.mp4" type="video/mp4"></video><div style="padding:16px;display:flex;justify-content:space-between"><div><div style="font-weight:700">HowzitBot AI Demo</div><div style="font-size:12px;color:rgba(
