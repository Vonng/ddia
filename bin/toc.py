#!/usr/bin/env python3
"""
TOC Generator for DDIA book
Usage: python toc.py <lang> <depth> [output_file]
Example: python toc.py zh 2
         python toc.py en 3 en-toc.md
"""

import os
import sys
import re
from pathlib import Path


def extract_front_matter_title(content):
    """Extract title from Hugo front matter"""
    lines = content.split('\n')
    in_front_matter = False
    for line in lines:
        if line.strip() == '---':
            if not in_front_matter:
                in_front_matter = True
            else:
                break
        elif in_front_matter and line.startswith('title:'):
            # Extract title, removing quotes
            title = line.split(':', 1)[1].strip()
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            elif title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            return title
    return None


def extract_headings(content, max_depth):
    """Extract headings up to specified depth from markdown content
    
    max_depth=1 -> extract H2 only
    max_depth=2 -> extract H2-H3
    max_depth=3 -> extract H2-H4
    max_depth=4 -> extract H2-H5
    """
    headings = []
    lines = content.split('\n')
    
    # Skip front matter
    skip_until = 0
    if lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                skip_until = i + 1
                break
    
    for line in lines[skip_until:]:
        # Match markdown headings with optional ID
        # Format: ## Heading Text {#heading-id}
        match = re.match(r'^(#{2,5})\s+(.*?)(?:\s*\{#([\w-]+)\})?$', line)
        if match:
            level = len(match.group(1))
            # max_depth=1 -> extract level 2 only (H2)
            # max_depth=2 -> extract level 2-3 (H2-H3)
            # max_depth=3 -> extract level 2-4 (H2-H4)
            # max_depth=4 -> extract level 2-5 (H2-H5)
            max_level = max_depth + 1
            if level <= max_level:
                heading_text = match.group(2).strip()
                heading_id = match.group(3)
                headings.append({
                    'level': level,  # Keep original level: 2 for H2, 3 for H3, etc.
                    'text': heading_text,
                    'id': heading_id
                })
    
    return headings


def generate_toc_entry(file_name, title, lang, depth, content_dir):
    """Generate TOC entry for a file"""
    entries = []
    
    # Determine URL path
    base_name = file_name.replace('.md', '')
    if lang == 'zh':
        url = f"/{base_name}"
    else:
        url = f"/{lang}/{base_name}"
    
    # Add main entry (level 1)
    entries.append({
        'level': 1,
        'text': f"[{title}]({url})",
        'raw_text': title
    })
    
    # Special case: glossary.md only shows main title (no sub-headings)
    if file_name == 'glossary.md':
        effective_depth = 0  # Don't extract any sub-headings
    else:
        effective_depth = depth - 1  # Adjust depth: user depth 1 = no extraction, 2 = extract H2, etc.
    
    # If effective_depth >= 1, extract headings from file
    if effective_depth >= 1:
        file_path = content_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            headings = extract_headings(content, effective_depth)
            for heading in headings:
                # Create link with anchor
                if heading['id']:
                    anchor_url = f"{url}#{heading['id']}"
                else:
                    # Generate anchor from heading text (simplified)
                    anchor = heading['text'].lower()
                    anchor = re.sub(r'[^\w\s-]', '', anchor)
                    anchor = re.sub(r'\s+', '-', anchor)
                    anchor_url = f"{url}#{anchor}"
                
                # Adjust level: H2 becomes level 2, H3 becomes level 3, etc.
                # This ensures proper indentation under the main entry
                entries.append({
                    'level': heading['level'],
                    'text': f"[{heading['text']}]({anchor_url})",
                    'raw_text': heading['text']
                })
    
    return entries


def format_toc_entries(entries):
    """Format TOC entries with proper indentation"""
    formatted = []
    for entry in entries:
        level = entry['level']
        text = entry['text']
        
        if level == 0:
            # Blank line separator
            formatted.append('')
        elif level == 1:
            # Main entry (chapter/section level)
            formatted.append(f"## {text}")
        elif level == 2:
            # H2 heading
            formatted.append(f"- {text}")
        elif level == 3:
            # H3 heading
            formatted.append(f"    - {text}")
        elif level == 4:
            # H4 heading
            formatted.append(f"        - {text}")
        elif level == 5:
            # H5 heading
            formatted.append(f"            - {text}")
    
    return '\n'.join(formatted)


def check_file_status(file_path, lang):
    """Check if a file exists and add status marker if needed"""
    if not file_path.exists():
        return " (未发布)" if lang == 'zh' else " (未發布)" if lang == 'tw' else " (WIP)"
    
    # Check if file has minimal content (you can adjust this logic)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Simple heuristic: if file has less than 500 characters of actual content, consider it WIP
        # Remove front matter for content check
        lines = content.split('\n')
        if lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    content = '\n'.join(lines[i+1:])
                    break
        
        content_length = len(content.strip())
        if content_length < 500:
            return " (未发布)" if lang == 'zh' else " (未發布)" if lang == 'tw' else " (WIP)"
    
    return ""


def main():
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python toc.py <lang> <depth> [output_file]")
        print("Example: python toc.py zh 2")
        sys.exit(1)
    
    lang = sys.argv[1]
    if lang not in ['zh', 'en', 'tw']:
        print(f"Error: Language must be one of: zh, en, tw")
        sys.exit(1)
    
    try:
        depth = int(sys.argv[2])
        if depth not in [1, 2, 3, 4]:
            raise ValueError
    except ValueError:
        print(f"Error: Depth must be 1, 2, 3, or 4")
        sys.exit(1)
    
    # Determine output file
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    else:
        output_file = f"{lang}.md"
    
    # Get content directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    content_dir = project_root / 'content' / lang
    
    if not content_dir.exists():
        print(f"Error: Content directory {content_dir} does not exist")
        sys.exit(1)
    
    # Define file order
    file_order = [
        'preface.md',
        'ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md',
        'ch7.md', 'ch8.md', 'ch9.md', 'ch10.md', 'ch11.md', 'ch12.md', 'ch13.md',
        'glossary.md',
        'colophon.md'
    ]
    
    # Generate TOC
    all_entries = []
    
    for file_name in file_order:
        file_path = content_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = extract_front_matter_title(content)
            if title:
                entries = generate_toc_entry(file_name, title, lang, depth, content_dir)
                
                # Add status marker to main entry if needed
                status = check_file_status(file_path, lang)
                if status and entries:
                    # Update the first entry (main title) with status
                    entries[0]['text'] = entries[0]['text'].replace(')', f'){status}')
                
                all_entries.extend(entries)
                if entries:  # Add blank line between chapters
                    all_entries.append({'level': 0, 'text': ''})
    
    # Format and write output
    formatted_toc = format_toc_entries(all_entries)
    
    # Clean up extra blank lines
    formatted_toc = re.sub(r'\n{3,}', '\n\n', formatted_toc)
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_toc)
    
    print(f"TOC generated successfully: {output_path}")
    print(f"Language: {lang}, Depth: {depth}")


if __name__ == "__main__":
    main()