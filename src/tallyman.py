import sys
from json import loads, dumps
from lib.file_cache import FileCache as file_cache

"""
Assign unique, monotonically increasing IDs to each article if not in cache.
Skip cached articles since they've already been assigned an ID and processed.
"""

COUNTERFILE = 'cache/counter.json'
CACHEFILE = 'cache/articles.json'

id = 0
fc = file_cache(CACHEFILE)

try:
    count_fh = open(COUNTERFILE, 'r')
    idline = count_fh.read()
    id = loads(idline)["id"]
    count_fh.close()
except FileNotFoundError as e:
    count_fh = open(COUNTERFILE, 'w')
    count_fh.write(dumps({"id": 0}))
except ValueError as e:
    print(f"Invalid JSON: {idline}", file=sys.stderr)
    exit(1)
count_fh = open(COUNTERFILE, 'w')
    
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    data = loads(line)
    if fc.cached(data["link"]): continue
    fc.put(data["link"], id)
    data["id"] = id
    print(dumps(data))
    id += 1
count_fh.write(dumps({"id": id}))
count_fh.close()
