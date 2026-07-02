#!/usr/bin/env python3
"""status.py — unified bootcamp status reporter.

Parses progress files for each registered bootcamp and prints:
- Completion percentage
- Current focus / next target
- Pending items list
- Last activity timestamp

Usage:
  status.py                    # all bootcamps
  status.py mw01               # one bootcamp
  status.py mw01 --json        # machine-readable
  status.py --all --short      # one-line per bootcamp (for Telegram)
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "config", "bootcamps.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


# --- MW01 progress parsing -------------------------------------------------

def parse_mw01_progress(path: Path) -> dict:
    """Parse progress/Bootcamp_Progress.md markdown table."""
    result = {
        "bootcamp": "mw01",
        "items": [],
        "summary_line": None,
        "next_targets": [],
    }
    if not path.exists():
        result["error"] = f"progress file not found: {path}"
        return result

    text = path.read_text()
    lines = text.splitlines()

    # Parse markdown table rows
    # Format: | 2026-05-15 | MW 1.6 Protective Barrier | ✅ Complete | projects/... | 100% |
    for line in lines:
        m = re.match(
            r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*MW\s*([\d.]+)\s+([^|]+?)\s*\|\s*"
            r"(✅\s*Complete|⏳\s*Partial|⏳\s*Not started|🔵\s*In progress|"
            r"✅\s*Done|⏳\s*Draft done|[✅⏳⬜🔵]\s*[A-Za-z][^|]*)\s*\|",
            line,
        )
        if m:
            status_full = m.group(4).strip()
            status_icon = status_full.split()[0] if status_full else ""
            result["items"].append({
                "date": m.group(1),
                "mw_id": m.group(2),
                "name": m.group(3).strip(),
                "status": status_icon,
                "status_text": status_full,
                "raw": line.strip(),
            })

    # Parse summary lines — strip leading markdown bullets/headings/em-dashes
    for line in lines:
        if "Completed:" in line or "完成" in line:
            cleaned = line.strip()
            # strip leading - * # characters and whitespace
            while cleaned and cleaned[0] in "-*# \t":
                cleaned = cleaned[1:]
            cleaned = cleaned.strip()
            # Collapse markdown emphasis: handle "**Completed:**", "Completed:**",
            # or any stray ** anywhere in the string.
            import re as _re
            cleaned = _re.sub(r"\*\*+", "", cleaned)
            cleaned = cleaned.strip()
            result["summary_line"] = cleaned
            break

    # Parse next targets
    in_next = False
    for line in lines:
        if "Next Target" in line or "下一個" in line:
            in_next = True
            continue
        if in_next:
            stripped = line.strip()
            if stripped.startswith("-"):
                target = stripped.lstrip("- ").strip()
                # ignore blank or separator lines
                if target and target not in ("", "---"):
                    result["next_targets"].append(target)
            elif stripped.startswith("#") or not stripped:
                if stripped.startswith("#"):
                    in_next = False

    return result


# --- MSC-IRE progress parsing ---------------------------------------------

def parse_msc_ire_progress(path: Path, start_date: datetime.date,
                           total_weeks: int = 24) -> dict:
    """Parse progress.md table; compute current week from start_date."""
    result = {
        "bootcamp": "msc-ire",
        "today": datetime.date.today().isoformat(),
        "current_week": None,
        "current_phase": None,
        "weeks": [],
        "phases": [],
    }
    if not path.exists():
        result["error"] = f"progress file not found: {path}"
        return result

    text = path.read_text()
    lines = text.splitlines()

    # Parse week-by-week table
    for line in lines:
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\s*\|"
            r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(✅|⏳|⬜|🔵|)\s*\|",
            line,
        )
        if m:
            result["weeks"].append({
                "week": int(m.group(1)),
                "date": m.group(2),
                "phase": int(m.group(3)),
                "focus": m.group(4).strip(),
                "sim_update": m.group(5).strip(),
                "status": m.group(7) or "⬜",
                "notes": m.group(6).strip(),
            })

    # Compute current week from start_date
    today = datetime.date.today()
    days = (today - start_date).days
    cw = (days // 7) + 1
    if cw < 1:
        result["current_week"] = 0
        result["current_phase"] = 0
    elif cw > total_weeks:
        result["current_week"] = total_weeks + 1
        result["current_phase"] = 5
    else:
        result["current_week"] = cw
        if cw <= 6:
            result["current_phase"] = 1
        elif cw <= 12:
            result["current_phase"] = 2
        elif cw <= 18:
            result["current_phase"] = 3
        else:
            result["current_phase"] = 4

    return result


# --- Pretty-print ----------------------------------------------------------

def fmt_mw01_short(data: dict) -> str:
    completed = sum(1 for i in data["items"] if i.get("status", "").startswith("✅"))
    total = len(data["items"])
    pct = int(100 * completed / total) if total else 0
    return f"🏗️ MW01: {completed}/{total} ({pct}%)"


def fmt_msc_ire_short(data: dict) -> str:
    cw = data["current_week"]
    cp = data["current_phase"]
    total = data.get("weeks") and len(data["weeks"]) or 24
    done = sum(1 for w in data["weeks"] if (w.get("status") or "").startswith("✅"))
    if cw and 1 <= cw <= 24:
        current_week = next((w for w in data["weeks"] if w["week"] == cw), None)
        focus = current_week["focus"] if current_week else "?"
        return f"🤖 MSC-IRE: Week {cw}/24 — {focus}"
    return f"🤖 MSC-IRE: {cw}/24 (phase {cp})"


def fmt_mw01_full(data: dict) -> str:
    out = ["🏗️ **MW01 RSE Bootcamp**", ""]
    if "error" in data:
        out.append(f"⚠️ {data['error']}")
        return "\n".join(out)
    completed = sum(1 for i in data["items"] if i.get("status", "").startswith("✅"))
    partial = sum(1 for i in data["items"] if (i.get("status") or "").startswith("⏳"))
    total = len(data["items"])
    pct = int(100 * completed / total) if total else 0
    out.append(f"📊 Progress: {completed}/{total} complete ({pct}%)")
    if partial:
        out.append(f"⏳ In progress: {partial}")
    if data.get("summary_line"):
        out.append(f"   {data['summary_line']}")
    if data.get("next_targets"):
        out.append("")
        out.append("🎯 **Next targets:**")
        for t in data["next_targets"][:5]:
            out.append(f"  • {t}")
    if data.get("items"):
        out.append("")
        out.append("📋 **Recent items:**")
        for it in data["items"][-6:]:
            out.append(f"  {it['status']} MW {it['mw_id']} — {it['name']} ({it['date']})")
    return "\n".join(out)


def fmt_msc_ire_full(data: dict) -> str:
    out = ["🤖 **24-Week Bootcamp (PolyU MSc IRE)**", ""]
    if "error" in data:
        out.append(f"⚠️ {data['error']}")
        return "\n".join(out)
    cw = data["current_week"]
    cp = data["current_phase"]
    today = data["today"]
    if cw == 0:
        out.append("📅 Not started yet (before 2026-06-13)")
    elif cp == 5:
        out.append("🎉 Completed all 24 weeks!")
    elif cw and 1 <= cw <= 24:
        current_week = next((w for w in data["weeks"] if w["week"] == cw), None)
        phase_name = ""
        # crude phase name lookup
        phase_map = {1: "Phase 1: Foundations", 2: "Phase 2: Mechatronics & Control",
                     3: "Phase 3: Robotics & Advanced", 4: "Phase 4: Integration & FYP"}
        phase_name = phase_map.get(cp, "")
        out.append(f"📅 Today: {today}  →  **Week {cw}/24** ({phase_name})")
        if current_week:
            out.append(f"📚 Focus: {current_week['focus']}")
            out.append(f"🔧 Simulator update: {current_week['sim_update']}")
    # upcoming
    upcoming = [w for w in data["weeks"] if (w.get("status") or "").startswith("⬜")][:3]
    if upcoming:
        out.append("")
        out.append("🎯 **Upcoming weeks:**")
        for w in upcoming:
            out.append(f"  W{w['week']} ({w['date']}) — {w['focus']}")
    return "\n".join(out)


# --- main ------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bootcamp", nargs="?", help="mw01 or msc-ire (default: all)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--short", action="store_true")
    args = ap.parse_args()

    cfg = load_config()["bootcamps"]
    selected = []
    if args.bootcamp:
        if args.bootcamp not in cfg:
            print(f"❌ unknown bootcamp: {args.bootcamp}", file=sys.stderr)
            print(f"   available: {', '.join(cfg.keys())}", file=sys.stderr)
            return 2
        selected.append((args.bootcamp, cfg[args.bootcamp]))
    else:
        selected = list(cfg.items())

    results = {}
    for name, bcfg in selected:
        path = Path(bcfg["path"]) / bcfg["progressFile"]
        if name == "mw01":
            results[name] = parse_mw01_progress(path)
        elif name == "msc-ire":
            start = datetime.date.fromisoformat(bcfg["startDate"])
            total = bcfg.get("totalWeeks", 24)
            results[name] = parse_msc_ire_progress(path, start, total)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return 0

    if args.short:
        for name, data in results.items():
            if name == "mw01":
                print(fmt_mw01_short(data))
            elif name == "msc-ire":
                print(fmt_msc_ire_short(data))
        return 0

    for name, data in results.items():
        print("")
        if name == "mw01":
            print(fmt_mw01_full(data))
        elif name == "msc-ire":
            print(fmt_msc_ire_full(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())