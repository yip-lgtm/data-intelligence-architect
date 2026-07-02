#!/usr/bin/env python3
"""course_read.py — read & pretty-print a course .md from mae-cuhk.

Usage:
  course_read.py <course-code>                # print full course .md
  course_read.py <course-code> --summary      # just header + key topics
  course_read.py <course-code> --topic "PID"   # grep for topic
"""

import argparse
import sys
from pathlib import Path

MAE_CUHK = Path("/app/bootcamps/msc-ire/mae-cuhk/courses")


def find_course(code: str) -> Path | None:
    """Find course .md by code (case-insensitive, searches all subdirs)."""
    code_upper = code.upper().strip()
    for sub in MAE_CUHK.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if f.suffix == ".md" and f.stem.upper() == code_upper:
                return f
    return None


def find_course_in_overview(code: str) -> str | None:
    """Search COURSE_LISTS.md for code reference."""
    cl = MAE_CUHK / "COURSE_LISTS.md"
    if not cl.exists():
        return None
    for line in cl.read_text().splitlines():
        if code.upper() in line.upper():
            return line.strip()
    return None


def render_summary(text: str) -> str:
    """Extract first 60 lines (header + topics + key info)."""
    lines = text.splitlines()
    out = []
    in_section = True
    blank_count = 0
    for i, line in enumerate(lines[:80]):
        out.append(line)
        if not line.strip():
            blank_count += 1
            if blank_count >= 2 and i > 15:
                break
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", help="course code, e.g. MAEG1020, ENGG1110")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--topic", help="grep for this topic inside the course")
    args = ap.parse_args()

    path = find_course(args.code)
    if not path:
        print(f"❌ course {args.code} not found in mae-cuhk/courses/", file=sys.stderr)
        # try COURSE_LISTS.md
        ref = find_course_in_overview(args.code)
        if ref:
            print(f"   (but found in COURSE_LISTS.md: {ref})", file=sys.stderr)
        print(f"   Try one of: MAEG1020, ENGG1110, MAEG2020", file=sys.stderr)
        return 2

    text = path.read_text()
    if args.topic:
        pat = args.topic.lower()
        matching = [l for l in text.splitlines() if pat in l.lower()]
        print(f"## {args.code}: matches for '{args.topic}' ({len(matching)} lines)")
        for l in matching[:30]:
            print(f"  {l}")
        return 0

    if args.summary:
        print(render_summary(text))
        print(f"\n…(full course: {path}, {len(text.splitlines())} lines total)")
    else:
        print(text)

    print(f"\n— from {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())