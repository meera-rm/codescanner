"""
add_timestamps.py
-----------------
Injects SpecStory-compatible frontmatter timestamps into .md conversation
files that don't already have them.

Usage (run from your project root):
    python add_timestamps.py

Reads files from:  .specstory/history/
Skips files that already start with ---
Derives timestamp from filename prefix (e.g. 1781287030025_)
Falls back to current UTC time if no prefix found.
"""

import os
import re
from datetime import datetime, timezone

HISTORY_DIR = ".specstory/history"


def extract_timestamp(filename: str) -> str:
    """Parse Unix-ms prefix from filename, return ISO-8601 string."""
    match = re.match(r'^(\d{13})_', filename)
    if match:
        ts_ms = int(match.group(1))
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    # fallback: current time
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_frontmatter(date_str: str, filename: str) -> str:
    # derive a clean title from filename (strip prefix + extension)
    title = re.sub(r'^\d+_', '', filename).replace('.md', '').replace('_', ' ').title()
    return (
        "---\n"
        f"created_at: {date_str}\n"
        f"title: {title}\n"
        "source: claude-code\n"
        "project: codescanner\n"
        "---\n\n"
    )


def process_files(history_dir: str) -> None:
    if not os.path.isdir(history_dir):
        print(f"❌  Directory not found: {history_dir}")
        print("    Make sure you run this script from your project root.")
        print("    Expected structure: .specstory/history/*.md")
        return

    files = sorted(f for f in os.listdir(history_dir) if f.endswith(".md"))

    if not files:
        print(f"No .md files found in {history_dir}")
        return

    updated = 0
    skipped = 0

    for filename in files:
        filepath = os.path.join(history_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            print(f"  skip  {filename}")
            skipped += 1
            continue

        date_str = extract_timestamp(filename)
        frontmatter = build_frontmatter(date_str, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + content)

        print(f"  ✓     {filename}  →  {date_str}")
        updated += 1

    print(f"\nDone — {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    process_files(HISTORY_DIR)
