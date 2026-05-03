import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyByAlVSBgR6zoId8M7gOOeh_5YRHbyieoo"
genai.configure(api_key=GEMINI_API_KEY)

models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro", "gemini-2.0-flash", "gemini-2.5-flash"]

for model_name in models:
    try:
        print(f"Testing {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"SUCCESS with {model_name}: {response.text.strip()}")
        break
    except Exception as e:
        print(f"FAILED with {model_name}: {e}")
