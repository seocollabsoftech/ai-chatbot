# list_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

print("🔍 Available Gemini models that support generateContent:\n")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print("✅", m.name)