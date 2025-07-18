import sys
import json


def load_entities(file_path):
    """Parse entities from a file."""
    entities = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    entity_name, entity_type = parts
                    entities.append((entity_name.strip(), entity_type.strip()))
                else:
                    print(
                        f"Skipping malformed entity line: {line.strip()}",
                        file=sys.stderr,
                    )
        return entities
    except FileNotFoundError:
        print(f"Error: Entity file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading entity file: {e}", file=sys.stderr)
        sys.exit(1)


def matches_entities(record, entities):
    """Check if record contains any of the specified entities."""
    try:
        ner = record.get("ner", [])
        for entry in ner:
            spans = entry.get("spans", [])
            for span in spans:
                span_text = span.get("text", "")
                span_value = span.get("value", "")
                for entity_name, entity_type in entities:
                    if span_text == entity_name and span_value == entity_type:
                        return True
        return False
    except Exception as e:
        print(f"Error processing record: {e}", file=sys.stderr)
        return False


def main():
    # Check for entity file path argument
    if len(sys.argv) != 2:
        print(
            "Usage: python filter_jsonl_by_entities.py <entity_file_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load entities from file
    entities = load_entities(sys.argv[1])
    if not entities:
        print("No valid entities found in file", file=sys.stderr)
        sys.exit(1)

    print(
        f"Loaded {len(entities)} entities from {sys.argv[1]} for filtering",
        file=sys.stderr,
    )

    # Process JSONL input from stdin
    matched_records = 0
    total_records = 0

    for line in sys.stdin:
        try:
            total_records += 1
            record = json.loads(line.strip())
            if matches_entities(record, entities):
                print(json.dumps(record))
                matched_records += 1
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON line: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error processing line: {e}", file=sys.stderr)

    print(
        f"Processed {total_records} records, matched {matched_records}", file=sys.stderr
    )


if __name__ == "__main__":
    main()
