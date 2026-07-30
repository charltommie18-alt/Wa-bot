import streamlit as st
import os
from supabase import create_client

# 1. Connect to Supabase using Environment Variables
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Missing Supabase Environment Variables")
    st.stop()

# DEBUG: Show what's being read
st.write(f"URL: {supabase_url}")
st.write(f"Key starts with: {supabase_key[:20]}...")



supabase = create_client(supabase_url, supabase_key)

# 2. Dashboard UI Setup
st.set_page_config(page_title="WaBot Admin", page_icon="🤖", layout="wide")
st.title("🤖 WaBot Training Dashboard")
st.markdown("---")

# Create two tabs: One to add businesses, one to train them
tab1, tab2 = st.tabs([" Manage Businesses", "🧠 Train Bot (Add Knowledge)"])

# --- TAB 1: ADD A BUSINESS ---
with tab1:
    st.header("Register a New Business")
    col1, col2 = st.columns(2)
    
    with col1:
        new_biz_name = st.text_input("Business Name", placeholder="e.g. Cape Town Coffee")
    with col2:
        new_phone_id = st.text_input("Meta Phone ID", placeholder="e.g. 1288061827718112")
        
    if st.button("Create Business", type="primary"):
        if new_biz_name and new_phone_id:
            try:
                # Check if business already exists
                check = supabase.table("businesses").select("id").eq("phone_id", new_phone_id).execute()
                if check.data:
                    st.warning("A business with this Phone ID already exists!")
                else:
                    # Insert new business
                    supabase.table("businesses").insert({"name": new_biz_name, "phone_id": new_phone_id}).execute()
                    st.success(f"✅ Successfully created: {new_biz_name}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill in both fields.")

    # Show existing businesses
    st.subheader("Current Businesses")
    businesses = supabase.table("businesses").select("*").execute()
    if businesses.data:
        st.table(businesses.data)
    else:
        st.info("No businesses added yet.")

# --- TAB 2: TRAIN THE BOT ---
with tab2:
    st.header("Add Knowledge to the Bot")
    
    # Fetch businesses to select from
    businesses = supabase.table("businesses").select("id, name, phone_id").execute()
    
    if not businesses.data:
        st.warning("Please add a business in the first tab before training.")
    else:
        # Create a dropdown of businesses
        biz_options = {f"{b['name']} ({b['phone_id']})": b['id'] for b in businesses.data}
        selected_biz_name = st.selectbox("Select Business to Train", list(biz_options.keys()))
        selected_biz_id = biz_options[selected_biz_name]
        
        # Text area for knowledge
        knowledge_text = st.text_area(
            "Paste Business Info / FAQs here:", 
            height=200, 
            placeholder="We open at 7 AM. Our best seller is the Rooibos Latte for R45..."
        )
        
        if st.button(" Save Knowledge to Database", type="primary"):
            if knowledge_text:
                try:
                    # Insert the knowledge linked to the business ID
                    supabase.table("knowledge_base").insert({
                        "business_id": selected_biz_id, 
                        "content": knowledge_text
                    }).execute()
                    st.success("✅ Knowledge saved! The bot will now use this info.")
                except Exception as e:
                    st.error(f"Error saving: {e}")
            else:
                st.error("Please enter some text to train the bot.")
