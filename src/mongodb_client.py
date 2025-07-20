#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reusable MongoArticles class + CLI entry-point.

Examples
--------
# --- CLI ---
python mongo_client.py mydb id 1,2,3
python mongo_client.py mydb text "Andy+Byron"

# --- Library ---
from mongo_client import MongoArticles
db = MongoArticles("mydb", user="alice", password="s3cr3t", authSource="admin")
docs = db.search_text("Andy+Byron")
docs = db.search_ids([9723, "abc"])
"""

from __future__ import annotations
import os
import json
import argparse
from typing import List, Any, Dict
from pymongo import MongoClient


class MongoArticles:
    """
    Lightweight wrapper around the 'articles' collection.
    """

    def __init__(
        self,
        database: str,
        host: str = "localhost:27017",
        user: str | None = None,
        password: str | None = None,
        authSource: str = "admin",
    ):
        uri = self._build_uri(host, user, password, authSource)
        self.col = MongoClient(uri)[database]["articles"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def search_ids(self, ids: List[str | int]) -> List[Dict[str, Any]]:
        """Return all documents whose `id` is in `ids`."""
        return list(self.col.find({"id": {"$in": ids}}, {"_id": 0}))

    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """
        Search text index.

        Spaces = OR, '+' = AND (quoted phrases).
        """
        search_clause = self._build_text_query(query)
        cursor = self.col.find(
            {"$text": {"$search": search_clause}},
            {"_id": 0, "score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})])
        return list(cursor)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_uri(host: str, user: str | None, pwd: str | None, auth: str) -> str:
        if user and pwd:
            return f"mongodb://{user}:{pwd}@{host}/?authSource={auth}"
        return f"mongodb://{host}/"

    @staticmethod
    def _build_text_query(raw: str) -> str:
        if "+" in raw.strip():
            # AND search: "foo" "bar"
            return " ".join(f'"{t.strip()}"' for t in raw.split("+") if t.strip())
        # OR search: leave untouched
        return raw.strip()


# ----------------------------------------------------------------------
# CLI shim
# ----------------------------------------------------------------------
def _parse_ids(raw: str) -> List[str | int]:
    """Convert '1,2,abc' → [1, 2, 'abc']"""
    out = []
    for part in raw.split(","):
        part = part.strip()
        try:
            out.append(int(part))
        except ValueError:
            out.append(part)
    return out


def _cli():
    parser = argparse.ArgumentParser(description="Query MongoDB articles.")
    parser.add_argument("database")
    parser.add_argument("mode", choices=["id", "text"])
    parser.add_argument("query", help="id list or text query")
    parser.add_argument("--host", default="localhost:27017")
    parser.add_argument("--user", default=os.getenv("MONGO_USER"))
    parser.add_argument("--password", default=os.getenv("MONGO_PASS"))
    parser.add_argument("--authSource", default=os.getenv("MONGO_AUTH", "admin"))
    args = parser.parse_args()

    db = MongoArticles(
        args.database,
        host=args.host,
        user=args.user,
        password=args.password,
        authSource=args.authSource,
    )

    if args.mode == "id":
        docs = db.search_ids(_parse_ids(args.query))
    else:
        docs = db.search_text(args.query)

    print(json.dumps(docs, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
