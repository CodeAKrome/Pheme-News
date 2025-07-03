#!/usr/bin/env python

import google.generativeai as genai
import sys
import os
import google.auth

DEFAULT_MODEL = "gemini-2.5-pro"

def main():
    """
    Uses Gemini AI to answer a prompt from a file with data from stdin.
    Mimics the behavior of gemtest.py.

    Usage:
        python ask_gemini.py [model] [promptfile] < stdin
    """
    # To use your Google ID for authentication, run the following command in your terminal:
    # gcloud auth application-default login
    # The script will automatically use your credentials.
    # Alternatively, you can set the GEMINI_API_KEY environment variable.
    if os.environ.get("GEMINI_API_KEY"):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    else:
        try:
            credentials, _ = google.auth.default()
            genai.configure(credentials=credentials)
        except google.auth.exceptions.DefaultCredentialsError:
            # The library will still try to find credentials in other places.
            # If it fails, it will raise an exception.
            pass

    modelname = DEFAULT_MODEL
    prompt = ""
    promptfile = None

    if len(sys.argv) == 2:
        # Assume the argument is a promptfile if it exists, otherwise it's a model name
        if os.path.exists(sys.argv[1]):
            promptfile = sys.argv[1]
        else:
            modelname = sys.argv[1]
    elif len(sys.argv) > 2:
        modelname = sys.argv[1]
        promptfile = sys.argv[2]

    if promptfile:
        try:
            with open(promptfile, 'r') as f:
                prompt = f.read()
        except FileNotFoundError:
            sys.stderr.write(f"Error: Prompt file '{promptfile}' not found.\n")
            sys.exit(1)

    stdin_data = sys.stdin.read()

    full_prompt = f"{prompt}{stdin_data}"

    model = genai.GenerativeModel(modelname)
    response = model.generate_content(full_prompt)
    print(response.text)

if __name__ == "__main__":
    main()
