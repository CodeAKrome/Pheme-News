#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bulk-load JSON-lines from stdin into a local MongoDB database.

Usage:
    cat file.jsonl | python jsonl2mongo.py mydb
"""

import json, sys
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.operations import IndexModel

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python jsonl2mongo.py <database_name>")

    # connect
    client = MongoClient("mongodb://localhost:27017")
    db = client[sys.argv[1]]
    col = db["articles"]

    # --- create indexes only once ---
    if "id_1" not in col.index_information():                 # single-field
        col.create_index("id", unique=True)

    compound_name = "ner.spans.text_text_ner.spans.value_text"
    if compound_name not in col.index_information():          # text index
        col.create_index(
            [("ner.spans.text", TEXT), ("ner.spans.value", TEXT)]
        )

    # --- bulk-insert ---
    docs = (json.loads(l) for l in sys.stdin if l.strip())
    try:
        from pymongo.errors import BulkWriteError
        col.insert_many(docs, ordered=False)
    except BulkWriteError as bwe:
        # duplicates on 'id' are ignored; other errors are printed
        for err in bwe.details["writeErrors"]:
            if err["code"] != 11000:
                print(err, file=sys.stderr)

    print("✓ Finished inserting into MongoDB database '{}'".format(sys.argv[1]))

if __name__ == "__main__":
    main()