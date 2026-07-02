#!/usr/bin/env python3
"""mwtge_lookup.py — search the MWTGe English text for clauses about an MW item.

Usage:
  mwtge_lookup.py <item-id>           # find clauses mentioning item, e.g. "1.6"
  mwtge_lookup.py <item-id> --context # include ±3 lines around each match
  mwtge_lookup.py <keyword>           # free-text search
  mwtge_lookup.py --item-list         # list all item IDs found

The MWTGe text is pre-extracted at:
  /app/bootcamps/MW01-RSE-Bootcamp/MW01-Technical-Guidelines/MWTGe_English_text.txt
"""

import argparse
import os
import re
import sys
from pathlib import Path

MWTGE_PATH = Path("/app/bootcamps/MW01-RSE-Bootcamp/MW01-Technical-Guidelines/MWTGe_English_text.txt")


def find_lines(text: str, pattern: re.Pattern, context: int = 0) -> list[tuple[int, str]]:
    """Return list of (line_no, snippet). If context>0, include ±N lines."""
    lines = text.splitlines()
    results = []
    seen_blocks = set()
    for i, line in enumerate(lines):
        if pattern.search(line):
            block_start = max(0, i - context)
            block_end = min(len(lines), i + context + 1)
            if (block_start, block_end) in seen_blocks:
                continue
            seen_blocks.add((block_start, block_end))
            snippet = "\n".join(lines[block_start:block_end])
            results.append((i + 1, snippet))
    return results


def find_item_blocks(text: str, item_id: str, context: int = 3) -> list[tuple[str, str]]:
    """Find structured sections about a specific MW item (e.g. '1.6')."""
    lines = text.splitlines()
    item_pat = re.compile(rf"\b{item_id}\b\s")
    # Find lines mentioning the item, then group adjacent matches into a section
    matches = []
    seen_starts = set()
    for i, line in enumerate(lines):
        if item_pat.search(line) or f"item {item_id}" in line.lower() or f"items {item_id}" in line.lower():
            # find a reasonable block: from previous blank-line-2 to next blank-line-2
            block_start = i
            for j in range(i - 1, max(0, i - 30), -1):
                if lines[j].strip() == "" and j < i - 1:
                    block_start = j + 1
                    break
                block_start = j
            block_end = i + 1
            for j in range(i + 1, min(len(lines), i + 80)):
                if lines[j].strip() == "" and j > i + 5:
                    block_end = j
                    break
                block_end = j + 1
            if (block_start, block_end) in seen_starts:
                continue
            seen_starts.add((block_start, block_end))
            matches.append((f"lines {block_start + 1}-{block_end}", "\n".join(lines[block_start:block_end]).strip()))
    return matches


def list_all_items(text: str) -> list[str]:
    """Find all unique MW item IDs mentioned."""
    pat = re.compile(r"\b(\d+\.\d+)\b\s+(Alteration|Erection|Removal|Drainage|Supporting|Internal|Protective|Canopy|Strengthening|Other|Construction|Addition)")
    items = set()
    for m in pat.finditer(text):
        items.add(m.group(1))
    return sorted(items, key=lambda x: tuple(int(p) for p in x.split(".")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="MW item id (e.g. 1.6) or keyword")
    ap.add_argument("--context", type=int, default=2, help="Lines of context")
    ap.add_argument("--item-list", action="store_true", help="List all MW item IDs")
    ap.add_argument("--max", type=int, default=10, help="Max results to show")
    args = ap.parse_args()

    if not MWTGE_PATH.exists():
        print(f"❌ MWTGe text not found: {MWTGE_PATH}", file=sys.stderr)
        return 1

    text = MWTGE_PATH.read_text()

    if args.item_list:
        items = list_all_items(text)
        print(f"MW items found in MWTGe text: {len(items)}")
        for it in items[:50]:
            print(f"  {it}")
        if len(items) > 50:
            print(f"  … and {len(items) - 50} more")
        return 0

    if not args.query:
        print("❌ query required. Try: `mwtge_lookup.py --item-list`", file=sys.stderr)
        return 2

    # If query looks like a number.number, do structured item search
    if re.match(r"^\d+\.\d+$", args.query):
        blocks = find_item_blocks(text, args.query, args.context)
        if not blocks:
            # fallback to plain search
            pat = re.compile(re.escape(args.query))
            blocks = [(f"line {ln}", snippet) for ln, snippet in find_lines(text, pat, args.context)]
        print(f"## MWTGe clauses about item {args.query}")
        print(f"({len(blocks)} block(s) found)\n")
        for label, snippet in blocks[:args.max]:
            print(f"### {label}")
            print(snippet)
            print()
        if len(blocks) > args.max:
            print(f"… and {len(blocks) - args.max} more (use --max to see more)")
        return 0

    # Free-text keyword search
    pat = re.compile(re.escape(args.query), re.IGNORECASE)
    results = find_lines(text, pat, args.context)
    print(f"## MWTGe matches for: {args.query}")
    print(f"({len(results)} block(s) found)\n")
    for ln, snippet in results[:args.max]:
        print(f"### line {ln}")
        print(snippet)
        print()
    if len(results) > args.max:
        print(f"… and {len(results) - args.max} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())