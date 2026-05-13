#!/usr/bin/env python3
"""
CWE / OWASP keyword search against the reference map.
Usage: python3 cwe-search.py <keyword> [keyword2 ...]
       python3 cwe-search.py sqli
       python3 cwe-search.py broken access
"""

import sys
import os

REFERENCE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "references", "owasp-cwe-map.md"
)


def load_entries(path):
    """Parse table rows from the markdown reference file."""
    entries = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|") or line.startswith("| ---") or line.startswith("| CWE"):
                    continue
                cols = [c.strip() for c in line.strip("|").split("|")]
                if len(cols) >= 3:
                    entries.append(cols)
    except FileNotFoundError:
        print(f"Reference file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return entries


def search(entries, keywords):
    keywords = [k.lower() for k in keywords]
    results = []
    for row in entries:
        row_text = " ".join(row).lower()
        if all(kw in row_text for kw in keywords):
            results.append(row)
    return results


def print_results(results):
    if not results:
        print("  No matches found.")
        return
    for row in results:
        print(f"\n  {row[0]}")
        if len(row) >= 3:
            print(f"  CWEs:     {row[1]}")
            print(f"  Examples: {row[2]}")


def main():
    if len(sys.argv) < 2:
        print("Usage: cwe-search.py <keyword> [keyword2 ...]")
        print("Example: cwe-search.py injection")
        sys.exit(1)

    keywords = sys.argv[1:]
    entries = load_entries(REFERENCE_FILE)
    results = search(entries, keywords)

    print(f"\n  Search: {' '.join(keywords)}")
    print(f"  Matches: {len(results)}")
    print_results(results)
    print()


if __name__ == "__main__":
    main()
