import json
import os
import sys
from collections import defaultdict

# Check if command-line argument is provided
if len(sys.argv) != 2:
    print("Usage: python generate_html.py <input_jsonl_file>")
    sys.exit(1)

INPUT_JSONL = sys.argv[1]
OUTPUT_DIR = "./articles_html"

# Ensure the input file exists
if not os.path.isfile(INPUT_JSONL):
    print(f"Error: File '{INPUT_JSONL}' does not exist.")
    sys.exit(1)

# Load all articles
articles = []
with open(INPUT_JSONL, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            article = json.loads(line.strip())
            if isinstance(article, dict):
                articles.append(article)
        except json.JSONDecodeError:
            continue  # Skip invalid lines

# Build index of data for linking
title_to_article = {article["title"]: idx for idx, article in enumerate(articles)}

# For Entities and Types
entity_to_articles = defaultdict(list)
type_to_articles = defaultdict(list)

for idx, article in enumerate(articles):
    title = article["title"]
    ner_spans = [span["text"] for span in article.get("ner", []) for span in span.get("spans", [])]

    for span in article.get("ner", []):
        for ent in span.get("spans", []):
            entity = ent["text"]
            entity_type = ent["value"]
            entity_to_articles[entity].append((idx, title))
            type_to_articles[entity_type].append((idx, title))

# Helper functions
def linkify(kind, name):
    return f"<a href='{kind}/{name}.html'>{name}</a>"

def write_page(path, content):
    full_path = f"{OUTPUT_DIR}/{path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{path.replace('.html', '').capitalize()}</title></head>
<body>
<nav style="margin-bottom: 20px;">
<a href="index.html">Home</a> | 
<a href="titles.html">Titles</a> | 
<a href="entities.html">Entities</a> | 
<a href="types.html">Types</a>
</nav>
{content}
</body></html>""")

# Generate individual article pages
ARTICLE_PAGES_DIR = f"{OUTPUT_DIR}/articles"
os.makedirs(ARTICLE_PAGES_DIR, exist_ok=True)

for idx, article in enumerate(articles):
    content = f"<h1>{article['title']}</h1>"
    content += "<p>" + article.get('summary', '') + "</p>"
    content += "<h2>Text:</h2><p>" + article.get('text', '').replace('\n', '<br>') + "</p>"
    write_page(f"articles/{idx}.html", content)

# Home Page (index.html)
stats = f"""
<h2>Total Articles: {len(articles)}</h2>
<ul>
<li>Unique Titles: {len(set(a['title'] for a in articles))}</li>
<li>Unique Entities: {len(entity_to_articles)}</li>
<li>Entity Types: {len(type_to_articles)}</li>
</ul>
"""

write_page("index.html", stats)

# Titles page - list all titles with links to their articles
titles_content = "<h1>All Titles</h1><ul>"
for idx, article in enumerate(articles):
    titles_content += f"<li><a href='articles/{idx}.html'>{article['title']}</a></li>"
titles_content += "</ul>"
write_page("titles.html", titles_content)

# Entities page - list all named entities and link to related articles
entities_content = "<h1>All Named Entities</h1><ul>"
for entity, refs in sorted(entity_to_articles.items()):
    articles_links = ", ".join([f"<a href='articles/{idx}.html'>{title}</a>" for idx, title in refs])
    entities_content += f"<li>{linkify('entities', entity)}: {articles_links}</li>"
entities_content += "</ul>"
write_page("entities.html", entities_content)

# Types page - list all entity types and link to related articles
types_content = "<h1>All Entity Types</h1><ul>"
for ent_type, refs in sorted(type_to_articles.items()):
    articles_links = ", ".join([f"<a href='articles/{idx}.html'>{title}</a>" for idx, title in refs])
    types_content += f"<li>{linkify('types', ent_type)}: {articles_links}</li>"
types_content += "</ul>"
write_page("types.html", types_content)

print(f"✅ HTML files generated successfully in: {OUTPUT_DIR}")
