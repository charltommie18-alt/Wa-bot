import streamlit as st
import os
import pandas as pd

# --- 1. LOAD KEYS (Works on both Streamlit Cloud and Render) ---
try:
    # On Streamlit Cloud
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    # On Render / Local
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Clean keys (remove quotes/spaces that break Supabase)
SUPABASE_URL = str(SUPABASE_URL).strip().replace('"','').replace("'","")
SUPABASE_KEY = str(SUPABASE_KEY).strip().replace('"','').replace("'","")
OPENAI_API_KEY = str(OPENAI_API_KEY).strip().replace('"','').replace("'","")

# --- 2. CONNECT TO SUPABASE ---
from supabase import create_client, Client

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE keys are missing! Go to Streamlit Settings -> Secrets and add them.")
    st.stop()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.info(f"URL you sent: {SUPABASE_URL[:30]}...")
    st.stop()

# --- 3. PAGE UI ---
st.set_page_config(page_title="WaBot Dashboard", page_icon="🤖", layout="wide")
st.title("🤖 WaBot Training Dashboard")
st.success("✅ Connected to Supabase!")

# --- 4. TABS ---
tab1, tab2, tab3 = st.tabs(["📚 View Training Data", "➕ Add New FAQ", "⚙️ Settings"])

with tab1:
    st.header("Current Training Data")
    try:
        response = supabase.table("training_data").select("*").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.write(f"Total rows: {len(df)}")
        else:
            st.info("No training data yet. Add some in the next tab.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Make sure you have a table named 'training_data' in Supabase with columns: question, answer")

with tab2:
    st.header("Add New Training")
    with st.form("add_form"):
        question = st.text_input("Customer Question")
        answer = st.text_area("Bot Answer")
        submitted = st.form_submit_button("Add to Bot")
        if submitted:
            if question and answer:
                try:
                    supabase.table("training_data").insert({"question": question, "answer": answer}).execute()
                    st.success(f"✅ Added: {question}")
                except Exception as e:
                    st.error(f"Failed to add: {e}")
            else:
                st.warning("Please fill both fields")

with tab3:
    st.header("Connection Status")
    st.write(f"**Supabase URL:** {SUPABASE_URL}")
    st.write(f"**Supabase Key:** {SUPABASE_KEY[:10]}...{SUPABASE_KEY[-4:]}")
    st.write(f"**OpenAI Key:** {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
    if st.button("Test OpenAI"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            res = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":"Say hi"}])
            st.success(f"OpenAI Works: {res.choices[0].message.content}")
        except Exception as e:
            st.error(f"OpenAI Error: {e}")
