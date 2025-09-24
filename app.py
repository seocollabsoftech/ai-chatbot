# app.py

import streamlit as st
import os
from dotenv import load_dotenv
import logging
from io import BytesIO
from urllib.parse import urlparse

# Import audit functions
from word_report import perform_seo_audit, create_word_report, capture_screenshot

# Optional: import google generative ai if available for AI suggestions
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

# --- Streamlit UI ---
st.set_page_config(
    page_title="AI Chatbot & SEO Auditor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #EEAECA 0%, #94BBE9 100%); }
    .stTextInput>div>div>input { background-color: #fff; border-radius: 10px; border: 1px solid #ccc; padding: 10px; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 10px; border: none; padding: 10px 20px; }
    .stExpander { background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; }
    .stChatMessage { background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin: 5px 0; }
    .main-footer { text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("AI Chatbot with SEO Audit")
st.markdown("Enter a website URL below to get an on-page SEO audit report in a Word document.")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_client = None
if GENAI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        ai_client = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        ai_client = None

if not GEMINI_API_KEY:
    st.info("Gemini API key not found. AI suggestions in the report will be disabled. (Optional)")

# Input
url_input = st.text_input("Website URL", placeholder="e.g., https://streamlit.io")

if st.button("Generate SEO Report"):
    if not url_input:
        st.warning("Please enter a URL to start the audit.")
    else:
        with st.spinner("Analyzing website..."):
            seo_data = perform_seo_audit(url_input)

        if "Error" in seo_data:
            st.error(seo_data["Error"])
        else:
            st.success("Audit collected. Preparing Word report...")

            # Show summary
            with st.expander("Show Audit Summary"):
                st.write("Quick overview:")
                for k, v in seo_data.items():
                    if isinstance(v, list) and v:
                        st.markdown(f"**{k}**")
                        for item in v[:10]:
                            st.markdown(f"- {item}")
                    elif isinstance(v, list) and not v:
                        st.markdown(f"**{k}**: None")
                    elif isinstance(v, dict):
                        st.markdown(f"**{k}**: (structured)")
                    else:
                        st.markdown(f"**{k}**: {v}")

            # Try to capture screenshot (optional)
            screenshot_bytes = None
            try:
                with st.spinner("Capturing screenshot (if supported)..."):
                    screenshot_bytes = capture_screenshot(seo_data.get("Final URL", url_input))
            except Exception as e:
                # Show a non-fatal warning
                st.warning(f"Screenshot not captured: {e}")

            # Create Word doc in-memory
            doc_stream = BytesIO()
            # create_word_report writes into the stream when passed
            create_word_report(seo_data, doc_stream, screenshot_bytes=screenshot_bytes, ai_client=ai_client)
            doc_stream.seek(0)

            # Offer download
            filename = f"seo_report_{urlparse(url_input).netloc}.docx"
            st.download_button(
                label="Download SEO Report (Word)",
                data=doc_stream,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# --- Chat / Gemini UI (kept minimal here) ---
# NOTE: Chat features remain similar to your earlier code; we keep them simple here.

st.markdown("---")
st.markdown("## Chat (Gemini) — use sidebar to configure model")

# Sidebar
with st.sidebar:
    st.title("🤖 Chat Settings")
    st.markdown("---")
    if GENAI_AVAILABLE:
        model_choice = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    else:
        st.write("Gemini SDK not available.")
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
    else:
        st.markdown('<style> .stApp { background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%); } </style>', unsafe_allow_html=True)
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
    st.markdown("---")
    st.caption("Powered by Collab Softech")

# Simple chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    role = m.get("role", "user")
    with st.chat_message(role):
        st.markdown(m.get("content", ""))

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        if ai_client:
            try:
                # create minimal chat request
                model = genai.GenerativeModel("gemini-1.5-flash")
                chat = model.start_chat()
                resp = chat.send_message(prompt, stream=False)
                reply = resp.text
            except Exception as e:
                reply = f"AI error: {e}"
        else:
            reply = "AI not configured (GEMINI_API_KEY missing or SDK unavailable)."

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Footer
st.markdown('<div class="main-footer">© 2025 Collab Softech AI Chatbot App</div>', unsafe_allow_html=True)