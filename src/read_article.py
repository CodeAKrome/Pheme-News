#!env python3
import fileinput
import json
from lib.decor import arrest, log_error
from lib.curling import gurl
from lib.chowda import ps
from lib.toolbox import jloads
from lib.cash import rcache, wcache, ccache
import re

"""Pull RSS articles from 'link' entries"""

OUTPUT_DIRECTORY = "/home/kyle/srcLocal/data/art/"


import csv


def save_dicts_to_csv(dicts, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(dicts[0].keys()))
        writer.writeheader()
        for dict in dicts:
            writer.writerow(dict)


def write_file(data: dict):
    subject = re.sub(r"\W", "", data["title"])[:32]
    timestamp = "".join(map(lambda x: str(x), data["published_parsed"]))
    filename = (
        OUTPUT_DIRECTORY + data["source_id"] + "_" + timestamp + "_" + subject + ".json"
    )

    # print(f"\n->{filename}\n{data}\n--\n")

    with open(filename, "w") as fh:
        json.dump(data, fh)


@arrest([TypeError], "I love trash -- Oscar T. Grouch.")
def read():
    for line in fileinput.input():
        # print(f"<- {line}")
        try:
            rec = jloads(line)
            if rec["type"] != "art":
                print(line.strip())
            else:
                try:
                    lnk = rec["link"]
                    if lnk in cache:
                        log_error(f"Cache:\t{lnk}")
                        continue
                    doc = gurl(lnk, {})
                    doc = ps(doc)
                    rec["text"] = doc

                    print(json.dumps(rec))
                    # write_file(rec)

                    ccache(lnk, cache)
                except Exception as e:
                    log_error(f"Dropped on floor: {rec['link']} [{e}]")
        except Exception as e:
            log_error(f"Blank or malformed line. {e} '{line}'")


if __name__ == "__main__":
    cache = rcache()
    read()
    wcache(cache)
