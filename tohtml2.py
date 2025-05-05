import json
import os
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: python generate_html.py <input_jsonl_file>")
    sys.exit(1)

INPUT_JSONL = sys.argv[1]
OUTPUT_DIR = "./output_html"

if not os.path.isfile(INPUT_JSONL):
    print(f"Error: File '{INPUT_JSONL}' does not exist.")
    sys.exit(1)

articles = []
with open(INPUT_JSONL, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            article = json.loads(line.strip())
            if isinstance(article, dict):
                articles.append(article)
        except json.JSONDecodeError:
            continue

# Build data structures
entity_to_articles = defaultdict(list)
type_to_entities = defaultdict(set)
title_to_date = {a["title"]: a.get("published", "Unknown") for a in articles}
sorted_titles_by_date = sorted(title_to_date.items(), key=lambda x: x[1], reverse=True)

for idx, article in enumerate(articles):
    title = article["title"]
    for span_group in article.get("ner", []):
        for ent in span_group.get("spans", []):
            entity = ent["text"]
            entity_type = ent["value"]
            entity_to_articles[entity].append((idx, title))
            type_to_entities[entity_type].add(entity)

def write_page(path, content):
    full_path = os.path.join(OUTPUT_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{path.replace('.html', '').replace('/', ' > ').capitalize()}</title>
<link rel="stylesheet" href="static/style.css">
</head>
<body>
<nav>
<a href="index.html">Home</a> | 
<a href="titles.html">Titles</a> | 
<a href="entities.html">Entities</a> | 
<a href="types.html">Types</a>
</nav>
<div class="content">
{content}
</div>
</body></html>""")

os.makedirs(os.path.join(OUTPUT_DIR, "static"), exist_ok=True)
with open(os.path.join(OUTPUT_DIR, "static/style.css"), "w", encoding="utf-8") as f:
    f.write("""
body {
    font-family: Arial, sans-serif;
    background: #f9f9f9;
    margin: 0;
    padding: 0;
}
nav {
    background: #003366;
    color: white;
    padding: 1em;
}
nav a {
    color: white;
    text-decoration: none;
    margin-right: 1em;
}
.content {
    max-width: 900px;
    margin: 2em auto;
    padding: 1em;
    background: white;
    border-radius: 5px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
h1, h2, h3 {
    color: #003366;
}
.title-list li, .entity-list li {
    margin-bottom: 0.5em;
}
.date {
    color: #777;
    font-size: 0.9em;
}
.entity-name {
    font-weight: bold;
}
.article-link {
    display: block;
    color: #0066cc;
}
.alt-color {
    color: #d9534f;
}
.search-box {
    margin-bottom: 1em;
}
""")

# Generate article pages
ARTICLE_PAGES_DIR = os.path.join(OUTPUT_DIR, "articles")
os.makedirs(ARTICLE_PAGES_DIR, exist_ok=True)

for idx, article in enumerate(articles):
    content = f"<h1>{article['title']}</h1>"
    content += "<p>" + article.get('summary', '') + "</p>"
    content += "<h2>Text:</h2><p>" + article.get('text', '').replace('\n', '<br>') + "</p>"
    write_page(f"articles/{idx}.html", content)

# Index Page
write_page("index.html", f"""
<h2>Total Articles: {len(articles)}</h2>
<ul>
<li>Unique Titles: {len(set(a['title'] for a in articles))}</li>
<li>Unique Entities: {len(entity_to_articles)}</li>
<li>Entity Types: {len(type_to_entities)}</li>
</ul>
<p>This site was generated from <code>{os.path.basename(INPUT_JSONL)}</code>.</p>
""")

# Titles Page (sorted by published date)
titles_content = "<h1>All Titles</h1><ol class='title-list'>"
for title, date in sorted_titles_by_date:
    idx = title_to_article.get(title, -1)
    if idx >= 0:
        titles_content += f"<li><span class='date'>{date}</span><br><a href='articles/{idx}.html'>{title}</a></li>"
titles_content += "</ol>"
write_page("titles.html", titles_content)

# Named Entities Page
entities_content = "<h1>All Named Entities</h1><div class='search-box'><input type='text' id='searchInput' placeholder='Search entities...'></div><ul class='entity-list'>"
for entity in sorted(entity_to_articles):
    titles_links = "".join([
        f"<a class='article-link alt-color' href='articles/{idx}.html'>• {title}</a><br>" if i % 2 == 0 else
        f"<a class='article-link' href='articles/{idx}.html'>• {title}</a><br>"
        for i, (idx, title) in enumerate(entity_to_articles[entity])
    ])
    entities_content += f"<li><span class='entity-name'>{entity}</span><br>{titles_links}</li>"
entities_content += """
<script>
document.getElementById('searchInput').addEventListener('keyup', function() {
    let filter = this.value.toLowerCase();
    let items = document.querySelectorAll('.entity-list li');
    items.forEach(item => {
        let txt = item.textContent || item.innerText;
        item.style.display = txt.toLowerCase().includes(filter) ? '' : 'none';
    });
});
</script>
"""
write_page("entities.html", entities_content)

# Entity Types Page & Type-Specific Pages
type_links = ""
os.makedirs(os.path.join(OUTPUT_DIR, "types"), exist_ok=True)

for ent_type in sorted(type_to_entities):
    ents_content = f"<h1>Entities of Type: {ent_type}</h1><ul class='entity-list'>"
    for entity in sorted(type_to_entities[ent_type]):
        count = len(entity_to_articles.get(entity, []))
        ents_content += f"<li><a href='../entities/{entity.replace('/', '_')}.html'>{entity}</a> ({count} uses)</li>"
    ents_content += "</ul>"
    write_page(f"types/{ent_type}.html", ents_content)
    type_links += f"<li><a href='types/{ent_type}.html'>{ent_type}</a></li>"

write_page("types.html", f"<h1>Entity Types</h1><ul>{type_links}</ul>")

# Entity Detail Pages
ENTITY_DIR = os.path.join(OUTPUT_DIR, "entities")
os.makedirs(ENTITY_DIR, exist_ok=True)

for entity, refs in entity_to_articles.items():
    titles_list = "".join([f"<li><a href='../articles/{idx}.html'>{title}</a></li>" for idx, title in refs])
    write_page(f"entities/{entity.replace('/', '_')}.html", f"<h1>Titles Containing: {entity}</h1><ul>{titles_list}</ul>")

print(f"✅ HTML files with search, styling, and enhanced structure generated in: {OUTPUT_DIR}")
