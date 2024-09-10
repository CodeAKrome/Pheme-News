#!/usr/bin/env python3

from json import loads, JSONDecodeError
from lib.flair_sentiment import FlairSentiment
import sys

# from icecream import ic


def main():
    # ic.configureOutput(outputFunction=lambda *a: sys.stdout.write(ic(*a)))
    id = 0
    sentiment_analyzer = FlairSentiment()
    for line in sys.stdin:
        id += 1
        record = line.strip()
        if record:
            try:
                data = loads(record)
            except JSONDecodeError as e:
                sys.stderr.write(f"Error parsing JSON: {e}\n")
            ner = sentiment_analyzer.process_text(data["text"])
            print(f"{id}\n{dir(ner)}\n")


#            ic(ner)

if __name__ == "__main__":
    main()
