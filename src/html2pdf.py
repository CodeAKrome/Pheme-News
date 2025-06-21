#!/usr/bin/env python3
"""
HTML to PDF converter using pdfkit.
Reads HTML from stdin and saves PDF to specified file.
"""

import sys
import pdfkit
import fire
from typing import Optional


def html_to_pdf(output_file: str, options: Optional[dict] = None):
    """
    Convert HTML from stdin to PDF file.
    
    Args:
        output_file: Path to output PDF file
        options: Optional dictionary of wkhtmltopdf options
    """
    try:
        # Read HTML content from stdin
        html_content = sys.stdin.read()
        
        if not html_content.strip():
            print("Error: No HTML content provided via stdin", file=sys.stderr)
            sys.exit(1)
        
        # Default options for better PDF output
        default_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        # Merge with user-provided options if any
        if options:
            default_options.update(options)
        
        # Convert HTML to PDF
        pdfkit.from_string(html_content, output_file, options=default_options)
        
        print(f"Successfully converted HTML to PDF: {output_file}")
        
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}", file=sys.stderr)
        sys.exit(1)


class HTMLToPDFConverter:
    """HTML to PDF converter CLI."""
    
    def convert(self, output_file: str, **kwargs):
        """
        Convert HTML from stdin to PDF.
        
        Args:
            output_file: Output PDF file path
            **kwargs: Additional wkhtmltopdf options (use underscores for hyphens)
        """
        # Convert underscores back to hyphens for wkhtmltopdf options
        options = {k.replace('_', '-'): v for k, v in kwargs.items()} if kwargs else None
        html_to_pdf(output_file, options)


if __name__ == '__main__':
    fire.Fire(HTMLToPDFConverter)
