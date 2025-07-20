#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB client with authentication and flexible text search.

Modes
-----
id   : comma-separated list of ids
text : space-separated OR search; plus-separated (+) AND search

Examples
--------
python mongo_client.py mydb id 9723,1234,555
python mongo_client.py mydb text "Andy Byron"           # OR
python mongo_client.py mydb text "Andy+Byron+BBC"       # AND
"""

import os
import sys
import json
import argparse
from pymongo import MongoClient


def build_uri(host, user, pwd, auth):
    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}/?authSource={auth}"
    return f"mongodb://{host}/"


def parse_ids(raw):
    ids = []
    for part in raw.split(","):
        part = part.strip()
        try:
            ids.append(int(part))
        except ValueError:
            ids.append(part)
    return ids


def build_text_query(raw_terms: str):
    """
    Split on spaces for OR, on '+' for AND.
    Examples:
        "foo bar"   ->  {"$search": "foo bar"}          # OR
        "foo+bar"   ->  {"$search": "\"foo\" \"bar\""} # AND
    """
    if "+" in raw_terms:
        and_terms = [t.strip() for t in raw_terms.split("+") if t.strip()]
        return " ".join(f'"{t}"' for t in and_terms)  # AND
    return raw_terms.strip()                          # OR


def main():
    parser = argparse.ArgumentParser(description="Query MongoDB articles collection.")
    parser.add_argument("database", help="Database name")
    parser.add_argument("mode", choices=["id", "text"], help="Query mode")
    parser.add_argument("query", help="Query string (see docstring)")
    parser.add_argument("--host", default="localhost:27017")
    parser.add_argument("--user", default=os.getenv("MONGO_USER"))
    parser.add_argument("--password", default=os.getenv("MONGO_PASS"))
    parser.add_argument("--authSource", default=os.getenv("MONGO_AUTH", "admin"))
    args = parser.parse_args()

    uri = build_uri(args.host, args.user, args.password, args.authSource)
    col = MongoClient(uri)[args.database]["articles"]

    results = []
    if args.mode == "id":
        ids = parse_ids(args.query)
        results = list(col.find({"id": {"$in": ids}}, {"_id": 0}))
    elif args.mode == "text":
        search_clause = build_text_query(args.query)
        results = list(
            col.find(
                {"$text": {"$search": search_clause}},
                {"_id": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})])
        )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()