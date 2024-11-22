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

deadlines = defaultdict(lambda:[]) # This will be cached to use after the first article time through
last_src = False    

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
        continue

    src = data['source']
    if last_src:
        if src != last_src:
            init = True
            last_src = src
            dedupe = []
    else:
        last_src = src
        dedupe = []
        init = True # Flag to determine whether we are on the first article or not.
    
    for sentence in data['ner']:
        sent = sentence['sentence']
        alpha_sent = alphanumeric(sent)
        if init:
            dedupe.append(alpha_sent)
        else:
            if alpha_sent in dedupe:
                if alpha_sent not in deadlines[src]:
                    deadlines[src].append(alpha_sent)

    # Finished with sentences
    # dedupe should be full now.
    if init:
        init = False

with open(DUPEFILE, "w") as dfh:
    print(dumps(deadlines), file=dfh)

print("Duplicate lines by source\n=======\n")
for src in deadlines:
    print(f"{src}\t{len(deadlines[src])}")
    
