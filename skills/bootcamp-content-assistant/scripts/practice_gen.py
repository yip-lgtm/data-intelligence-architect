#!/usr/bin/env python3
"""practice_gen.py — generate practice problems from a course .md.

Heuristic generator:
- Pulls "Topics" / bullets → "explain X in your own words" prompts
- Pulls formulas → "derive / apply" prompts
- Pulls code blocks → "implement / debug / modify" prompts
- Pulls explicit "Practice & Exercises" sections if present

Usage:
  practice_gen.py <course-code>
  practice_gen.py <course-code> --count 5
  practice_gen.py <course-code> --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path

MAE_CUHK = Path("/app/bootcamps/msc-ire/mae-cuhk/courses")


def find_course(code: str) -> Path | None:
    code_upper = code.upper().strip()
    for sub in MAE_CUHK.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if f.suffix == ".md" and f.stem.upper() == code_upper:
                return f
    return None


def generate_problems(text: str) -> list[dict]:
    problems = []
    lines = text.splitlines()

    # 1. Topics → "Explain X"
    topic_pat = re.compile(r"^[-*]\s+(.+)")
    meta_pat = re.compile(r"\*\*[^*]+:\*\*")
    for line in lines:
        m = topic_pat.match(line)
        if m:
            topic = m.group(1).strip()
            # Skip metadata bullets (e.g. **Code:** MAEG1020)
            if meta_pat.match(topic):
                continue
            # Skip meta topics
            if topic.lower().startswith(("status", "last updated", "category")):
                continue
            # Skip short fragments
            if len(topic) < 12:
                continue
            problems.append({
                "type": "explain",
                "difficulty": "medium",
                "prompt": f"Explain **{topic}** in 2-3 paragraphs as if teaching a peer. Include a real-world example.",
            })

    # 2. Formulas → apply
    formula_pat = re.compile(r"(\w+)\s*=\s*([^=]+)")
    formulas_seen = set()
    for line in lines:
        if "$$" in line or "==" in line:
            continue
        m = formula_pat.search(line)
        if m and m.group(1).isalpha() and len(m.group(2)) < 50:
            var = m.group(1)
            if var in formulas_seen:
                continue
            formulas_seen.add(var)
            problems.append({
                "type": "apply",
                "difficulty": "medium",
                "prompt": f"Define `{var}` and explain when you would use it in practice. Show a worked example with numbers.",
            })

    # 3. Code blocks → modify
    in_code = False
    code_buf = []
    code_lang = ""
    code_idx = 0
    for line in lines:
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            if in_code:
                if code_buf and len(code_buf) > 3:
                    problems.append({
                        "type": "code",
                        "difficulty": "hard",
                        "prompt": f"This {code_lang or 'code'} snippet:\n\n```{code_lang}\n" + "\n".join(code_buf)[:300] + "\n```\n\nModify it to handle an edge case, then explain your changes.",
                    })
                    code_idx += 1
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                in_code = True
                code_lang = m.group(1)

    # 4. Practice & Exercises section
    in_practice = False
    for line in lines:
        if "Practice & Exercises" in line or "Practice and Exercises" in line:
            in_practice = True
            continue
        if in_practice:
            if line.startswith("#"):
                in_practice = False
                continue
            stripped = line.strip()
            if stripped.startswith("-"):
                problems.append({
                    "type": "author-defined",
                    "difficulty": "varies",
                    "prompt": stripped.lstrip("- ").strip(),
                })

    # 5. Universal starter problems
    problems.append({
        "type": "synthesis",
        "difficulty": "hard",
        "prompt": "Write a 5-minute teaching outline covering the entire course, with one concrete example per major section.",
    })
    problems.append({
        "type": "application",
        "difficulty": "medium",
        "prompt": "Identify the 3 most important concepts from this course that you've already applied (or could apply) in your 3R arm / warehouse robot simulator. Be specific.",
    })

    return problems


def render_markdown(problems: list[dict], code: str) -> str:
    out = [f"# Practice Problems — {code}\n"]
    by_type = {}
    for p in problems:
        by_type.setdefault(p["type"], []).append(p)
    for ptype, items in by_type.items():
        out.append(f"## {ptype.title()} ({len(items)})\n")
        for i, p in enumerate(items, 1):
            out.append(f"**{i}.** {p['prompt']}  *(difficulty: {p['difficulty']})*\n")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("code")
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args()

    path = find_course(args.code)
    if not path:
        print(f"❌ course {args.code} not found", file=sys.stderr)
        return 2

    text = path.read_text()
    problems = generate_problems(text)[:args.count]

    if args.format == "json":
        print(json.dumps(problems, indent=2))
    else:
        print(render_markdown(problems, args.code))

    print(f"\n— {len(problems)} problems from {path.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())