import sys

base = sys.argv[1]
#dest = sys.argv[2]

for line in sys.stdin:
    line = line.strip()
    entity, kind, count, ids = line.split("\t")

    buf = []
    
    buf.append(f"mkdir -p {base}/{entity}")
    buf.append(f"pullrecs {ids} > {base}/{entity}/pullrecs.jsonl")
    
    