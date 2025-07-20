#!/usr/bin/env python

import sys
import subprocess
import json

# add summaries and generate the TTS jsonl

# extract ids records from jsonl and do summaries
# model infile promptfile soundid

cmd = []
trig = -1
sound = []
sumcnt = 0


def runcmd(command):
    """Execute command using subprocess.run()"""
    global sumcnt
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        # print(f"Command: {command}")
        # print(f"Return code: {result.returncode}")
        # print(f"Output: {result.stdout}")

        # model prints to stderr, don't show it
        # if result.stderr:
        #     print(f"{sumcnt}: {result.stderr}", file=sys.stderr)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error executing command: {e}")


# -----

if len(sys.argv) > 3:
    model = sys.argv[1]
    infile = sys.argv[2]
    promptfile = sys.argv[3]
    soundid = sys.argv[4]
else:
    sys.exit(1)

for line in sys.stdin:
    if not line:
        continue

    # print(f"{trig}\t{line}", end='')
    print(line, end="")

    if trig == 1:
        
        # sys.stderr.write(f"trig: {line.strip()}\n")
        
        cmd.append(
            f"cat {infile} | jq 'select(.id | IN({line.strip()}))' | jq '[.text]' | src/gemtest.py {model} {promptfile}"
        )
    if line[0] == "`":
        trig = trig * -1

        # print(f"Trigger: {trig} cmd: {cmd}")

        if trig == -1:

            # sys.stderr.write(f"cmd: {cmd[0]}\n")

            summary = runcmd(cmd[0])
            soundfile = f"{sumcnt:02d}-{soundid}"
            print(f"[mp3 summary]({soundfile}.mp3)")
            print(summary)
            print()
            sound.append({"id": soundfile, "text": summary})
            sumcnt += 1
            # print(cmd[0])
            cmd = []

        continue


for ent in sound:
    print(json.dumps(ent), file=sys.stderr)

# print(f"Total summaries: {sumcnt}", file=sys.stderr)
