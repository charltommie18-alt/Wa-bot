# WaBot - Free WhatsApp Cloud API (No BSP Fee)

This is the FREE version of HowzitBot moved off Facebook Messenger policy.

## Why free?
- Uses WhatsApp Cloud API direct from Meta - no WATI/Respond.io monthly fee
- Reply inside 24h window = R0
- Hosted on Render free tier via Procfile

## Setup
1. Push this to your GitHub: charltommie18-alt/Wa-bot
2. Go to render.com -> New Web Service -> Connect repo
3. Add Env Vars: SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN
4. Deploy

## WhatsApp Webhook
In developers.facebook.com -> WhatsApp -> Configuration:
Callback URL: https://your-render-url.onrender.com/api/webhook
Verify Token: bot123 (or what you set in VERIFY_TOKEN)
Subscribe to: messages

Migrate your number 066 286 0184 from WhatsApp Business App to Cloud API to keep same number.

## Dashboard
Streamlit dashboard: streamlit run dashboard.py
