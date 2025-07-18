#!/usr/bin/env python

"""
Take a prompt and return a response from a local AI model.
"""

import sys
from litellm import completion

DEFAULT_MODEL = "ollama/gemma3:12b"
model = DEFAULT_MODEL

if len(sys.argv) > 1:
    model = sys.argv[1]

prompt = sys.stdin.read().strip()


def local_ai(text: str, model: str = DEFAULT_MODEL) -> str:
    """
    Local AI function to process text and return a response.
    """

    response = completion(
        model=model,
        messages=[{"content": text, "role": "user"}],
        api_base="http://localhost:11434",
    )
    return response.choices[0].message.content.strip()


print(local_ai(prompt, model))
