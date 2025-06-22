import google.generativeai as genai
import os

# Configure the API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# List available models
for m in genai.list_models():
    print(m)



# python list_gemini_models.py
