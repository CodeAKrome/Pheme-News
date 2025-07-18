#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove repeated string from text field and make sure it is a certain minimum length.
"""

import sys
import json
import re

min_length = 128
killfile = None

nospace = re.compile(r"\s+", re.IGNORECASE)

if len(sys.argv) > 1:
    killfile = sys.argv[1]
    if len(sys.argv) > 2:
        min_length = int(sys.argv[2])

killwords = []

try:
    with open(killfile, "r", encoding="utf-8") as f:
        for line in f:
            pat = line.strip()
            killwords.append(re.compile(pat, re.IGNORECASE))

except FileNotFoundError:
    print(f"Error: Killfile not found at '{killfile}'", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error reading killfile '{killfile}': {e}", file=sys.stderr)
    sys.exit(1)

for line_num, line in enumerate(sys.stdin, 1):
    try:
        record = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON on line {line_num}: {e}", file=sys.stderr)
        print(f"Skipping line: {line.strip()}", file=sys.stderr)
        continue

    original_text = record.get("text")
    l = len(original_text)

    if l < min_length:
        print(
            f"shorty: {l} {record['source']} {record['id']}: {original_text}",
            file=sys.stderr,
        )
        continue

    text = original_text
    for killpat in killwords:
        text = killpat.sub("", text)

    text = nospace.sub(" ", text)  # Replace multiple spaces with a single space
    text = text.strip()

    l = len(text)

    if l < min_length:
        print(
            f"shorty: {l} {record['source']} {record['id']}: {original_text}",
            file=sys.stderr,
        )
        continue

    record["text"] = text.strip()
    print(json.dumps(record))
