import sys
import html

def text_to_html_table():
    # Read all lines from stdin
    lines = [line.strip() for line in sys.stdin if line.strip()]
    
    # Start HTML table
    html_output = ["<table border='1' style='border-collapse: collapse; width: 100%;'>"]
    html_output.append("<tr><th>News Headlines</th></tr>")
    
    # Add each line as a table row
    for line in lines:
        # Escape HTML special characters
        escaped_line = html.escape(line)
        html_output.append(f"<tr><td style='padding: 8px;'>{escaped_line}</td></tr>")
    
    # Close table
    html_output.append("</table>")
    
    # Print complete HTML
    print("\n".join(html_output))

if __name__ == "__main__":
    text_to_html_table()
