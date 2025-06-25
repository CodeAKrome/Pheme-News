#!/usr/bin/env python

import sys
import re

id2link = sys.argv[1]
infile = sys.argv[2] if len(sys.argv) > 2 else None
dex = {}

with open(id2link, "r") as f:
    for line in f:
        line = line.strip()
        id, link, src, bval, bias = line.split("\t")
        id = int(id)
        link = link.strip()
        src = src.strip()
        dex[id] = (link, src)

# - **1412**: Africa: Former Mauritanian Finance Minister Tah Elected President of AfDB
#- *3958* Biden: We are making some real progress on Gaza deal
cite = re.compile(r"^- \*(\d+)\* (.*)$")
hyphen = re.compile(r"^-")

#head = re.compile(r"^#")
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
    hmatch = hyphen.match(line)
    if hmatch:
        m = cite.match(line)
        if not m:
            # sys.stderr.write(f"Bad hyphen line: {line}\n")
            bhyph += 1
            continue            
    
        id = int(m.group(1))
        
        if id in ids:
            dupe += 1
            # sys.stderr.write(f"Dup {id}\n")
            continue

        ids.add(id)
        
        if not id in dex:
            bad += 1
            # perc = good / tot
            # sys.stderr.write(f"<-{id} {perc:.2f} {tot} {good} / {bad}\n")
    #        print(line)
            continue
        link, src = dex[id]
        # buf.append(id)
        # h = head.match(line)
        
        # print(dir(h))
            
        # if h:
        #     print("\n```\n" + ','.join(buf) + "\n```\n")
        #     buf = []
        good += 1
        print(f"- *{id}* [{m.group(2)}]({link}) *{src}* **{bias[:3]} {bval}**")
    else:
        print(line)
if tot:        
    perc = good / tot
    sys.stderr.write(f"{{\"infile\": \"{infile}\", \"perc\": {perc:.2f}, \"tot\": {tot}, \"good\": {good}, \"bad\": {bad}, \"dupe\": {dupe}, \"bhyph\": {bhyph}}}\n")
    sys.exit(0)
sys.stderr.write("No valid lines found.\n")
sys.exit(1)