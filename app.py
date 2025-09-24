# app.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from word_report import perform_seo_audit, create_word_report
from io import BytesIO

# --- Streamlit Page Config (only once!) ---
st.set_page_config(
    page_title="AI SEO Auditor & Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #EEAECA 0%, #94BBE9 100%); }
.stTextInput>div>div>input { background-color: #fff; border-radius: 10px; border: 1px solid #ccc; padding: 10px; }
.stButton>button { background-color: #007bff; color: white; border-radius: 10px; border: none; padding: 10px 20px; }
.stExpander { background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; }
.stChatMessage { background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin: 5px 0; }
.user { background-color: #007bff; color: white; }
.ai { background-color: #e9ecef; color: black; }
.main-footer { text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("AI Chatbot with SEO Audit")
st.markdown("Enter a website URL below to get an on-page SEO audit report in a Word document.")

# --- URL Input ---
url_input = st.text_input("Website URL", placeholder="https://example.com", key="url_input")

# --- Generate SEO Report Button ---
if st.button("Generate SEO Report", key="generate_seo_report"):
    if not url_input:
        st.warning("Please enter a URL to start the audit.")
    else:
        with st.spinner("Performing SEO audit... This may take a moment."):
            seo_data = perform_seo_audit(url_input)
        
        if "Error" in seo_data:
            st.error(seo_data["Error"])
        else:
            st.success("Audit complete!")

            # --- Audit Summary ---
            with st.expander("Audit Summary"):
                for key, value in seo_data.items():
                    if isinstance(value, list) and value:
                        st.markdown(f"**{key}**:")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{key}**: {value}")

            # --- Generate Word Report ---
            word_doc = create_word_report(seo_data)
            doc_stream = BytesIO()
            word_doc.save(doc_stream)
            doc_stream.seek(0)

            st.download_button(
                label="Download SEO Report (Word)",
                data=doc_stream,
                file_name=f"seo_report_{url_input.split('//')[-1].split('/')[0]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_word"
            )

# --- Suppress Warnings ---
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Error: Add your Gemini API key to .env file or Streamlit Cloud secrets!")
    st.stop()
genai.configure(api_key=api_key)

# --- Sidebar for Chatbot ---
with st.sidebar:
    st.title("🤖 Chat Settings")
    st.markdown("---")
    model_choice = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"], key="model_choice")
    theme = st.selectbox("Theme", ["Light", "Dark"], key="theme_choice")
    if theme == "Dark":
        st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
    else:
        st.markdown('<style> .stApp { background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%); } </style>', unsafe_allow_html=True)
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.messages = []
    st.markdown("---")
    st.caption("Powered by Collab Softech")

# --- Initialize Chat Session ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"]=="user" else "🤖"):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Type your message here...", key="chat_input"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            model = genai.GenerativeModel(model_choice)
            chat_history = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in st.session_state.messages[:-1]]
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt, stream=False)
            ai_reply = response.text
            st.markdown(ai_reply)
            st.session_state.messages.append({"role":"assistant","content":ai_reply})
        except Exception as e:
            st.error(f"Oops! Error: {e}")

# --- Footer ---
st.markdown('<div class="main-footer">© 2025 Collab Softech AI Chatbot App</div>', unsafe_allow_html=True)