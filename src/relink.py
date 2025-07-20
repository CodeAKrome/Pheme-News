#!/usr/bin/env python

import sys
import re

# id2link tab delim id, link, src, bval, bias
# bug = True enables debug mode

bug = False

id2link = sys.argv[1]
infile = sys.argv[2] if len(sys.argv) > 2 else None
dex = {}

# print(f"Reading id2link file: {id2link}", file=sys.stderr)

# Load rest of data , link by article id
with open(id2link, "r") as f:
    for line in f:
        if not line:
            continue

        #        print(f"-> {line}", file=sys.stderr, end='')

        line = line.strip()
        try:
            id, link, src, bval, bias, bbias, bdeg = line.split("\t")
        except ValueError:
            sys.stderr.write(f"retry 5: {line}\n")

            try:
                id, link, src, bval, bias = line.split("\t")
                bbias = "NA"
                bdeg = "NA"
            except ValueError:
                sys.stderr.write(f"retry 3: {line}\n")

                try:
                    id, link, src = line.split("\t")
                    bval = "NA"
                    bias = "NA"
                    bbias = "NA"
                    bdeg = "NA"
                except ValueError:                
                    sys.stderr.write(f"Retry 3 failed, dropping: {line}\n")
                    continue

        id = int(id)
        link = link.strip()
        src = src.strip()
        dex[id] = (link, src, bval, bias, bbias, bdeg)
        # if bug:
        #     print(f"=>\t{id}\t{link}\t{src}\t{bval}\t{bias}", file=sys.stderr)

# - **1412**: Africa: Former Mauritanian Finance Minister Tah Elected President of AfDB
# - *3958* Biden: We are making some real progress on Gaza deal
cite = re.compile(r"^- \*(\d+)\* (.*)$")
hyphen = re.compile(r"^-")

# head = re.compile(r"^#")
# buf = []
good = 0
bad = 0
tot = 0
dupe = 0
ids = set()
bhyph = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    tot += 1
    if bug:
        print(f"-> {tot}\t{line}")

    hmatch = hyphen.match(line)
    if hmatch:
        m = cite.match(line)
        if not m:
            bhyph += 1
            if bug:
                print(f"Bad hyphen {bhyph} {line}\n")
            continue

        id = int(m.group(1))

        if bug:
            print(f"ID: {id}\n")

        if id in ids:
            dupe += 1
            if bug:
                print(f"Dup {dupe} {id}\n")
            continue

        ids.add(id)

        if not id in dex:
            bad += 1
            if bug:
                print(f"{bad} {id} not in dex\n")
            continue
        link, src, bval, bias, bbias, bdeg = dex[id]
        # buf.append(id)
        # h = head.match(line)

        # print(dir(h))

        # if h:
        #     print("\n```\n" + ','.join(buf) + "\n```\n")
        #     buf = []
        good += 1
        print(
            f"- *{id}* [{m.group(2)}]({link}) *{src}* **{bias[:3]} {bval} {bdeg} {bbias}**"
        )
    else:
        print(line)
if tot:
    perc = good / tot
    sys.stderr.write(
        f'{{"infile": "{infile}", "perc": {perc:.2f}, "tot": {tot}, "good": {good}, "bad": {bad}, "dupe": {dupe}, "bhyph": {bhyph}}}\n'
    )
    sys.exit(0)
sys.stderr.write("No valid lines found.\n")
sys.exit(1)
