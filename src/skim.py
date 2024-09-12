import sys
from json import loads

"""json -> tsv"""
   
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    data = loads(line)
    for field in sys.argv[1:]:
        print(data[field].replace('\t', ' '), end="\t")
    print()
