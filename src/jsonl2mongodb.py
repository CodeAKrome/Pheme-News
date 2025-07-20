#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bulk-load JSON-lines from stdin into a local (or remote) MongoDB database
with optional authentication.

Usage
-----
    # flags
    cat file.jsonl | python jsonl2mongodb.py mydb \
        --user alice --password s3cr3t --authSource admin

    # env vars
    export MONGO_USER=alice
    export MONGO_PASS=s3cr3t
    export MONGO_AUTH=admin
    cat file.jsonl | python jsonl2mongodb.py mydb
"""

import json, sys, os
import argparse
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import BulkWriteError


def build_uri(host, user, pwd, auth):
    """Return a MongoDB URI with optional auth."""
    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}/?authSource={auth}"
    return f"mongodb://{host}/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream JSONL → MongoDB.")
    parser.add_argument("database", help="Target database name")
    parser.add_argument(
        "--host",
        default="localhost:27017",
        help="MongoDB host[:port] (default localhost:27017)",
    )
    parser.add_argument(
        "--user", default=os.getenv("MONGO_USER"), help="Username (env: MONGO_USER)"
    )
    parser.add_argument(
        "--password", default=os.getenv("MONGO_PASS"), help="Password (env: MONGO_PASS)"
    )
    parser.add_argument(
        "--authSource",
        default=os.getenv("MONGO_AUTH", "admin"),
        help="Auth database (env: MONGO_AUTH, default admin)",
    )
    args = parser.parse_args()

    uri = build_uri(args.host, args.user, args.password, args.authSource)
    client = MongoClient(uri)
    db = client[args.database]
    col = db["articles"]

    # --- create indexes only once ---
    if "id_1" not in col.index_information():  # single-field
        col.create_index("id", unique=True)

    compound_name = "ner.spans.text_text_ner.spans.value_text"
    if compound_name not in col.index_information():  # text index
        col.create_index([("ner.spans.text", TEXT), ("ner.spans.value", TEXT)])

    # --- bulk-insert ---
    docs = (json.loads(l) for l in sys.stdin if l.strip())
    try:
        col.insert_many(docs, ordered=False)
    except BulkWriteError as bwe:
        for err in bwe.details["writeErrors"]:
            if err["code"] != 11000:
                print(err, file=sys.stderr)

    print(f"✓ Finished inserting into MongoDB database '{args.database}'")


if __name__ == "__main__":
    main()
