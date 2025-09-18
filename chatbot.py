import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging  # Added for logging control

# Suppress ALTS-related warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: Add your Gemini API key to .env file!")
    exit()
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Start chat with a system-like prompt
chat = model.start_chat(history=[
    {"role": "user", "parts": [{"text": "You are a helpful AI assistant."}]}
])

print("Gemini AI Chatbot ready! Type 'quit' to exit.")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    try:
        # Send message to Gemini
        response = chat.send_message(user_input, stream=False)
        ai_reply = response.text
        print(f"AI: {ai_reply}")
    except Exception as e:
        print(f"Error: {e}")
        continue