import sys
import pprint
import json

# import os
"""General purpose tool kit"""


def jloads(line: str) -> dict:
    """Load string using json"""
    line = line.strip()
    rec = json.loads(line)
    return rec


def alphas(text: str) -> str:
    """Return string with only alphanumerics"""
    return "".join(c for c in text if c.isalpha())


def pretty(obj):
    """Pretty print"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(obj)


def lread_input(infile=None):
    """Read data from a file or stdin and return a list of strings."""
    err = False
    data = []
    if infile:
        try:
            with open(infile, "r") as f:
                line = f.readline()
                while line:
                    data.append(line.strip())
        except IsADirectoryError as e:
            err = f"Attempt to read directory as RSS URL list. {e}"
    else:
        for line in sys.stdin:
            if line:
                data.append(line.strip())
    return data, err


def read_input(infile=None):
    """Read data from a file or stdin and return a string."""
    err = False
    data = False
    if infile:
        try:
            with open(infile, "r") as f:
                data = f.read()
        except IsADirectoryError as e:
            err = f"Attempt to read directory as RSS URL list. {e}"
    else:
        data = sys.stdin.read()
    return data, err
