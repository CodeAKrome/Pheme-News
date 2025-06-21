import json
import sys
from collections import defaultdict

# Create a tab delimited file of entities.
# entity, type, reference count, article ids containing entity
# from stdin to stdout

# Dictionary to store entity references with article IDs and occurrence counts
entity_references = defaultdict(lambda: {'count': 0, 'article_ids': set()})

# Read JSONL from stdin
for line in sys.stdin:
    try:
        # Parse each line as JSON
        record = json.loads(line.strip())
        
        # Get article ID
        article_id = record.get('id')
        
        # Process NER spans
        for ner_entry in record.get('ner', []):
            spans = ner_entry.get('spans', [])
            for span in spans:
                entity_name = span.get('text')
                entity_type = span.get('value')
                if entity_name and entity_type:
                    # Create composite key from entity name and type
                    entity_key = (entity_name, entity_type)
                    # Increment occurrence count and add article ID
                    entity_references[entity_key]['count'] += 1
                    entity_references[entity_key]['article_ids'].add(article_id)
    
    except json.JSONDecodeError:
        # Skip invalid JSON lines
        continue

# Prepare data for sorting
output_data = [
    (entity_name, entity_type, data['count'], sorted(data['article_ids']))
    for (entity_name, entity_type), data in entity_references.items()
]

# Sort by occurrence count (descending), then entity name, then entity type
output_data.sort(key=lambda x: (-x[2], x[0], x[1]))

# Output results in tab-delimited format
for entity_name, entity_type, count, article_ids in output_data:
    article_ids_str = ','.join(map(str, article_ids))
    print(f"{entity_name}\t{entity_type}\t{count}\t{article_ids_str}")
