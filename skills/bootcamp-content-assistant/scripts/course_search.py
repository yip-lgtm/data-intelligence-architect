#!/usr/bin/env python3
"""course_search.py — search mae-cuhk courses by keyword.

Usage:
  course_search.py "PID control"
  course_search.py "robotics" --category major-required
  course_search.py "PID" --limit 5
"""

import argparse
import sys
from pathlib import Path

MAE_CUHK = Path("/app/bootcamps/msc-ire/mae-cuhk/courses")


def iter_courses(category: str | None = None):
    """Yield (Path, code, title, category)."""
    for sub in MAE_CUHK.iterdir():
        if not sub.is_dir():
            continue
        cat = sub.name
        if category and cat != category:
            continue
        for f in sub.iterdir():
            if f.suffix != ".md":
                continue
            if f.stem in ("COURSE_TEMPLATE", "README"):
                continue
            # Extract title from first heading
            text = f.read_text()
            title = ""
            for line in text.splitlines()[:5]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            yield f, f.stem, title, cat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="search keyword")
    ap.add_argument("--category", help="filter by category (e.g. foundation, major-required)")
    ap.add_argument("--limit", type=int, default=10, help="max results")
    args = ap.parse_args()

    q = args.query.lower()
    results = []
    for path, code, title, cat in iter_courses(args.category):
        text = path.read_text().lower()
        score = text.count(q)
        if score > 0:
            results.append((score, path, code, title, cat))

    results.sort(key=lambda x: -x[0])
    print(f"## Courses matching '{args.query}'")
    if args.category:
        print(f"   category: {args.category}")
    print(f"   {len(results)} match(es)\n")

    for score, path, code, title, cat in results[:args.limit]:
        print(f"  [{score:3d}] {code:12s}  {cat:24s}  {title}")
        print(f"        {path.relative_to(MAE_CUHK.parent.parent)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())