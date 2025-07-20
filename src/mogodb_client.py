#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB client for the previously-created collection.

Searches the 'articles' collection by:

1. exact match on the `id` field (single id or comma-separated list)
2. full-text search across `ner.spans.text` + `ner.spans.value`

Usage
-----
python mongo_client.py mydb id 9723
python mongo_client.py mydb id 9723,1234,555
python mongo_client.py mydb text "Andy Byron"
"""
import sys
import json
from pymongo import MongoClient


def usage():
    sys.exit("Usage: python mongo_client.py <db> id|<text> <query>")


def parse_ids(raw: str):
    """Convert comma-separated string to list of int or str."""
    ids = []
    for part in raw.split(","):
        part = part.strip()
        try:
            ids.append(int(part))
        except ValueError:
            ids.append(part)
    return ids


def main():
    if len(sys.argv) < 4:
        usage()

    _, db_name, mode, *query_parts = sys.argv
    query = " ".join(query_parts)

    client = MongoClient("mongodb://localhost:27017")
    col = client[db_name]["articles"]

    results = []
    if mode == "id":
        ids = parse_ids(query)
        results = list(col.find({"id": {"$in": ids}}, {"_id": 0}))
    elif mode == "text":
        results = list(
            col.find(
                {"$text": {"$search": query}},
                {"_id": 0, "score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
        )
    else:
        usage()

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()