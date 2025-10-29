# app.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from io import BytesIO
from word_report import perform_seo_audit, create_word_report

# ------------------- Streamlit UI -------------------
st.set_page_config(
    page_title="AI Chatbot & SEO Auditor",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #EEAECA 0%, #94BBE9 100%); }
    .stTextInput>div>div>input {
        background-color: #fff;
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
    }
    .stExpander {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI Chatbot with SEO Audit")
st.markdown("Enter a website URL below to generate an on-page SEO audit report in a Word document.")

# ------------------- SEO AUDIT SECTION -------------------
url_input = st.text_input("Website URL", placeholder="e.g., https://streamlit.io")

if st.button("Generate SEO Report"):
    if url_input:
        with st.spinner("Analyzing website... please wait..."):
            seo_data = perform_seo_audit(url_input)
        
        if "Error" in seo_data:
            st.error(seo_data["Error"])
        else:
            st.success("✅ Audit complete! Report ready.")
            
            with st.expander("🔍 Show Audit Summary"):
                for key, value in seo_data.items():
                    if isinstance(value, list) and value:
                        st.markdown(f"**{key}**:")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{key}**: {value}")

            # Create Word document
            word_doc = create_word_report(seo_data)
            doc_stream = BytesIO()
            word_doc.save(doc_stream)
            doc_stream.seek(0)
            
            st.download_button(
                label="📄 Download SEO Report (Word)",
                data=doc_stream,
                file_name=f"seo_report_{url_input.split('//')[-1].split('/')[0]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("⚠️ Please enter a valid URL.")

# ------------------- GEMINI SETUP -------------------
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ Missing API key! Add GEMINI_API_KEY in .env file.")
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)

# ------------------- CHATBOT UI -------------------
st.subheader("💬 Gemini AI Chatbot")

# Sidebar options
with st.sidebar:
    st.title("⚙️ Chat Settings")
    model_choice = st.selectbox("Model", ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"])
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
    else:
        st.markdown('<style> .stApp { background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%); } </style>', unsafe_allow_html=True)
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
    st.caption("Powered by Collab Softech")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel(model_choice)
        chat_history = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in st.session_state.messages[:-1]]
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt)
        ai_reply = response.text

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(ai_reply)

        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        st.error(f"⚠️ Oops! {e}")

# Footer
st.markdown('<div style="text-align:center; padding:20px; color:white; background:#764ba2;">© 2025 Collab Softech AI Chatbot App</div>', unsafe_allow_html=True)