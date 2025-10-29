# chatbot.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# ------------------- Setup -------------------

# Suppress unnecessary warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Load API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file!")
    print("👉 Please add it like this: GEMINI_API_KEY=your_api_key_here")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

# ------------------- Model Setup -------------------

# Use the latest supported models
# Options: "gemini-1.5-flash-latest" or "gemini-1.5-pro-latest"
MODEL_NAME = "gemini-1.5-flash-latest"

try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"⚠️ Failed to initialize model '{MODEL_NAME}': {e}")
    exit(1)

# Start a chat session
chat = model.start_chat(history=[
    {"role": "user", "parts": [{"text": "You are a friendly and helpful AI assistant."}]}
])

print("🤖 Gemini AI Chatbot is ready!")
print("Type your message below (or 'quit' to exit):\n")

# ------------------- Chat Loop -------------------

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
        if "API key" in str(e):
            print("💡 Hint: Your API key might be expired or invalid. Check your .env file.")