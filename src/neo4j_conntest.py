#!/usr/bin/env python

from neo4j import GraphDatabase
import os
import sys

# NEO4J_URI=neo4j+s://a991e34d.databases.neo4j.io
# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
PASS = os.environ.get("NEO4J_PASSWORD")
URI = os.environ.get("NEO4J_URI")
USER = "neo4j"

print(f"uri: {URI} u: {USER} p: {PASS}\n", file=sys.stderr)

AUTH = (USER, PASS)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
