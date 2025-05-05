from json import loads, dumps, JSONDecodeError
import sys
from lib.xl8 import Xl8

i18n = Xl8()


def readstd(callback):
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
        # Nothing to xl8
        if data["lang"] == "en":
            print(line)
            continue
        callback(data)


def convert(data):
    data["orig"] = data["text"]
    data["text"], input_tokens, output_tokens = i18n.translate(
        data["text"], data["lang"], "en"
    )
    print(dumps(data))


if __name__ == "__main__":
    readstd(convert)
