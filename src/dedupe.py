import sys
import re
from collections import defaultdict
from json import loads, dumps, JSONDecodeError

"""Remove duplicate sentences by comparing to sentences in the previous article. No text field -> passthrough."""

DUPEFILE = "cache/dupes.json"
PATTERN = re.compile(r"[^a-zA-Z0-9]")

def alphanumeric(text):
    return PATTERN.sub("", text)

dfh = open(DUPEFILE, "w")
deadlines = defaultdict(lambda:[]) # This will be cached to use after the first article time through
dedupe = {}
dedupe_init = True
   
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        data = loads(line)
    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue
    # This should mean this is an rss flavored record
    if not 'ner' in data:
        print(line)
        continue

    src = data['source']
    dupe_count = 0
    clean_ner = []
    buf = {}

    for sentence in data['ner']:
        sent = sentence['sentence']
        alpha_sent = alphanumeric(sent)

        if alpha_sent in dedupe:
            dupe_count += 1
            print(f"DROP\t{src}\t{sent}", file=sys.stderr)
            deadlines[src].append(alpha_sent)
            continue

        if dedupe_init:
            dedupe[alpha_sent] = True

        clean_ner.append(sent)
        buf[alpha_sent] = True

    # Finished with sentences
    if dedupe_init:
        # dedupe should be full now.
        dedupe_init = False
    else:
    # If we haven't seen any dupes and we didn't just fill it, swap in current buffer data
        if dupe_count == 0:
            dedupe = buf

    data['ner'] = clean_ner
    print(dumps(data))
print(dumps(deadlines), file=dfh)
