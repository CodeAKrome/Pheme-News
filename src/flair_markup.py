from json import loads, dumps, JSONDecodeError
import sys
import re


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
        callback(data)


def convert(data):
    markup = ""
    for rec in data["ner"]:
        sent = rec["sentence"]
        reps = {}

        for span in rec["spans"]:
            txt = span["text"]
            cat = span["value"]

            key = cat + txt
            if key in reps:
                continue
            reps[key] = True

            #            pat = r'\b' + re.escape(txt) + r'\b'
            pat = re.escape(txt)
            rep = f"<{cat}>{txt}</{cat}>"
            sent = re.sub(pat, rep, sent)
        markup += sent
    #        print(f">>{sent}\n")

    data["markup"] = markup
    print(dumps(data))


if __name__ == "__main__":
    readstd(convert)
