import google.generativeai as genai
import toml

# Load secrets
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets = toml.load(f)
    api_key = secrets.get("GOOGLE_API_KEY")
    if not api_key:
        print("API Key not found in .streamlit/secrets.toml")
        exit(1)
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
