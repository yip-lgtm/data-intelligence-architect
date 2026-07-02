#!/usr/bin/env python3
"""mw_lookup.py — look up an MW item's MWTGe requirements.

Usage:
  mw_lookup.py 1.1               # show requirements for MW item 1.1
  mw_lookup.py 1.1 --references  # also list MWTGe/CoP references
  mw_lookup.py --list            # list all known MW items
  mw_lookup.py --core            # list the 4 core items

Reads from the local MW01-RSE-Bootcamp clone, in particular:
- references/  (MWTGe.pdf, CoP, PNAP)
- projects/    (one folder per MW item)

Outputs Markdown-formatted requirements summary.
"""

import argparse
import os
import sys
from pathlib import Path

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "config", "bootcamps.json")

# Known MW item descriptions (from MWTGe.pdf Class I minor works)
# This is a curated subset; the agent should extend from MWTGe.pdf as needed.
KNOWN_ITEMS = {
    "1.1": {
        "name": "Erection or Alteration of Internal Staircase",
        "class": "I",
        "typical_span": "≤ 6m",
        "typical_load": "1.5 kPa + 1.0 kN/m line",
        "key_checks": [
            "Deflection ≤ span/360",
            "Tread/riser 公式 ≥ 2R + G ≥ 550",
            "Handrail height ≥ 900mm",
            "Open riser opening ≤ 100mm",
        ],
        "coP_refs": ["Concrete 2013", "Steel 2011"],
        "appendix": "VII-§3",
    },
    "1.5": {
        "name": "Removal of Supporting Structure on Cantilevered Slab",
        "class": "I",
        "typical_span": "cantilever 1-2m",
        "typical_load": "3.0 kPa (residential)",
        "key_checks": [
            "Propping sequence — temporary support design",
            "Slab punching shear check at remaining columns",
            "Reinforcement continuity check",
            "Crack width ≤ 0.3mm",
        ],
        "coP_refs": ["Concrete 2013 §6.4"],
        "appendix": "VII-§5",
    },
    "1.6": {
        "name": "Alteration or Removal of Protective Barrier",
        "class": "I",
        "typical_span": "N/A",
        "typical_load": "1.5 kN/m horizontal at handrail",
        "key_checks": [
            "Handrail height ≥ 1100mm (residential) / 1400mm (公共)",
            "Opening ≤ 100mm",
            "Post spacing ≤ 1.5m",
            "Fixing detail check (anchor capacity)",
        ],
        "coP_refs": ["Steel 2011", "Concrete 2013"],
        "appendix": "VII-§6",
    },
    "1.27": {
        "name": "Erection / Alteration / Removal of Canopy",
        "class": "I",
        "typical_span": "≤ 6m projection",
        "typical_load": "Wind (per Wind Effects 2019) + 1.0 kPa",
        "key_checks": [
            "Wind pressure per Wind Effects 2019",
            "Cantilever deflection ≤ L/180",
            "Fixing bracket capacity (≥ 1.5× design)",
            "Drainage detail (≥ 2% fall)",
        ],
        "coP_refs": ["Steel 2011", "Wind Effects 2019"],
        "appendix": "VII-§27",
    },
    "1.36": {
        "name": "Underground Drainage (Class I)",
        "class": "I",
        "typical_span": "N/A",
        "typical_load": "Soil + traffic",
        "key_checks": [
            "Pipe class per SDR rating",
            "Trench backfill compaction ≥ 95%",
            "Gradient ≥ 1:100 for DN100",
        ],
        "coP_refs": ["Drainage Manual"],
        "appendix": "VII-§36",
    },
    "1.50": {
        "name": "Supporting structures for AC unit on roof",
        "class": "I",
        "typical_span": "≤ 1.5m",
        "typical_load": "AC unit 80-200 kg + wind",
        "key_checks": [
            "Steel support frame per Steel 2011",
            "Anchor pull-out ≥ 1.5× design uplift",
            "Vibration isolation",
            "Wind load per Wind Effects 2019",
        ],
        "coP_refs": ["Steel 2011", "Wind Effects 2019"],
        "appendix": "VII-§50",
    },
}

CORE_ITEMS = ["1.6", "1.1", "1.5", "1.27"]


def load_mw01_path() -> Path:
    import json
    with open(CONFIG_PATH) as f:
        return Path(json.load(f)["bootcamps"]["mw01"]["path"])


def find_project_folder(mw_id: str, base: Path) -> Path | None:
    """Search projects/ for a folder matching the MW item id."""
    projects = base / "projects"
    if not projects.exists():
        return None
    # match patterns like "MW1.1_Internal_Staircase" or "1.1_..."
    for entry in projects.iterdir():
        if entry.is_dir() and (entry.name.startswith(f"MW{mw_id}_") or entry.name.startswith(f"{mw_id}_") or entry.name.startswith(f"MW{mw_id}.")):
            return entry
    return None


def fmt_item(mw_id: str, include_refs: bool = False, mw01_base: Path = None) -> str:
    info = KNOWN_ITEMS.get(mw_id)
    out = []
    out.append(f"## MW {mw_id}")
    if info:
        out.append(f"**Name:** {info['name']}")
        out.append(f"**Class:** {info['class']}")
        out.append(f"**Typical span:** {info['typical_span']}")
        out.append(f"**Typical load:** {info['typical_load']}")
        out.append(f"**MWTGe reference:** {info['appendix']}")
        out.append("")
        out.append("**Key checks:**")
        for chk in info["key_checks"]:
            out.append(f"- {chk}")
        if include_refs:
            out.append("")
            out.append("**Codes of Practice:**")
            for ref in info["coP_refs"]:
                out.append(f"- {ref}")
        # Check local project folder
        if mw01_base:
            proj = find_project_folder(mw_id, mw01_base)
            if proj:
                files = sorted(p.name for p in proj.iterdir() if p.is_file())
                out.append("")
                out.append(f"**Local project folder:** `{proj.relative_to(mw01_base)}/`")
                if files:
                    out.append("Files in folder:")
                    for f in files[:10]:
                        out.append(f"- {f}")
                    if len(files) > 10:
                        out.append(f"- … and {len(files) - 10} more")
            else:
                out.append("")
                out.append("**Local project folder:** _not found in projects/_")
    else:
        out.append(f"_No curated info for MW {mw_id}. Consult MWTGe.pdf and update KNOWN_ITEMS in this script._")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mw_id", nargs="?", help="MW item number, e.g. 1.1, 1.5")
    ap.add_argument("--references", action="store_true", help="Include CoP refs")
    ap.add_argument("--list", action="store_true", help="List all known MW items")
    ap.add_argument("--core", action="store_true", help="List the 4 core items")
    args = ap.parse_args()

    if args.list:
        print("Known MW items (curated subset):")
        for k, v in KNOWN_ITEMS.items():
            mark = " ⭐ CORE" if k in CORE_ITEMS else ""
            print(f"  {k}{mark}  {v['name']}")
        print()
        print(f"Total: {len(KNOWN_ITEMS)} items. Extend KNOWN_ITEMS dict in scripts/mw_lookup.py to add more.")
        return 0

    if args.core:
        for k in CORE_ITEMS:
            print(fmt_item(k))
            print()
        return 0

    if not args.mw_id:
        print("❌ MW item required. e.g. `mw_lookup.py 1.1`", file=sys.stderr)
        print("   Use --list or --core to browse.", file=sys.stderr)
        return 2

    base = load_mw01_path()
    print(fmt_item(args.mw_id, include_refs=args.references, mw01_base=base))
    return 0


if __name__ == "__main__":
    sys.exit(main())