import sys

# Read tab-delimited data from stdin
print('<!DOCTYPE html>')
print('<html lang="en">')
print('<head><meta charset="UTF-8"><title>Article Table</title></head>')
print('<body>')
print('<table border="1">')
print('<tr><th>Article ID</th><th>Article Title</th><th>Article Link</th></tr>')

for line in sys.stdin:
    # Split the line by tabs and strip any whitespace
    article_id, title, link = line.strip().split('\t')
    # Output HTML table row with link as clickable
    print(f'<tr><td>{article_id}</td><td>{title}</td><td><a href="{link}">{link}</a></td></tr>')

print('</table>')
print('</body>')
print('</html>')
