#!/usr/bin/env python3
"""rse_draft.py — generate first-draft RSE Calculation Report for an MW item.

Usage:
  rse_draft.py <item-id>                          # generate blank template
  rse_draft.py <item-id> --params <json>          # fill template with given params
  rse_draft.py <item-id> --params <json> --write  # also write to projects/<id>/<id>_Report.md

The template follows the structure of the existing sample report:
  projects/MW1.6_Protective_Barrier/MW1.6_Report.md

Sections generated:
  1. Project Details (location, scope, item)
  2. Design Parameters (table)
  3. References (MWTGe, CoP)
  4. Structural Analysis (load, moment, shear, deflection)
  5. Material Specifications
  6. Conclusions / RSE sign-off
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

MWTGE_PATH = Path("/app/bootcamps/MW01-RSE-Bootcamp/MW01-Technical-Guidelines/MWTGe_English_text.txt")
SAMPLE_REPORT = Path("/app/bootcamps/MW01-RSE-Bootcamp/projects/MW1.6_Protective_Barrier/MW1.6_Report.md")
PROJECTS_DIR = Path("/app/bootcamps/MW01-RSE-Bootcamp/projects")

# Curated item metadata for the draft
ITEM_META = {
    "1.1": {
        "name": "Erection or Alteration of Internal Staircase",
        "mwtge_ref": "Part 3 - Class I Minor Works (Items 1.1 - 1.5)",
        "cop_refs": ["Code of Practice for Structural Use of Concrete 2013",
                     "Code of Practice for Structural Use of Steel 2011"],
        "default_params": {
            "span_mm": 4000, "width_mm": 1000, "rise_mm": 175, "going_mm": 250,
            "live_load_kPa": 1.5, "concrete_grade": "C30", "steel_grade": "HY250",
        },
    },
    "1.5": {
        "name": "Removal of Supporting Structure on Cantilevered Slab",
        "mwtge_ref": "Part 3 - Class I Minor Works (Items 1.1 - 1.5)",
        "cop_refs": ["Code of Practice for Structural Use of Concrete 2013"],
        "default_params": {
            "cantilever_mm": 1500, "slab_thk_mm": 175, "live_load_kPa": 3.0,
            "concrete_grade": "C30", "steel_grade": "HY250",
        },
    },
    "1.6": {
        "name": "Alteration or Removal of Protective Barrier",
        "mwtge_ref": "Part 3 - Class I Minor Works (Items 1.6 - 1.10)",
        "cop_refs": ["Code of Practice for Structural Use of Steel 2011",
                     "Code of Practice for Structural Use of Concrete 2013"],
        "default_params": {
            "height_m": 1.1, "post_spacing_m": 1.2, "live_load_kPa": 1.5,
            "horizontal_load_kN_m": 1.5, "steel_grade": "S275",
        },
    },
    "1.27": {
        "name": "Erection / Alteration / Removal of Canopy",
        "mwtge_ref": "Part 4 - Class I Minor Works (Items 1.11 - 1.30)",
        "cop_refs": ["Code of Practice for Structural Use of Steel 2011",
                     "Code of Practice on Wind Effects in Hong Kong 2019"],
        "default_params": {
            "projection_m": 3.5, "width_m": 6.0,
            "wind_pressure_kPa": 2.5, "steel_grade": "S275",
        },
    },
    "1.36": {
        "name": "Underground Drainage",
        "mwtge_ref": "Part 5 - Class I Minor Works (Items 1.31 - 1.40)",
        "cop_refs": ["Drainage Manual"],
        "default_params": {
            "pipe_dn_mm": 100, "depth_m": 1.2, "gradient_pct": 1.0,
        },
    },
    "1.50": {
        "name": "Supporting Structures for AC Unit on Roof",
        "mwtge_ref": "Part 6 - Class I Minor Works (Items 1.41 - 1.50)",
        "cop_refs": ["Code of Practice for Structural Use of Steel 2011",
                     "Code of Practice on Wind Effects in Hong Kong 2019"],
        "default_params": {
            "unit_weight_kg": 120, "frame_span_m": 1.4, "frame_height_m": 0.6,
            "wind_pressure_kPa": 2.5, "steel_grade": "S275",
        },
    },
}


def render_template(item_id: str, params: dict, project_no: str = "") -> str:
    meta = ITEM_META.get(item_id)
    if not meta:
        return f"❌ unknown item {item_id}. Supported: {', '.join(ITEM_META.keys())}"

    name = meta["name"]
    today = date.today().strftime("%Y-%m-%d")
    proj = project_no or f"PR-2026-MW{item_id.replace('.', '')}-001"

    # Render params table
    p_rows = []
    for k, v in params.items():
        # convert snake_case to Title Case
        label = k.replace("_", " ").title()
        p_rows.append(f"| {label} | {v} |")
    p_table = "\n".join(p_rows) if p_rows else "_(no parameters — fill manually)_"

    # Render CoP refs
    cop_lines = []
    for ref in meta["cop_refs"]:
        cop_lines.append(f"- {ref}")
    cop_md = "\n".join(cop_lines)

    # Render basic structural analysis placeholder
    analysis_md = render_analysis(item_id, params)

    md = f"""# MW {item_id} RSE Calculation Report
**{name}**
**Item No.:** MW {item_id}
**Project No.:** {proj}
**Date:** {today}

---

## 1. Project Details

**Item:** {name}
**Location:** <填寫地址>
**Scope:** <填寫工程範圍>

---

## 2. Design Parameters

| Parameter | Value |
|---|---|
{p_table}

---

## 3. References

**Primary:**
- Minor Works Technical Guidelines on Minor Works Control System (MWTGe), Buildings Department
- Item reference: {meta['mwtge_ref']}

