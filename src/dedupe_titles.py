#!/usr/bin/env python

import json
import sys

def main():
    seen_titles = set()
    
    for line_number, line in enumerate(sys.stdin, 1):
        try:
            record = json.loads(line.strip())
            
            # Check if "title" field exists
            if "title" not in record:
                continue
                
            title = record["title"]
            
            if title in seen_titles:
                sys.stderr.write(f"Duplicate title found and rejected: {title}\n")
            else:
                seen_titles.add(title)
                print(json.dumps(record))
                
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Error decoding JSON on line {line_number}: {e}\n")
        except Exception as e:
            sys.stderr.write(f"Unexpected error processing line {line_number}: {e}\n")

if __name__ == "__main__":
    main()
