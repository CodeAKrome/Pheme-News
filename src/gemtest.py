#!/usr/bin/env python
import google.generativeai as genai
import sys
import os

DEFAULT_MODEL = "gemini-2.0-flash-thinking-exp-1219"
DEFAULT_MODEL = "gemini-2.5-flash-preview-04-17"

modelname = DEFAULT_MODEL

if len(sys.argv) > 1:
    modelname = sys.argv[1]
    
sys.stderr.write(f"model: {modelname}\n")

# Ensure the GEMINI_API_KEY environment variable is set
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)
    
# Configure the API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(modelname)

buf = []

for line in sys.stdin:
    if not line:
        continue
    buf.append(line)
    
prompt = "".join(buf)    
response = model.generate_content(prompt)
print(response.text)

