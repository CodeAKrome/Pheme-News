import sys

def print_html_table():
    # Store rows
    rows = []
    
    # Read from stdin
    for line in sys.stdin:
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        id_num, title = parts
        rows.append((id_num, title))
    
    if not rows:
        print("<p>No valid data found</p>")
        return
    
    # Print HTML
    print('<!DOCTYPE html>')
    print('<html lang="en">')
    print('<head>')
    print('    <meta charset="UTF-8">')
    print('    <title>Data Table</title>')
    print('    <style>')
    print('        table {')
    print('            border-collapse: collapse;')
    print('            width: 100%;')
    print('            max-width: 800px;')
    print('            margin: 20px auto;')
    print('            font-family: Arial, sans-serif;')
    print('        }')
    print('        th, td {')
    print('            border: 1px solid #ddd;')
    print('            padding: 8px;')
    print('            text-align: left;')
    print('        }')
    print('        th {')
    print('            background-color: #f2f2f2;')
    print('            font-weight: bold;')
    print('        }')
    print('        tr:nth-child(even) {')
    print('            background-color: #f9f9f9;')
    print('        }')
    print('    </style>')
    print('</head>')
    print('<body>')
    print('    <table>')
    print('        <tr>')
    print('            <th>ID</th>')
    print('            <th>Title</th>')
    print('        </tr>')
    for id_num, title in rows:
        print('        <tr>')
        print(f'            <td>{id_num}</td>')
        print(f'            <td>{title}</td>')
        print('        </tr>')
    print('    </table>')
    print('</body>')
    print('</html>')

if __name__ == "__main__":
    print_html_table()
