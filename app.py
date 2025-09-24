# app.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
# Import the functions from the new file
from word_report import perform_seo_audit, create_word_report
from io import BytesIO

# --- Streamlit UI ---
import streamlit as st
from word_report import perform_seo_audit, create_word_report
from io import BytesIO

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="AI SEO Auditor",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Chatbot with SEO Audit")
st.markdown("Enter a website URL to get an on-page SEO audit report in a Word document.")

# --- URL Input ---
url_input = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Generate SEO Report"):
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
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# Custom CSS for a beautiful look
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
st.markdown("Enter a website URL below to get an on-page SEO audit report in a Word document.")

# Input for URL
url_input = st.text_input("Website URL", placeholder="e.g., https://streamlit.io")

# Button to trigger the audit
if st.button("Generate SEO Report"):
    if url_input:
        with st.spinner("Analyzing website... This may take a moment."):
            seo_data = perform_seo_audit(url_input)
        
        if "Error" in seo_data:
            st.error(seo_data["Error"])
        else:
            st.success("Audit complete! Report generated.")
            
            # Use an expander to show a summary of the findings
            with st.expander("Show Audit Summary"):
                st.write("Here is a quick overview of the findings:")
                for key, value in seo_data.items():
                    if isinstance(value, list) and value:
                        st.markdown(f"**{key}**:")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{key}**: {value}")

            # Generate and download the Word document
            word_doc = create_word_report(seo_data)
            
            # Save the document to a byte stream to make it downloadable
            doc_stream = BytesIO()
            word_doc.save(doc_stream)
            doc_stream.seek(0)
            
            # Create a download button
            st.download_button(
                label="Download SEO Report (Word)",
                data=doc_stream,
                file_name=f"seo_report_{url_input.split('//')[-1].split('/')[0]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Please enter a URL to start the audit.")

# Suppress ALTS warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables (local .env or Streamlit Cloud secrets)
load_dotenv()

# Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Error: Add your Gemini API key to .env file or Streamlit Cloud secrets!")
    st.stop()
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit page config for beautiful layout
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design
st.markdown("""
    <style>
    .stChatMessage { background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin: 5px 0; }
    .user { background-color: #007bff; color: white; }
    .ai { background-color: #e9ecef; color: black; }
    .main-footer { text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
""", unsafe_allow_html=True)

# Theme toggle in sidebar
with st.sidebar:
    st.title("🤖 Chat Settings")
    st.markdown("---")
    model_choice = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
    else:
        st.markdown('<style> .stApp { background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%); } </style>', unsafe_allow_html=True)
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
    st.markdown("---")
    st.caption("Powered by Collab Softech")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant", avatar="🤖"):
        try:
            # Use selected model
            model = genai.GenerativeModel(model_choice)
            # Recreate chat with history
            chat_history = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in st.session_state.messages[:-1]]
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt, stream=False)
            ai_reply = response.text
            st.markdown(ai_reply)
            
            # Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error(f"Oops! Error: {e}")

# Footer
st.markdown('<div class="main-footer">© 2025 Collab Softech AI Chatbot App</div>', unsafe_allow_html=True)