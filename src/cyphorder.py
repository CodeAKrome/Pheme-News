#!/usr/bin/env python

import sys

"""Reorder cypher statements so nodes are creaated before they are used in relationships."""


def order_statements(lines):
    # Separate statements by type
    nodes = [line for line in lines if "-[" not in line]
    relationships = [line for line in lines if "-[" in line]
    # Combine all nodes followed by relationships
    return nodes + relationships


def main():
    input_lines = sys.stdin.read().strip().split("\n")
    # Create nodes before using them in relationships
    ordered_statements = order_statements(input_lines)
    # Output the ordered statements
    for statement in ordered_statements:
        print(statement)


if __name__ == "__main__":
    main()
