#!/usr/bin/env python3
"""week_content.py — full week-N content for the 24-Week Bootcamp.

Usage:
  week_content.py <week-number>           # show this week's full content
  week_content.py --current               # auto-detect current week from today
  week_content.py 5 --json                # machine-readable

Pulls from progress.md (week-by-week table) + course .md files.
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

PROGRESS_PATH = Path("/app/bootcamps/msc-ire/24_Week_Weekend_Bootcamp/progress.md")
MAE_CUHK = Path("/app/bootcamps/msc-ire/mae-cuhk/courses")
BOOTCAMP_START = datetime.date(2026, 6, 13)
TOTAL_WEEKS = 24


def parse_weeks(text: str) -> list[dict]:
    weeks = []
    for line in text.splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\s*\|"
            r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(✅|⏳|⬜|🔵|)\s*\|",
            line,
        )
        if m:
            weeks.append({
                "week": int(m.group(1)),
                "date": m.group(2),
                "phase": int(m.group(3)),
                "focus": m.group(4).strip(),
                "sim_update": m.group(5).strip(),
                "status": m.group(7) or "⬜",
                "notes": m.group(6).strip(),
            })
    return weeks


def extract_course_codes(focus: str) -> list[str]:
    """Pull course codes like MAEG2020, ENGG1110 from focus text."""
    return re.findall(r"[A-Z]{4}\s*\d{4}", focus)


def load_course_summary(code: str) -> dict | None:
    """Quick header + topics from a course .md."""
    code_upper = code.upper().strip()
    for sub in MAE_CUHK.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if f.suffix == ".md" and f.stem.upper() == code_upper:
                text = f.read_text()
                title = ""
                for line in text.splitlines()[:5]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                return {"code": code_upper, "title": title, "path": str(f)}
    return None


def render_week(week: dict, include_courses: bool = True) -> str:
    out = []
    out.append(f"## Week {week['week']}/24 — Phase {week['phase']}")
    out.append(f"📅 Date: {week['date']}")
    out.append(f"📚 Focus: {week['focus']}")
    out.append(f"🔧 Simulator update: {week['sim_update']}")
    out.append(f"📊 Status: {week['status']}")
    if week.get("notes"):
        out.append(f"📝 Notes: {week['notes']}")

    if include_courses:
        codes = extract_course_codes(week["focus"])
        if codes:
            out.append("")
            out.append("### Courses referenced:")
            for code in codes:
                summary = load_course_summary(code)
                if summary:
                    out.append(f"  • **{summary['code']}** — {summary['title']}")
                    out.append(f"    📁 {summary['path']}")
                else:
                    out.append(f"  • **{code}** — (course .md not found in mae-cuhk)")

    out.append("")
    out.append("### Suggested weekend plan")
    out.append("- **Sat AM** (3-4 hrs): Theory — read course .md, take notes")
    out.append("- **Sat PM** (3-4 hrs): Practice — apply to simulator")
    out.append("- **Sun AM** (2-3 hrs): Reflection — update progress.md")
    out.append("- **Sun PM**: Light review or rest")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("week", nargs="?", type=int, help="week number 1-24")
    ap.add_argument("--current", action="store_true", help="use current week")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-courses", action="store_true")
    args = ap.parse_args()

    if not PROGRESS_PATH.exists():
        print(f"❌ progress.md not found: {PROGRESS_PATH}", file=sys.stderr)
        return 1

    text = PROGRESS_PATH.read_text()
    weeks = parse_weeks(text)

    if args.current:
        today = datetime.date.today()
        days = (today - BOOTCAMP_START).days
        cw = (days // 7) + 1
        if cw < 1:
            print("⏳ Bootcamp hasn't started yet (start: 2026-06-13)")
            return 0
        if cw > TOTAL_WEEKS:
            print("🎉 All 24 weeks completed!")
            return 0
        target = cw
    elif args.week:
        target = args.week
    else:
        print("❌ provide a week number or --current", file=sys.stderr)
        return 2

    week = next((w for w in weeks if w["week"] == target), None)
    if not week:
        print(f"❌ week {target} not in progress.md", file=sys.stderr)
        return 2

    if args.json:
        out = dict(week)
        if not args.no_courses:
            out["courses"] = []
            for code in extract_course_codes(week["focus"]):
                cs = load_course_summary(code)
                if cs:
                    out["courses"].append(cs)
        print(json.dumps(out, indent=2))
    else:
        print(render_week(week, include_courses=not args.no_courses))
    return 0


if __name__ == "__main__":
    sys.exit(main())