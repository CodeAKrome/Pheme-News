import sys
import html

print("<!DOCTYPE html>")
print("<html lang=\"en\">")
print("<head>")
print("  <meta charset=\"UTF-8\">")
print("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
print("  <title>TSV to HTML Table</title>")
print("  <style>")
print("    body { font-family: sans-serif; margin: 20px; }")
print("    table { border-collapse: collapse; width: 100%; }")
print("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
print("    th { background-color: #f2f2f2; }")
print("  </style>")
print("</head>")
print("<body>")
print("  <h1>Converted TSV Data</h1>")
print("  <table>")

# Assuming the first row is data, not a header.
# If you want to treat the first row as a header,
# you'll need to modify this section to print <th> tags.
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    columns = line.split('\t')
    print("    <tr>")
    for col in columns:
        print(f"      <td>{html.escape(col)}</td>")
    print("    </tr>")

print("  </table>")
print("</body>")
print("</html>")
