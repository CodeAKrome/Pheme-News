#!/bin/sh
cat cache/dedupe.jsonl|jq -r '[.id, .title] | join("\t")' | sort -k 2 | uniq | awk '!seen[$2]++'
