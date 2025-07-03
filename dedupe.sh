cat `find cache -type f -name 'dedupe_*.jsonl' -newermt '1 day ago'` | src/date_filter.py '-1 day' > cache/dedupe.jsonl
