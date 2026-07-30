import streamlit as st
import os
from supabase import create_client

st.set_page_config(page_title="WaBot Admin", layout="wide")

# 1. Connect to Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Missing Supabase Environment Variables")
    st.stop()

supabase = create_client(supabase_url, supabase_key)

# 2. Dashboard UI Setup
st.title("🤖 WaBot Training Dashboard")
st.markdown("---")

tab1, tab2 = st.tabs([" Manage Businesses", "🧠 Train Bot"])

with tab1:
    st.header("Businesses")
    # your business code here

with tab2:
    st.header("Train Bot")
    # your training code here
