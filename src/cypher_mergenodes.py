#!/usr/bin/env python3
import sys
import re
from difflib import SequenceMatcher
from collections import defaultdict


def similarity(a, b):
    """Calculate similarity ratio between two strings (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_nodes_from_cypher(cypher_text):
    """Extract node information from Cypher queries"""
    nodes = []

    # Pattern to match node creation/merge statements
    # Matches: CREATE (n:Label {name: "value"}) or MERGE (n:Label {name: "value"})
    node_pattern = (
        r"(?:CREATE|MERGE)\s*\(\s*(\w+)\s*(?::\s*(\w+))?\s*(?:\{([^}]+)\})?\s*\)"
    )

    matches = re.finditer(node_pattern, cypher_text, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        variable = match.group(1)
        label = match.group(2) if match.group(2) else None
        properties_str = match.group(3) if match.group(3) else ""

        # Extract name property if it exists
        name = None
        if properties_str:
            name_match = re.search(
                r'name\s*:\s*["\']([^"\']+)["\']', properties_str, re.IGNORECASE
            )
            if name_match:
                name = name_match.group(1)

        nodes.append(
            {
                "variable": variable,
                "label": label,
                "name": name,
                "properties": properties_str,
                "full_match": match.group(0),
            }
        )

    return nodes


def find_similar_nodes(nodes, similarity_threshold=0.8):
    """Find groups of similar nodes based on name similarity"""
    similar_groups = []
    processed = set()

    for i, node1 in enumerate(nodes):
        if i in processed or not node1["name"]:
            continue

        group = [i]
        processed.add(i)

        for j, node2 in enumerate(nodes[i + 1 :], i + 1):
            if j in processed or not node2["name"]:
                continue

            # Check if nodes have similar names and same label (if specified)
            if (
                similarity(node1["name"], node2["name"]) >= similarity_threshold
                and node1["label"] == node2["label"]
            ):
                group.append(j)
                processed.add(j)

        if len(group) > 1:
            similar_groups.append(group)

    return similar_groups


def remove_duplicates(cypher_text, similarity_threshold=0.8):
    """Remove duplicate nodes with similar names from Cypher text"""
    nodes = extract_nodes_from_cypher(cypher_text)

    if not nodes:
        return cypher_text

    similar_groups = find_similar_nodes(nodes, similarity_threshold)

    # Track which nodes to remove (keep first in each group)
    nodes_to_remove = set()
    replacements = {}

    for group in similar_groups:
        keeper_idx = group[0]
        keeper_node = nodes[keeper_idx]

        print(
            f"Found similar nodes (keeping '{keeper_node['name']}'):", file=sys.stderr
        )

        for idx in group:
            node = nodes[idx]
            print(f"  - {node['name']} (variable: {node['variable']})", file=sys.stderr)

            if idx != keeper_idx:
                nodes_to_remove.add(idx)
                # Map duplicate variable to keeper variable for replacements
                replacements[node["variable"]] = keeper_node["variable"]

    # Remove duplicate node creation statements
    result_text = cypher_text

    # Sort by position in reverse order to avoid index shifting issues
    nodes_to_remove_sorted = sorted(nodes_to_remove, reverse=True)

    for idx in nodes_to_remove_sorted:
        node = nodes[idx]
        # Remove the entire CREATE/MERGE statement
        result_text = result_text.replace(node["full_match"], "", 1)

    # Replace variable references in the remaining text
    for old_var, new_var in replacements.items():
        # Use word boundaries to avoid partial replacements
        result_text = re.sub(r"\b" + re.escape(old_var) + r"\b", new_var, result_text)

    # Clean up extra whitespace and empty lines
    lines = result_text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped:  # Keep non-empty lines
            cleaned_lines.append(line)
        elif (
            cleaned_lines and cleaned_lines[-1].strip()
        ):  # Keep one empty line between sections
            cleaned_lines.append("")

    return "\n".join(cleaned_lines)


def main():
    """Main function to process Cypher queries from stdin"""
    if len(sys.argv) > 1:
        try:
            similarity_threshold = float(sys.argv[1])
            if not 0 <= similarity_threshold <= 1:
                print(
                    "Error: Similarity threshold must be between 0 and 1",
                    file=sys.stderr,
                )
                sys.exit(1)
        except ValueError:
            print(
                "Error: Invalid similarity threshold. Must be a number between 0 and 1",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        similarity_threshold = 0.8

    print(f"Using similarity threshold: {similarity_threshold}", file=sys.stderr)

    # Read all input from stdin
    try:
        cypher_input = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)

    if not cypher_input.strip():
        print("No input provided", file=sys.stderr)
        sys.exit(1)

    # Process and remove duplicates
    result = remove_duplicates(cypher_input, similarity_threshold)

    # Output the cleaned Cypher queries
    print(result)


if __name__ == "__main__":
    main()
