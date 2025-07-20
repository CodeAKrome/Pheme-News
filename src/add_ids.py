#!/usr/bin/env python3

"""
Add unique IDs to each JSON object in a JSON Lines file.
Reads from standard input and writes to standard output.
Usage: python add_ids.py <STARTING_ID>
"""

import json
import sys
from typing import TextIO


def add_ids(infile: TextIO, outfile: TextIO, start_id: int) -> None:
    next_id = start_id
    for line in infile:
        line = line.rstrip("\n")
        if not line:  # skip empty lines
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            # Write diagnostic to stderr so output stays valid JSONL
            print(f"Invalid JSON: {e}", file=sys.stderr)
            continue

        obj["id"] = next_id
        next_id += 1
        json.dump(obj, outfile, ensure_ascii=False)
        outfile.write("\n")


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <STARTING_ID>", file=sys.stderr)
        sys.exit(1)

    try:
        start_id = int(argv[1])
    except ValueError:
        print("STARTING_ID must be an integer", file=sys.stderr)
        sys.exit(1)

    add_ids(sys.stdin, sys.stdout, start_id)


if __name__ == "__main__":
    main(sys.argv)
