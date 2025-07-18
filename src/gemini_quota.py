#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch the rate limit for a Gemini model using the Gemini API.
"""

import google.generativeai as genai
import requests
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
MODEL   = "gemini-2.5-pro"            # or gemini-2.5-pro-preview-06-05
MODEL   = "gemini-2.5-flash"            # or gemini-2.5-pro-preview-06-05

# ------------------------------------------------------------------
# 1.  Authenticate
# ------------------------------------------------------------------
# genai.configure(api_key=API_KEY)

# ------------------------------------------------------------------
# 2.  Grab the headers returned by the *first* OPTIONS call
#     which contains X-RateLimit-* headers
# ------------------------------------------------------------------
endpoint = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent?key={API_KEY}"
)

r = requests.options(endpoint)
rlimit = r.headers

print("Gemini API (AI Studio) rate limit for", MODEL)
print("  Limit (req/min) :", rlimit.get("X-RateLimit-Limit"))
print("  Remaining       :", rlimit.get("X-RateLimit-Remaining"))
print("  Reset (UTC)     :", rlimit.get("X-RateLimit-Reset"))