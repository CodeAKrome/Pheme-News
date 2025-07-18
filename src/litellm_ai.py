#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from litellm import completion
import sys
import json
import re
import time
from lib.emojify import emojify

"""
Use LiteLLM to get bias from news articles.
"""

JSON_RE = re.compile(r"(\{[^\}]+\})")
MODEL = "gemini/gemini-2.5-flash"
MODEL = "gemini/gemini-2.5-pro"
# DEFAULT_MODEL = "ollama/llama4:scout"
# DEFAULT_MODEL = "ollama/gemma3:27b"
DEFAULT_MODEL = "ollama/llama4:scout"
# DEFAULT_MODEL = "ollama/deepseek-r1:70b"
# DEFAULT_MODEL = "ollama/llama3.3:70b"
# DEFAULT_MODEL = "ollama/qwen3:8b"
# DEFAULT_MODEL = "ollama/qwen3:32b"


# init
e = emojify
model_name = DEFAULT_MODEL
location = "local"

# load emojis
emap = {
    "left": e(["reverse_button"])[0],
    "center": e(["record_button"])[0],
    "right": e(["play_button"])[0],
    "minimal": e(["right_arrow_curving_down"])[0],
    "moderate": e(["up-down_arrow"])[0],
    "strong": e(["right_arrow_curving_up"])[0],
}

if len(sys.argv) > 1:
    prompt_file = sys.argv[1]
    prompt = open(prompt_file, "r").read().strip()

    if len(sys.argv) > 2:
        model_name = sys.argv[2]
        if "gemini" in model_name:
            location = "remote"
            model = MODEL

else:
    exit("Usage: python litellm_ai.py <prompt_file> <model_name> optional")


class LapTimer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.lap_times = []

    def lap(self):
        current_time = time.perf_counter()
        lap_time = current_time - self.start_time
        self.lap_times.append(lap_time)
        self.start_time = current_time
        return lap_time

    def get_lap_times(self):
        return self.lap_times

    def get_count(self):
        return len(self.lap_times)

    def get_average_lap_time(self):
        return sum(self.lap_times) / len(self.lap_times)


timer = LapTimer()


def remote_ai(text: str, model: str = MODEL):
    """
    Remote AI function to process text and return a response.
    Google gemini for now.
    """
    response = completion(model=model, messages=[{"role": "user", "content": text}])
    return response.choices[0].message.content.strip()


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


def getbias(prompt: str, text: str, model: str) -> dict:
    """
    Function to get bias from text using a local AI model.
    """
    instring = f"{prompt}\n{text}"
    # print(f"=> Local AI: {instring}\n")

    if location == "remote":
        res = remote_ai(text=instring, model=model)
    else:
        res = local_ai(text=instring, model=model)

    lap = timer.lap()
    # sys.stderr.write(f"Lap {timer.get_count()}: {lap:.4f} sec.\n")
    # print(f"AI Response: {res}\n")

    match = JSON_RE.search(res)
    out = {
        "bias": "NA",
        "degree": "NA",
        "reason": "NA",
        "model": model,
        "lap": f"{lap:.1f}",
    }

    if match:
        data = match.group(0)
    else:
        # try to recover from bad JSON
        sys.stderr.write(f"Attempting fix:\n{res}\n")
        res = res + "}"
        match = JSON_RE.search(res)

        if match:
            data = match.group(0)
        else:
            sys.stderr.write(f"No JSON found in response, returning NA dict.\n{res}\n")
            return out
    out = json.loads(data)
    out["model"] = model
    out["lap"] = f"{lap:.1f}"
    return out


# === Main ===
source = None

for lno, line in enumerate(sys.stdin, start=1):
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)

        if "source" in data:
            if source != data["source"]:
                sys.stderr.write(f"\nProcessing:\t{data['source']}\n\n")
                source = data["source"]

        if "text" in data:
            text = data["text"]
            # print(f"-----\n{text}")
            bias = getbias(prompt, text, model_name)
            # print(f"\n{json.dumps(bias)}\n=====\n")
            data["bias"] = bias
            bdir = bias["bias"]
            deg = bias["degree"]

            sys.stderr.write(
                f"{lno} {data['id']}: {data['title']}\n{emap[bdir]} {emap[deg]} {bias['lap']}\t{bias['reason']}\n"
            )

            print(json.dumps(data))
    except Exception as e:
        sys.stderr.write(f"Error parsing line {lno}: {e}\n")
        continue

sys.stderr.write(f"Lap times: {timer.get_lap_times()}\n")
sys.stderr.write(f"Average lap time: {timer.get_average_lap_time():.4f} sec.\n")
