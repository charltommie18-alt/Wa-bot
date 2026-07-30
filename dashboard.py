import streamlit as st
from supabase import create_client
import pandas as pd
import openai
import os

st.set_page_config(page_title="WaBot Dashboard", layout="wide")
st.title("🤖 WaBot Training Dashboard")

# --- Load Secrets ---
try:
    SUPABASE_URL = str(st.secrets["SUPABASE_URL"]).strip().strip('"').strip("'")
    SUPABASE_KEY = str(st.secrets["SUPABASE_KEY"]).strip().strip('"').strip("'")
    OPENAI_KEY = str(st.secrets["OPENAI_API_KEY"]).strip().strip('"').strip("'")
except Exception as e:
    st.error(f"❌ Secrets missing in Streamlit. Go to Settings -> Secrets. Error: {e}")
    st.stop()

# --- Debug ---
if not SUPABASE_URL.startswith("https://"):
    st.error(f"❌ SUPABASE_URL is wrong! You put: {SUPABASE_URL[:20]}... It must start with https://")
    st.stop()
if not SUPABASE_KEY.startswith("sb_"):
    st.error(f"❌ SUPABASE_KEY is wrong! You put: {SUPABASE_KEY[:20]}... It must start with sb_secret_")
    st.stop()

# --- Connect ---
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # test connection
    supabase.table("training_data").select("*").limit(1).execute()
    st.success("✅ Connected to Supabase!")
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.info(f"URL you sent: {SUPABASE_URL}")
    st.info(f"KEY you sent: {SUPABASE_KEY[:20]}... (length {len(SUPABASE_KEY)})")
    st.stop()

# --- Sidebar ---
st.sidebar.header("Settings")
openai.api_key = OPENAI_KEY

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📚 View Training Data", "➕ Add Training Data", "🧪 Test AI"])

with tab1:
    st.subheader("Current Training Data")
    try:
        data = supabase.table("training_data").select("*").execute()
        df = pd.DataFrame(data.data)
        if df.empty:
            st.info("No data yet. Add some in Tab 2.")
        else:
            st.dataframe(df, use_container_width=True)
            st.write(f"Total rows: {len(df)}")
    except Exception as e:
        st.error(f"Error loading data: {e}")

with tab2:
    st.subheader("Add New Q&A")
    with st.form("add_form"):
        question = st.text_input("User Question (what customer will ask)")
        answer = st.text_area("Bot Answer (how bot should reply)")
        category = st.selectbox("Category", ["general", "pricing", "support", "product", "other"])
        submit = st.form_submit_button("Add to Database")
        if submit:
            if not question or not answer:
                st.warning("Fill both question and answer")
            else:
                try:
                    supabase.table("training_data").insert({
                        "question": question,
                        "answer": answer,
                        "category": category
                    }).execute()
                    st.success("✅ Added!")
                except Exception as e:
                    st.error(f"Failed: {e}")

with tab3:
    st.subheader("Test Your Bot")
    user_q = st.text_input("Ask something like a customer")
    if st.button("Ask AI"):
        if not user_q:
            st.warning("Type a question")
        else:
            try:
                # Get training data
                training = supabase.table("training_data").select("*").execute()
                context = "\n".join([f"Q: {r['question']}\nA: {r['answer']}" for r in training.data[:20]])

                prompt = f"You are WaBot. Use this training data to answer:\n{context}\n\nUser asks: {user_q}\nAnswer helpfully:"

                client = openai.OpenAI(api_key=OPENAI_KEY)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"OpenAI Error: {e}")
