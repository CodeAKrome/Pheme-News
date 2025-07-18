import sys
from json import loads, dumps, JSONDecodeError
from lib.flair_sentiment import FlairSentiment

"""Do targetted sentiment detection on news articles. If no text field, passthrough."""

fs = FlairSentiment()
last_source = None
data = {}

for lno, line in enumerate(sys.stdin, start=1):

    #    sys.stderr.write(f"{lno}: {line}\n===\n")

    line = line.strip()
    if not line:
        # sys.stderr.write("Blank {lno}\n")
        continue
    try:
        #        sys.stderr.write(f"Parsing {lno}: {line}\n")
        data = loads(line)

    #        sys.stderr.write(f"Parsed {lno}: {data}\n")

    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue

    #    sys.stderr.write(f"data out: {data}\n")

    # Print message when data stream switches sources
    if "source" in data:
        if last_source != data["source"]:
            sys.stderr.write(f"\nProcessing:\t{data['source']}\n\n")
            last_source = data["source"]

    if not "text" in data:
        print(line)
        #        sys.stderr.write("No text field in data, passing through.\n")
        continue

    sys.stderr.write(f"{lno}\t{data['title']}\n")

    data["ner"], data["stats"] = fs.process_text(data["text"])

    #    sys.stderr.write(f"\ndataNER {data['ner']}\n")

    print(dumps(data))
