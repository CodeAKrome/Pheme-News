#!/usr/bin/env python

import json
import sys
import subprocess
import os

# This script reads JSON files from standard input, looking for the highest 'good' value.
# It then prints the filename with the highest 'good' value and copies a related markdown file
# to a temporary location.  

cwd = os.getcwd()
if cwd.endswith('/'):
    cwd = cwd[:-1]
    
def find_highest_good_file():
    max_good = float('-inf')
    best_file = None
    
    for line in sys.stdin:
        filename = line.strip()
        if not filename:
            continue
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            if 'good' in data:
                good_value = data['good']
                if isinstance(good_value, (int, float)) and good_value > max_good:
                    max_good = good_value
                    best_file = filename
                    
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
            continue
    
    if best_file:
        print(f"file: {best_file} max_good: {max_good}", file=sys.stderr)
        best_file = best_file.split('_')[0]
        md = f"{best_file}_relink.md"
        print(md, file=sys.stdout)
        absolute_path = os.path.join(cwd, 'tmp/top10.md')
        # cmd = f"cp {md} {absolute_path}"
        cmd = f"cat {md} | src/no_mthead.pl | src/gatherids.pl > {absolute_path}"
        print(cmd, file=sys.stderr)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        sys.exit(result.returncode)
    else:
        print("No valid files with 'good' entries found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_highest_good_file()