**Codes of Practice:**
{cop_md}

---

## 4. Structural Analysis

{analysis_md}

---

## 5. Material Specifications

_(fill material grades, thicknesses, fixing details per CoP)_

---

## 6. Conclusions

_(summary of compliance + RSE sign-off block)_

---

## 7. RSE Signature

| | |
|---|---|
| RSE Name: | _________________ |
| HKIE Membership No.: | _________________ |
| Signature: | _________________ |
| Date: | _________________ |

---

*Generated by skills/bootcamp-content-assistant/scripts/rse_draft.py — review before signing.*
"""
    return md


def render_analysis(item_id: str, params: dict) -> str:
    """Item-specific first-draft calculations."""
    if item_id == "1.1":
        span = params.get("span_mm", 4000)
        rise = params.get("rise_mm", 175)
        going = params.get("going_mm", 250)
        return f"""### 4.1 Stair Geometry Check
$$2R + G = 2 \\times {rise} + {going} = {2*rise + going} \\geq 550 \\text{{ mm}} \\quad ✓$$

### 4.2 Deflection Check (Span = {span} mm)
$$δ_allow = L/360 = {span}/360 = {span/360:.1f} \\text{{ mm}}$$

_(run analysis to verify)_

### 4.3 Live Load
- LL = {params.get('live_load_kPa', 1.5)} kPa (per MWTGe Class I)
"""
    if item_id == "1.5":
        cl = params.get("cantilever_mm", 1500)
        sl = params.get("slab_thk_mm", 175)
        ll = params.get("live_load_kPa", 3.0)
        return f"""### 4.1 Cantilever Load
- Cantilever length L = {cl} mm
- Slab thickness = {sl} mm
- LL = {ll} kPa

### 4.2 Moment (per metre width)
$$M = \\frac{{w L^2}}{{2}} = \\frac{{{ll*1000} \\times {cl/1000}^2}}{{2}} = {ll*1000*(cl/1000)**2/2:.2f} \\text{{ kNm/m}}$$

### 4.3 Removal Sequence
1. Prop remaining structure before cutting
2. Cut in sequence from cantilever tip
3. Monitor deflection
"""
    if item_id == "1.6":
        h = params.get("height_m", 1.1)
        sp = params.get("post_spacing_m", 1.2)
        hl = params.get("horizontal_load_kN_m", 1.5)
        return f"""### 4.1 Handrail Load
- Horizontal load at handrail = {hl} kN/m (per MWTGe)
- Height of barrier H = {h} m

### 4.2 Moment on Post
$$M_{{post}} = \\frac{{q L^2}}{{8}} = \\frac{{{hl} \\times {sp}^2}}{{8}} = {hl*sp**2/8:.3f} \\text{{ kNm}}$$

### 4.3 Opening Check
- Opening ≤ 100 mm ✓ (per MWTGe §3.x)
- Handrail height ≥ 1100 mm ✓ ({h} m)
"""
    if item_id == "1.27":
        p = params.get("projection_m", 3.5)
        w = params.get("wind_pressure_kPa", 2.5)
        return f"""### 4.1 Wind Load
- Wind pressure q = {w} kPa (per Wind Effects 2019)

### 4.2 Cantilever Moment (per metre width)
$$M = \\frac{{q L^2}}{{2}} = \\frac{{{w} \\times {p}^2}}{{2}} = {w*p**2/2:.2f} \\text{{ kNm/m}}$$

### 4.3 Deflection Check
- δ_allow = L/180 = {p*1000/180:.1f} mm
"""
    if item_id == "1.36":
        return f"""### 4.1 Pipe Class
- DN = {params.get('pipe_dn_mm', 100)} mm
- Depth = {params.get('depth_m', 1.2)} m
- Gradient = {params.get('gradient_pct', 1.0)}% (≥ 1% for DN100 ✓)
"""
    if item_id == "1.50":
        m = params.get("unit_weight_kg", 120)
        s = params.get("frame_span_m", 1.4)
        w = params.get("wind_pressure_kPa", 2.5)
        return f"""### 4.1 Dead Load
- AC unit weight = {m} kg → W = {m*9.81/1000:.2f} kN

### 4.2 Wind Load
- Wind pressure q = {w} kPa
- Uplift check = {w} × area
"""
    return "_(no specific analysis template for this item — fill manually)_"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("item_id", help="MW item id (e.g. 1.6, 1.27)")
    ap.add_argument("--params", help="JSON file with parameters")
    ap.add_argument("--project-no", help="Project number (default auto)")
    ap.add_argument("--write", action="store_true",
                    help="Write to projects/<item>/MW<item>_Report.md")
    args = ap.parse_args()

    meta = ITEM_META.get(args.item_id)
    if not meta:
        print(f"❌ unknown item {args.item_id}. Supported: {', '.join(ITEM_META.keys())}", file=sys.stderr)
        return 2

    # Load params: file > defaults
    params = dict(meta["default_params"])
    if args.params:
        with open(args.params) as f:
            user_params = json.load(f)
        params.update(user_params)

    md = render_template(args.item_id, params, args.project_no)

    if args.write:
        # Find or create the project folder
        existing = None
        for entry in PROJECTS_DIR.iterdir():
            if entry.is_dir() and entry.name.startswith(f"MW{args.item_id}"):
                existing = entry
                break
        if existing:
            target = existing / f"MW{args.item_id}_Report.md"
            target.write_text(md)
            print(f"✓ Written to {target}")
        else:
            print(f"⚠️ No project folder found for MW {args.item_id}.")
            print(f"  Create one first: mkdir -p projects/MW{args.item_id}_<name>")
            print(f"  Then re-run with --write, or pipe output to file manually.")
            print()
            print(md)
            return 1
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())