import sys
from json import loads, dumps, JSONDecodeError
from lib.flair_sentiment import FlairSentiment

"""Do targetted sentiment detection on news articles. If no text field, passthrough."""

fs = FlairSentiment()
   
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        data = loads(line)
    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue
    if not 'text' in data:
        print(line)
        continue
    data["ner"] = fs.process_text(data["text"])
    print(dumps(data))
    