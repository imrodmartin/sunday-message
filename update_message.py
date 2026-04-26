#!/usr/bin/env python3
"""
update_message.py
Replaces the title and scripture markers inside index.html.
Usage: python3 update_message.py <title> <scripture>
"""
import sys
import re

def update_html(title: str, scripture: str, html_path: str = "index.html") -> None:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"<!-- TITLE_START -->.*?<!-- TITLE_END -->",
        f"<!-- TITLE_START -->{title}<!-- TITLE_END -->",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<!-- SCRIPTURE_START -->.*?<!-- SCRIPTURE_END -->",
        f"<!-- SCRIPTURE_START -->{scripture}<!-- SCRIPTURE_END -->",
        content,
        flags=re.DOTALL,
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated: {title!r} | {scripture!r}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 update_message.py <title> <scripture>")
        sys.exit(1)
    update_html(sys.argv[1], sys.argv[2])
