import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Suppress ALTS-related warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: Add your Gemini API key to the .env file!")
    exit()

# Configure Gemini client
genai.configure(api_key=api_key)

# ✅ Use the latest supported model
# Options: "models/gemini-pro-latest" or "gemini-1.5-flash-latest"
model = genai.GenerativeModel("models/gemini-pro-latest")

# Start a new chat session with initial instruction
chat = model.start_chat(history=[
    {"role": "user", "parts": [{"text": "You are a helpful AI assistant."}]}
])

print("🤖 Gemini AI Chatbot ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Goodbye!")
        break

    try:
        # Generate response
        response = chat.send_message(user_input)
        print(f"AI: {response.text}\n")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")