#!/usr/bin/env python3

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


def sanitize_title(title):
    """Convert title to lowercase and replace spaces/special chars with hyphens."""
    # Convert to lowercase and replace spaces with hyphens
    sanitized = re.sub(r'[^\w\s-]', '', title.lower())
    sanitized = re.sub(r'[\s_-]+', '-', sanitized)
    return sanitized.strip('-')


def generate_front_matter(title):
    """Generate the front matter for the blog post."""
    # Get current datetime with timezone
    now = datetime.now().astimezone()
    date_str = now.strftime('%Y-%m-%dT%H:%M:%S%z')
    # Format timezone with colon (e.g., -05:00)
    date_str = date_str[:-2] + ':' + date_str[-2:]
    
    return f"""---
date: '{date_str}'
draft: true
title: '{title}'
---

"""


def create_blog_post(dest_folder, title):
    """Create a new blog post with the given folder and title."""
    # Get current date for folder name
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Sanitize title for folder name
    sanitized_title = sanitize_title(title)
    
    # Create folder name: YYYY-MM-DD_title
    folder_name = f"{current_date}_{sanitized_title}"
    
    # Create full path
    blog_path = Path(dest_folder) / folder_name
    
    # Create directory if it doesn't exist
    blog_path.mkdir(parents=True, exist_ok=True)
    
    # Create index.md file
    index_file = blog_path / "index.md"
    
    # Generate front matter
    front_matter = generate_front_matter(title)
    
    # Write to file
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(front_matter)
    
    print(f"Created blog post: {index_file}")
    return index_file


def main():
    parser = argparse.ArgumentParser(description='Scaffold a new blog post')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # New command
    new_parser = subparsers.add_parser('new', help='Create a new blog post')
    new_parser.add_argument('--dest-folder', required=True, 
                           help='Destination folder for the blog post')
    new_parser.add_argument('--title', required=True,
                           help='Title of the blog post')
    
    args = parser.parse_args()
    
    if args.command == 'new':
        create_blog_post(args.dest_folder, args.title)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
