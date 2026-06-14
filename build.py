#!/usr/bin/env python3
"""
Build script to convert markdown to HTML with table of contents.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""
import markdown
import re
import hashlib
from datetime import datetime
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class DicierPreprocessor(Preprocessor):
    """Convert {dicier:CODE} syntax to <span class="dicier">CODE</span>"""
    
    def run(self, lines):
        new_lines = []
        for line in lines:
            # Replace {dicier:CODE} with <span class="dicier">CODE</span>
            line = re.sub(r'\{dicier:([^}]+)\}', r'<span class="dicier">\1</span>', line)
            new_lines.append(line)
        return new_lines

class DicierExtension(Extension):
    """Markdown extension for Dicier font support"""
    
    def extendMarkdown(self, md):
        md.preprocessors.register(DicierPreprocessor(md), 'dicier', 175)

def generate_cache_buster():
    """Generate a cache buster based on current timestamp."""
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]

def fix_toc_with_dicier(toc_html, html_content):
    """Fix TOC to include dicier spans from headers.
    
    The TOC extension strips HTML from header text, so we need to extract
    the actual header content (which includes dicier spans) and update the
    TOC links to match.
    """
    # Extract all headers with their IDs and content from the generated HTML
    # Use DOTALL flag to handle headers that may span multiple lines
    headers = re.findall(r'<h([1-6]) id="([^"]+)">(.+?)</h\1>', html_content, re.DOTALL)
    
    # Update TOC links to use the same content as the headers
    for level, header_id, content in headers:
        # Find and replace TOC links with the full header content (including HTML)
        # Pattern explanation:
        # - <a href="#header_id">  : opening anchor tag with the specific header ID
        # - [^<]*                  : any text before nested tags
        # - (?:<[^>]*>[^<]*</[^>]*>)* : zero or more nested HTML tags (e.g., <span>text</span>)
        # - [^<]*                  : any text after nested tags
        # - </a>                   : closing anchor tag
        # This pattern matches the entire TOC link so we can replace it with the correct header content
        pattern = r'<a href="#{}">[^<]*(?:<[^>]*>[^<]*</[^>]*>)*[^<]*</a>'.format(re.escape(header_id))
        replacement = '<a href="#{}">{}</a>'.format(header_id, content)
        toc_html = re.sub(pattern, replacement, toc_html)
    
    return toc_html

def add_decorative_headers(html_content):
    """Add decorative SVG headers after H1 and H2 elements."""
    # Add decorative header after H1 tags
    html_content = re.sub(
        r'</h1>',
        r'</h1>\n<img src="/assets/DecorativeHeaderLarge.svg" alt="" class="decorative-header-large" aria-hidden="true">',
        html_content
    )
    
    # Add decorative header after H2 tags
    html_content = re.sub(
        r'</h2>',
        r'</h2>\n<img src="/assets/DecorativeHeaderSmall.svg" alt="" class="decorative-header-small" aria-hidden="true">',
        html_content
    )
    
    return html_content

def build_html():
    """Build the HTML file from markdown content."""
    # Read markdown content
    with open('content.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with extensions
    md = markdown.Markdown(extensions=[
        'toc',  # Table of contents
        'extra',  # Extra features like tables, code blocks, etc.
        'nl2br',  # New line to break
        DicierExtension(),  # Custom Dicier font support
    ])
    
    html_content = md.convert(md_content)
    toc_html = md.toc
    
    # Fix TOC to include dicier spans from headers
    toc_html = fix_toc_with_dicier(toc_html, html_content)
    
    # Add decorative headers after H1 and H2 elements
    html_content = add_decorative_headers(html_content)
    
    # Generate cache buster for CSS
    cache_buster = generate_cache_buster()
    
    # Read HTML template
    with open('template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # Replace placeholders with actual content
    html_output = html_template.format(
        cache_buster=cache_buster,
        toc_html=toc_html,
        html_content=html_content
    )
    
    # Write the HTML file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✓ Built index.html with cache buster: {cache_buster}")

if __name__ == '__main__':
    build_html()
