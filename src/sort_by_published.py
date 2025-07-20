#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Read JSON records from stdin, sort by `published_parsed`, and emit them in
chronological order to stdout.

Each line on stdin must be a single JSON object.  The `published_parsed`
field is assumed to be a 9-element list/tuple as returned by
`time.struct_time`, i.e.:

    [year, month, day, hour, minute, second, weekday, yearday, dst]

The script simply sorts the list of records by this tuple; Python’s tuple
comparison already yields chronological order.

Usage
-----
    cat records.jsonl | python sort_by_published.py > sorted_records.jsonl
"""

import json
import sys

def main() -> None:
    dropped = 0
    records = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # silently ignore invalid JSON

        pp = rec.get("published_parsed")
        if isinstance(pp, (list, tuple)) and len(pp) >= 6:
            records.append(rec)
        else:
            dropped += 1
        # If you want to parse a string like "2025-07-18T21:52:40Z"
        # instead of skipping, uncomment the next block:
        # elif isinstance(pp, str):
        #     import datetime, email.utils
        #     try:
        #         dt = email.utils.parsedate_to_datetime(pp)
        #         rec["published_parsed"] = list(dt.timetuple())
        #         records.append(rec)
        #     except Exception:
        #         pass

    records.sort(key=lambda r: r["published_parsed"])

    for rec in records:
        print(json.dumps(rec, ensure_ascii=False))

    sys.stderr.write(f"Dropped {dropped} records with invalid 'published_parsed' field.\n")

if __name__ == "__main__":
    main()