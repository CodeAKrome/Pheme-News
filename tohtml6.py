import json
import os
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: python generate_html.py <input_jsonl_file>")
    sys.exit(1)

INPUT_JSONL = sys.argv[1]
OUTPUT_DIR = "./articles_html"

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
            continue

# Build data structures
title_to_article = {article["title"]: idx for idx, article in enumerate(articles)}
entity_to_articles = defaultdict(list)
type_to_entities = defaultdict(set)
title_to_date = {a["title"]: a.get("published", "Unknown") for a in articles}
sorted_titles_by_date = sorted(title_to_date.items(), key=lambda x: x[1], reverse=True)

for idx, article in enumerate(articles):
    title = article["title"]
    source = article.get("source", "Unknown")
    for span_group in article.get("ner", []):
        for ent in span_group.get("spans", []):
            entity = ent["text"]
            entity_type = ent["value"]
            # Append only if this article hasn't been added for this entity
            if not any(ref[0] == idx for ref in entity_to_articles[entity]):
                entity_to_articles[entity].append((idx, title, source))
            type_to_entities[entity_type].add(entity)

PAGINATION_SIZE = 50

def write_page(path, content, base_path=""):
    """Write an HTML page with navigation adjusted for the page's directory."""
    full_path = os.path.join(OUTPUT_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{path.replace('.html', '').replace('/', ' > ').capitalize()}</title>
<link rel="stylesheet" href="{base_path}static/style.css">
</head>
<body>
<nav>
<a href="{base_path}index.html">Home</a> | 
<a href="{base_path}titles.html">Titles</a> | 
<a href="{base_path}entities.html">Entities</a> | 
<a href="{base_path}types.html">Types</a>
</nav>
<div class="content">
{content}
</div>
<script src="{base_path}static/script.js"></script>
</body></html>""")

os.makedirs(os.path.join(OUTPUT_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "articles"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "entities"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "types"), exist_ok=True)

# CSS
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
.title-list li {
    margin-bottom: 0.7em;
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
.kv-table {
    width: 100%;
    border-collapse: collapse;
}
.kv-table td, .kv-table th {
    border: 1px solid #ccc;
    padding: 8px;
}
.kv-table th {
    background-color: #eee;
}
.pagination {
    margin-top: 1em;
    text-align: center;
}
.pagination a {
    margin: 0 5px;
    text-decoration: none;
    color: #003366;
}
""")

# JS
with open(os.path.join(OUTPUT_DIR, "static/script.js"), "w", encoding="utf-8") as f:
    f.write("""
function filterList(inputId, listClass) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const items = document.querySelectorAll(`.${listClass}`);
    items.forEach(item => {
        const txtValue = item.textContent || item.innerText;
        item.style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    });
}
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('searchInput')) {
        document.getElementById('searchInput').addEventListener('keyup', () => filterList('searchInput', 'entity-item'));
    }
});
""")

# Generate article pages
for idx, article in enumerate(articles):
    content = f"<h1>{article['title']}</h1>"
    content += "<table class='kv-table'>"
    for key, value in article.items():
        if key == "ner":
            spans = [span["text"] for group in value for span in group.get("spans", [])]
            links = ", ".join([f"<a href='../entities/{e.replace('/', '_')}.html'>{e}</a>" for e in spans])
            content += f"<tr><th>Named Entities</th><td>{links}</td></tr>"
        elif key == "text":
            content += f"<tr><th>Text</th><td><p>{value.replace(chr(10), '<br>')}</p></td></tr>"
        else:
            content += f"<tr><th>{key.capitalize()}</th><td>{value}</td></tr>"
    content += "</table>"
    # Use ../ for navigation from articles/ directory
    write_page(f"articles/{idx}.html", content, base_path="../")

# Index Page
write_page("index.html", f"""
<h2>Total Articles: {len(articles)}</h2>
<ul>
<li>Unique Titles: {len(set(a['title'] for a in articles))}</li>
<li>Unique Entities: {len(entity_to_articles)}</li>
<li>Entity Types: {len(type_to_entities)}</li>
</ul>
<p>This site was generated from <code>{os.path.basename(INPUT_JSONL)}</code>.</p>
""", base_path="")

