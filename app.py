import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json
json.dump(st.session_state.messages, open("chat_history.json", "w"))

st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    </style>
    """,
    unsafe_allow_html=True
)
with st.chat_message("user", avatar="👤"):
    st.markdown(prompt)
with st.chat_message("assistant", avatar="🤖"):
    st.markdown(ai_reply)
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
# Suppress ALTS warnings (from your previous fix)
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Error: Add your Gemini API key to .env file!")
    st.stop()
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit page config for beautiful layout
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖",
    layout="wide",  # Full-width layout
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design (add gradients, shadows, etc.)
st.markdown("""
    <style>
    .stChatMessage { background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin: 5px 0; }
    .user { background-color: #007bff; color: white; }
    .ai { background-color: #e9ecef; color: black; }
    .main-footer { text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
""", unsafe_allow_html=True)

# Sidebar for settings (beautiful collapsible)
with st.sidebar:
    st.title("🤖 Chat Settings")
    st.markdown("---")
    model_choice = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
    st.markdown("---")
    st.caption("Powered by Google Gemini")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        try:
            # Start a new chat if no history, or continue
            if not st.session_state.messages:
                chat = model.start_chat()
            else:
                # For simplicity, recreate chat with history (Gemini supports up to 1M tokens)
                chat_history = [{"role": msg["role"], "parts": [msg["content"]]} for msg in st.session_state.messages[:-1]]  # Exclude last user msg
                chat = model.start_chat(history=chat_history)
            
            response = chat.send_message(prompt, stream=False)
            ai_reply = response.text
            st.markdown(ai_reply)
            
            # Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error(f"Oops! Error: {e}")

# Footer for polish
st.markdown('<div class="main-footer">© 2025 Your AI Chatbot App</div>', unsafe_allow_html=True)