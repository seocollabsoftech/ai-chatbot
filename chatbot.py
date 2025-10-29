# chatbot.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Suppress unnecessary warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

# ✅ Use the latest available model from your list
MODEL_NAME = "models/gemini-2.5-flash"  # Fast and latest stable version

try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"✅ Using model: {MODEL_NAME}")
except Exception as e:
    print(f"⚠️ Error loading model '{MODEL_NAME}': {e}")
    print("💡 Try 'models/gemini-2.5-pro' instead.")
    exit(1)

# Start chat
chat = model.start_chat(history=[
    {"role": "user", "parts": [{"text": "You are a helpful AI assistant."}]}
])

print("🤖 Gemini 2.5 Chatbot ready! Type your question below (type 'quit' to exit)\n")

# Chat loop
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Goodbye!")
        break
    if not user_input:
        continue
    try:
        response = chat.send_message(user_input)
        print(f"AI: {response.text}\n")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")