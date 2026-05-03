import google.generativeai as genai
import sys

GEMINI_API_KEY = "AIzaSyByAlVSBgR6zoId8M7gOOeh_5YRHbyieoo"
genai.configure(api_key=GEMINI_API_KEY)

print("Available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
