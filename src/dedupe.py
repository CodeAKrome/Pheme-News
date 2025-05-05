import sys
import re
from collections import defaultdict
from json import loads, dumps, JSONDecodeError

"""
Remove duplicate sentences by comparing to sentences in the previous article.
No text field -> passthrough.
'ner' must be a field since that's what we use to compare sentences.
"""

DUPEFILE = "cache/dupes.json"
PATTERN = re.compile(r"[^a-zA-Z0-9]")


def alphanumeric(text):
    return PATTERN.sub("", text)


try:
    with open(DUPEFILE, "r") as dfh:
        deadlines = loads(dfh.read())
except FileNotFoundError as e:
    print(f"Missing: {DUPEFILE}\n{e}\n", file=sys.stderr)
    exit(1)
except JSONDecodeError as e:
    sys.stderr.write(f"JSONload error {DUPEFILE} file: {e}\n")
    exit(1)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        data = loads(line)
    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue
    # This should mean this is an rss flavored record
    if not "ner" in data:
        print(line)
        continue

    src = data["source"]
    clean_ner = []
    try:
        dedupe = deadlines[src]
    except KeyError:
        sys.stderr.write(f"Missing source {src} in dedupe cache.\n")
        dedupe = []

    for sentence in data["ner"]:
        sent = sentence["sentence"]
        alpha_sent = alphanumeric(sent)

        if alpha_sent in dedupe:
            print(f"DROP\t{src}\t{sent}", file=sys.stderr)
            continue

        clean_ner.append(sentence)

    # Sentences done
    data["ner"] = clean_ner
    print(dumps(data))
