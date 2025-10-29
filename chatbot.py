import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Suppress ALTS-related warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: Add your GEMINI_API_KEY to the .env file!")
    exit()

# Configure Gemini client
genai.configure(api_key=api_key)

# ✅ Use the latest supported model (remove 'models/' prefix)
# You can switch between: "gemini-1.5-flash" or "gemini-1.5-pro"
model = genai.GenerativeModel("gemini-1.5-flash")

# Start chat session
chat = model.start_chat(history=[
    {"role": "user", "parts": [{"text": "You are a helpful AI assistant."}]}
])

print("🤖 Gemini AI Chatbot ready! Type 'quit' to exit.\n")

# Main loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Goodbye!")
        break

    try:
        # Generate AI response
        response = chat.send_message(user_input)
        print(f"AI: {response.text}\n")
    except Exception as e:
        print(f"⚠️ Error: {e}\n")