# Titles Page with Pagination
def paginate_list(items, path_func, name_func, per_page=50):
    total_pages = (len(items) + per_page - 1) // per_page
    for i in range(total_pages):
        start = i * per_page
        end = start + per_page
        page_content = f"<h1>{name_func(i)}</h1>"
        page_content += "<ol class='title-list'>"
        for title, date in items[start:end]:
            idx = title_to_article.get(title, -1)
            if idx >= 0:
                page_content += f"<li><span class='date'>{date}</span><br><a href='articles/{idx}.html'>{title}</a></li>"
            else:
                print(f"Warning: No article found for title '{title}'")
        page_content += "</ol>"
        page_content += render_pagination(i, total_pages, path_func)
        # Titles pages are in root directory
        write_page(path_func(i), page_content, base_path="")
        
def render_pagination(current_page, total_pages, path_func):
    pagination = "<div class='pagination'>"
    for i in range(total_pages):
        if i == current_page:
            pagination += f"<strong>{i+1}</strong>"
        else:
            pagination += f"<a href='{path_func(i)}'>{i+1}</a>"
    pagination += "</div>"
    return pagination

paginate_list(
    sorted_titles_by_date,
    lambda p: "titles.html" if p == 0 else f"titles_{p}.html",
    lambda p: f"All Titles (Page {p+1})"
)

# Entities Page
entities_sorted = sorted(entity_to_articles.items())

def render_entity_page(entities_chunk, page_num):
    content = """
    <h1>All Named Entities</h1>
    <div class="search-box">
    <input type="text" id="searchInput" placeholder="Search entities..." />
    </div>
    <ul>
    """
    for entity, refs in entities_chunk:
        ref_lines = "".join([
            f"<a class='article-link alt-color' href='../articles/{idx}.html'>• {title} ({source})</a><br>" if i % 2 == 0 else
            f"<a class='article-link' href='../articles/{idx}.html'>• {title} ({source})</a><br>"
            for i, (idx, title, source) in enumerate(refs)
            if os.path.exists(os.path.join(OUTPUT_DIR, f"articles/{idx}.html"))
        ])
        content += f"<li class='entity-item'><span class='entity-name'>{entity}</span><br>{ref_lines}</li>"
    content += "</ul>"
    return content

for i in range(0, len(entities_sorted), PAGINATION_SIZE):
    chunk = entities_sorted[i:i + PAGINATION_SIZE]
    page_num = i // PAGINATION_SIZE
    page_content = render_entity_page(chunk, page_num)
    # Entities pages are in root directory
    if page_num == 0:
        write_page("entities.html", page_content, base_path="")
    else:
        write_page(f"entities_{page_num}.html", page_content, base_path="")

# Add pagination to main entities page
if len(entities_sorted) > PAGINATION_SIZE:
    page_links = render_pagination(
        0,
        (len(entities_sorted) + PAGINATION_SIZE - 1) // PAGINATION_SIZE,
        lambda p: "entities.html" if p == 0 else f"entities_{p}.html"
    )
    with open(os.path.join(OUTPUT_DIR, "entities.html"), "r", encoding="utf-8") as f:
        existing_content = f.read()
    with open(os.path.join(OUTPUT_DIR, "entities.html"), "w", encoding="utf-8") as f:
        f.write(existing_content.replace("</div>", f"{page_links}</div>"))

# Entity Detail Pages
for entity, refs in entity_to_articles.items():
    titles_list = "".join([
        f"<li><a href='../articles/{idx}.html'>{title}</a> ({source})</li>"
        for idx, title, source in refs
        if os.path.exists(os.path.join(OUTPUT_DIR, f"articles/{idx}.html"))
    ])
    # Entity detail pages are in entities/ directory
    write_page(f"entities/{entity.replace('/', '_')}.html", f"<h1>Titles Containing: {entity}</h1><ul>{titles_list}</ul>", base_path="../")

# Type Pages
for ent_type in sorted(type_to_entities):
    ents_content = f"<h1>Entities of Type: {ent_type}</h1><ul>"
    for entity in sorted(type_to_entities[ent_type]):
        count = len(entity_to_articles.get(entity, []))
        ents_content += f"<li><a href='../entities/{entity.replace('/', '_')}.html'>{entity}</a> ({count} uses)</li>"
    ents_content += "</ul>"
    # Type detail pages are in types/ directory
    write_page(f"types/{ent_type}.html", ents_content, base_path="../")

type_links = "".join([f"<li><a href='types/{typ}.html'>{typ}</a></li>" for typ in sorted(type_to_entities)])
write_page("types.html", f"<h1>Entity Types</h1><ul>{type_links}</ul>", base_path="")

print(f"✅ HTML files with pagination, entity sources, and styled article views generated in: {OUTPUT_DIR}")
