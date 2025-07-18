#!/usr/bin/env python3
"""
JSONL to HTML Converter

Converts JSONL (JSON Lines) files to formatted HTML documents.
Supports nested JSON structures and provides clean, readable HTML output.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from html import escape
from typing import Any, Dict, List, Union


class JsonlToHtmlConverter:
    def __init__(self, style_mode: str = "modern"):
        """
        Initialize the converter with specified styling.

        Args:
            style_mode: 'modern', 'classic', or 'minimal'
        """
        self.style_mode = style_mode

    def get_css_styles(self) -> str:
        """Return CSS styles based on the selected mode."""
        if self.style_mode == "modern":
            return """
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #333;
                }
                .container { 
                    background: white; 
                    padding: 30px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }
                .header { 
                    border-bottom: 3px solid #007bff; 
                    padding-bottom: 20px; 
                    margin-bottom: 30px;
                }
                .record { 
                    margin-bottom: 40px; 
                    padding: 25px; 
                    border: 1px solid #e9ecef; 
                    border-radius: 6px;
                    background-color: #fdfdfd;
                }
                .record:nth-child(even) { background-color: #f8f9fa; }
                .record-title { 
                    color: #007bff; 
                    font-size: 1.4em; 
                    font-weight: 600; 
                    margin-bottom: 15px;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 10px;
                }
                .field { 
                    margin: 12px 0; 
                    display: flex;
                    flex-wrap: wrap;
                }
                .field-name { 
                    font-weight: 600; 
                    color: #495057;
                    min-width: 120px;
                    margin-right: 15px;
                }
                .field-value { 
                    flex: 1;
                    word-break: break-word;
                }
                .nested-object { 
                    margin-left: 20px; 
                    padding: 15px; 
                    background-color: #f1f3f4; 
                    border-radius: 4px;
                    border-left: 4px solid #007bff;
                }
                .array-item { 
                    margin: 8px 0; 
                    padding: 10px; 
                    background-color: #e9ecef; 
                    border-radius: 4px;
                }
                .json-string { color: #d73a49; }
                .json-number { color: #005cc5; }
                .json-boolean { color: #e36209; }
                .json-null { color: #6f42c1; }
                .tags { 
                    display: flex; 
                    flex-wrap: wrap; 
                    gap: 6px; 
                    margin-top: 8px;
                }
                .tag { 
                    background-color: #e9ecef; 
                    padding: 4px 8px; 
                    border-radius: 12px; 
                    font-size: 0.85em;
                    color: #495057;
                }
                .metadata { 
                    font-size: 0.9em; 
                    color: #6c757d; 
                    border-top: 1px solid #e9ecef; 
                    padding-top: 15px; 
                    margin-top: 20px;
                }
                pre { 
                    background-color: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 4px; 
                    overflow-x: auto;
                    border-left: 4px solid #28a745;
                }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .stats {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    text-align: center;
                }
            </style>
            """
        elif self.style_mode == "classic":
            return """
            <style>
                body { 
                    font-family: Georgia, serif; 
                    line-height: 1.6; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background-color: #fff;
                }
                .container { margin-bottom: 30px; }
                .header { 
                    border-bottom: 2px solid #333; 
                    padding-bottom: 10px; 
                    margin-bottom: 20px;
                }
                .record { 
                    margin-bottom: 30px; 
                    padding: 20px; 
                    border: 1px solid #ccc;
                }
                .record-title { 
                    color: #333; 
                    font-size: 1.3em; 
                    font-weight: bold; 
                    margin-bottom: 15px;
                }
                .field { margin: 10px 0; }
                .field-name { font-weight: bold; }
                .nested-object { 
                    margin-left: 20px; 
                    padding: 10px; 
                    border-left: 3px solid #ccc;
                }
            </style>
            """
        else:  # minimal
            return """
            <style>
                body { 
                    font-family: monospace; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 20px;
                }
                .record { margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }
                .field { margin: 5px 0; }
                .field-name { font-weight: bold; }
                .nested-object { margin-left: 20px; }
            </style>
            """

    def format_value(self, value: Any, key: str = "") -> str:
        """Format a value based on its type with appropriate HTML styling."""
        if value is None:
            return '<span class="json-null">null</span>'
        elif isinstance(value, bool):
            return f'<span class="json-boolean">{str(value).lower()}</span>'
        elif isinstance(value, (int, float)):
            return f'<span class="json-number">{value}</span>'
        elif isinstance(value, str):
            # Special formatting for certain fields
            if key == "link" and value.startswith(("http://", "https://")):
                return f'<a href="{escape(value)}" target="_blank">{escape(value)}</a>'
            elif key == "published" or "date" in key.lower():
                return f'<span class="json-string" title="Date/Time">{escape(value)}</span>'
            elif len(value) > 200:  # Long text content
                return f'<div class="long-text"><span class="json-string">{escape(value)}</span></div>'
            else:
                return f'<span class="json-string">{escape(value)}</span>'
        elif isinstance(value, list):
            if not value:
                return "<em>empty list</em>"

            # Special handling for tags
            if key == "tags" and all(isinstance(item, str) for item in value):
                tags_html = "".join(
                    [f'<span class="tag">{escape(tag)}</span>' for tag in value]
                )
                return f'<div class="tags">{tags_html}</div>'

            # Regular list handling
            items = []
            for i, item in enumerate(value):
                if isinstance(item, (dict, list)):
                    items.append(
                        f'<div class="array-item"><strong>Item {i+1}:</strong><br>{self.format_value(item)}</div>'
                    )
                else:
                    items.append(
                        f'<div class="array-item">{self.format_value(item)}</div>'
                    )
            return "".join(items)
        elif isinstance(value, dict):
            return self.format_object(value)
        else:
            return f'<span class="json-string">{escape(str(value))}</span>'

    def format_object(self, obj: Dict[str, Any]) -> str:
        """Format a dictionary object as nested HTML."""
        html_parts = ['<div class="nested-object">']

        for key, value in obj.items():
            html_parts.append(
                f"""
                <div class="field">
                    <span class="field-name">{escape(key)}:</span>
                    <span class="field-value">{self.format_value(value, key)}</span>
                </div>
            """
            )

        html_parts.append("</div>")
        return "".join(html_parts)

    def convert_jsonl_to_html(self, input_file: Path, output_file: Path = None) -> str:
        """Convert JSONL file to HTML."""
        if output_file is None:
            output_file = input_file.with_suffix(".html")

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            records = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue

            if not records:
                raise ValueError("No valid JSON records found")

            # Generate HTML
            html_content = self.generate_html(records, input_file.name)

            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(output_file)

        except Exception as e:
            raise Exception(f"Error converting file: {e}")

    def generate_html(self, records: List[Dict[str, Any]], filename: str) -> str:
        """Generate complete HTML document from records."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"    <title>JSONL Data - {filename}</title>",
            self.get_css_styles(),
            "</head>",
            "<body>",
            '    <div class="container">',
            '        <div class="header">',
            f"            <h1>JSONL Data: {escape(filename)}</h1>",
            f"            <p>Generated on {timestamp}</p>",
            "        </div>",
            f'        <div class="stats">',
            f"            <h3>Document Statistics</h3>",
            f"            <p><strong>{len(records)}</strong> records processed</p>",
            "        </div>",
        ]

        # Add each record
        for i, record in enumerate(records, 1):
            title = self.get_record_title(record, i)
            html_parts.extend(
                [
                    f'        <div class="record" id="record-{i}">',
                    f'            <div class="record-title">{title}</div>',
                    self.format_object(record),
                    "        </div>",
                ]
            )

        html_parts.extend(
            [
                '        <div class="metadata">',
                f"            <p><em>Converted from {escape(filename)} on {timestamp}</em></p>",
                "        </div>",
                "    </div>",
                "</body>",
                "</html>",
            ]
        )

        return "\n".join(html_parts)

    def get_record_title(self, record: Dict[str, Any], index: int) -> str:
        """Generate a title for a record based on its content."""
        # Try common title fields
        for field in ["title", "name", "subject", "headline", "summary"]:
            if field in record and record[field]:
                title = str(record[field])
                if len(title) > 100:
                    title = title[:97] + "..."
                return f"Record {index}: {escape(title)}"

        # If no title field, use first string field
        for key, value in record.items():
            if isinstance(value, str) and value.strip():
                title = str(value)
                if len(title) > 100:
                    title = title[:97] + "..."
                return f"Record {index}: {escape(title)}"

        return f"Record {index}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSONL files to formatted HTML documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jsonl_to_html.py data.jsonl
  python jsonl_to_html.py data.jsonl -o output.html
  python jsonl_to_html.py data.jsonl --style modern
  python jsonl_to_html.py data.jsonl --style minimal -o simple.html
        """,
    )

    parser.add_argument("input_file", type=str, help="Input JSONL file path")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output HTML file path (default: input_file.html)",
    )

    parser.add_argument(
        "--style",
        choices=["modern", "classic", "minimal"],
        default="modern",
        help="HTML styling mode (default: modern)",
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{input_path}' is not a file")
        sys.exit(1)

    # Set output path
    output_path = Path(args.output) if args.output else None

    try:
        # Convert file
        converter = JsonlToHtmlConverter(style_mode=args.style)
        output_file = converter.convert_jsonl_to_html(input_path, output_path)

        print(f"✅ Successfully converted '{input_path}' to '{output_file}'")
        print(f"🎨 Style: {args.style}")

        # Show file size info
        input_size = input_path.stat().st_size
        output_size = Path(output_file).stat().st_size
        print(f"📊 Input: {input_size:,} bytes → Output: {output_size:,} bytes")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
