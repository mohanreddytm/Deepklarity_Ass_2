from dotenv import load_dotenv
load_dotenv()

import google.genai as genai  # Correct import for new SDK
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# List available models first (optional, run once to check)
for model in client.models.list():
    print(model.name)

# Use a current stable model instead of deprecated gemini-1.0-pro
response = client.models.generate_content(
    model="gemini-2.5-flash",  # Or "gemini-2.5-pro", "gemini-flash-latest"
    contents="Say hello in one word"
)

print(response.text)
