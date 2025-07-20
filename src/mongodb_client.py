#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB client for the previously-created collection with authentication support.

Searches the 'articles' collection by:

1. Exact match on the `id` field (single id or comma-separated list)
2. Full-text search across `ner.spans.text` + `ner.spans.value`

Usage
-----
# Flags
python mongo_client.py mydb id 9723 \
       --user alice --password s3cr3t --authSource admin

python mongo_client.py mydb text "Andy Byron" \
       --user alice --password s3cr3t --authSource admin

# Environment variables (safer for CI)
export MONGO_USER=alice
export MONGO_PASS=s3cr3t
export MONGO_AUTH=admin

python mongo_client.py mydb id 9723,1234,555
python mongo_client.py mydb text "Andy Byron"
"""

import os
import sys
import json
import argparse
from pymongo import MongoClient


def build_uri(host, user, pwd, auth):
    """Return a MongoDB URI with optional auth."""
    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}/?authSource={auth}"
    return f"mongodb://{host}/"


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


def usage():
    sys.exit("Usage: python mongo_client.py <db> id|text <query> [options]")


def main():
    parser = argparse.ArgumentParser(
        description="Query MongoDB articles collection."
    )
    parser.add_argument("database", help="Database name")
    parser.add_argument("mode", choices=["id", "text"], help="Query mode")
    parser.add_argument("query", nargs="+", help="Query string (space allowed)")
    parser.add_argument("--host", default="localhost:27017",
                        help="MongoDB host[:port] (default localhost:27017)")
    parser.add_argument("--user", default=os.getenv("MONGO_USER"),
                        help="Username (env: MONGO_USER)")
    parser.add_argument("--password", default=os.getenv("MONGO_PASS"),
                        help="Password (env: MONGO_PASS)")
    parser.add_argument("--authSource", default=os.getenv("MONGO_AUTH", "admin"),
                        help="Authentication database (env: MONGO_AUTH, default admin)")
    args = parser.parse_args()

    uri = build_uri(args.host, args.user, args.password, args.authSource)
    client = MongoClient(uri)
    col = client[args.database]["articles"]

    query_str = " ".join(args.query)
    results = []
    if args.mode == "id":
        ids = parse_ids(query_str)
        results = list(col.find({"id": {"$in": ids}}, {"_id": 0}))
    elif args.mode == "text":
        results = list(
            col.find(
                {"$text": {"$search": query_str}},
                {"_id": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})])
        )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()