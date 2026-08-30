import streamlit as st
import pandas as pd
import openai
import httpx

st.set_page_config(page_title="WaBot Dashboard", layout="wide")
st.title("🤖 WaBot Training Dashboard")

# --- Secrets ---
SUPABASE_URL = str(st.secrets["SUPABASE_URL"]).strip().strip('"').strip("'").rstrip("/")
SUPABASE_KEY = str(st.secrets["SUPABASE_KEY"]).strip().strip('"').strip("'")
OPENAI_KEY = str(st.secrets["OPENAI_API_KEY"]).strip().strip('"').strip("'")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- Test Connection ---
try:
    r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data?select=*&limit=1", headers=headers, timeout=10)
    if r.status_code in [200, 206]:
        st.success(f"✅ Connected to Supabase! Key length {len(SUPABASE_KEY)} works!")
    else:
        st.error(f"❌ Supabase returned {r.status_code}: {r.text}")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection failed: {e}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📚 View Data", "➕ Add Data", "🧪 Test AI"])

with tab1:
    st.subheader("Current Training Data")
    try:
        r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data?select=*&order=id.desc", headers=headers, timeout=10)
        data = r.json()
        df = pd.DataFrame(data)
        if df.empty:
            st.info("No data yet. Add some in Tab 2.")
        else:
            st.dataframe(df, use_container_width=True)
            st.write(f"Total rows: {len(df)}")
    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    st.subheader("Add New Q&A")
    with st.form("add_form"):
        question = st.text_input("User Question")
        answer = st.text_area("Bot Answer")
        category = st.selectbox("Category", ["general", "pricing", "support", "product", "other"])
        submit = st.form_submit_button("Add to Database")
        if submit:
            if not question or not answer:
                st.warning("Fill both fields")
            else:
                try:
                    r = httpx.post(f"{SUPABASE_URL}/rest/v1/training_data", headers=headers, json={
                        "question": question,
                        "answer": answer,
                        "category": category
                    }, timeout=10)
                    if r.status_code in [200, 201]:
                        st.success("✅ Added!")
                    else:
                        st.error(f"Failed {r.status_code}: {r.text}")
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
                r = httpx.get(f"{SUPABASE_URL}/rest/v1/training_data?select=question,answer&limit=20", headers=headers, timeout=10)
                training = r.json()
                context = "\n".join([f"Q: {x['question']}\nA: {x['answer']}" for x in training])
                prompt = f"You are WaBot. Use this training data:\n{context}\n\nUser asks: {user_q}\nAnswer helpfully:"

                client = openai.OpenAI(api_key=OPENAI_KEY)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"OpenAI Error: {e}")
