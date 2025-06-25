#!/usr/bin/env python
import google.generativeai as genai
import sys
import os

# modelname promptfile

DEFAULT_MODEL = "gemini-2.0-flash-thinking-exp-1219"
DEFAULT_MODEL = "gemini-2.5-flash-preview-04-17"

# Ensure the GEMINI_API_KEY environment variable is set
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)
    
# Configure the API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

modelname = DEFAULT_MODEL
prompt = ""

if len(sys.argv) > 2:
    modelname = sys.argv[1]
    promptfile = sys.argv[2]
    try:
        with open(promptfile, 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: Prompt file '{promptfile}' not found.\n")
        sys.exit(1)
else:
    if len(sys.argv) > 1:
        modelname = sys.argv[1]
 
# quiet   
#sys.stderr.write(f"model: {modelname}\n")

model = genai.GenerativeModel(modelname)
buf = []

for line in sys.stdin:
    if not line:
        continue
    buf.append(line)
    
prompt += "".join(buf)    
response = model.generate_content(prompt)
print(response.text)

