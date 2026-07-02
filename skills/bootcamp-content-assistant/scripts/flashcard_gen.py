#!/usr/bin/env python3
"""flashcard_gen.py — generate Q&A flashcards from a course .md.

Heuristic extractor:
- Course description paragraphs → Q&A
- Topic bullets → cloze deletions
- "Key concepts" / "Formulas" sections → term definitions
- Code blocks → "what does this do?" prompts

Usage:
  flashcard_gen.py <course-code>                 # generate cards, print markdown
  flashcard_gen.py <course-code> --format anki   # Anki-compatible TSV (front\tback)
  flashcard_gen.py <course-code> --format gpt    # JSON for LLM use
  flashcard_gen.py <course-code> --limit 10      # cap output
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


def extract_flashcards(text: str) -> list[dict]:
    """Return list of {front, back, type} cards."""
    cards = []
    lines = text.splitlines()

    # 1. Course description → "What is <code> about?"
    desc_lines = []
    in_desc = False
    for i, line in enumerate(lines):
        if "Course Description" in line or "course description" in line.lower():
            in_desc = True
            continue
        if in_desc:
            if line.startswith("#") or (line.strip() == "" and i > 5):
                in_desc = False
                continue
            if line.strip():
                desc_lines.append(line.strip())
    if desc_lines:
        first = desc_lines[0]
        cards.append({
            "type": "definition",
            "front": "What is this course about?",
            "back": " ".join(desc_lines)[:500],
        })

    # 2. Topics bullets → "Name a key topic"
    topics = []
    meta_pat = re.compile(r"\*\*[^*]+:\*\*\s+\S")
    for line in lines:
        m = re.match(r"^[-*]\s+(.+)", line)
        if m:
            text = m.group(1).strip()
            # Skip metadata-style bullets (e.g. **Code:** xxx)
            if meta_pat.match(text):
                continue
            # Skip very short
            if len(text) < 8:
                continue
            topics.append(text)
    if topics:
        cards.append({
            "type": "enumeration",
            "front": f"List 3-5 key topics covered (any order).",
            "back": "\n".join(f"- {t}" for t in topics[:7]),
        })

    # 3. Formulas (lines with $$ or = or math symbols)
    formula_lines = []
    for line in lines:
        if "$$" in line or re.search(r"\b\w+\s*=\s*[^=]+", line):
            if len(line) < 200:
                formula_lines.append(line.strip())
    for f in formula_lines[:3]:
        cards.append({
            "type": "formula",
            "front": f"State and explain: `{f[:80]}`",
            "back": f,
        })

    # 4. Code blocks → "What does this code do?"
    in_code = False
    code_buf = []
    code_lang = ""
    for line in lines:
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            if in_code:
                if code_buf and len(code_buf) > 3:
                    cards.append({
                        "type": "code",
                        "front": f"What does this {code_lang or 'code'} snippet do?",
                        "back": "\n".join(code_buf)[:500],
                    })
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                in_code = True
                code_lang = m.group(1)
        elif in_code:
            code_buf.append(line)

    # 5. Section headers → "What does section X cover?"
    sections = []
    for line in lines:
        m = re.match(r"^##\s+(.+)", line)
        if m:
            sections.append(m.group(1).strip())
    if len(sections) >= 2:
        cards.append({
            "type": "outline",
            "front": "Outline the main sections of this course.",
            "back": "\n".join(f"- {s}" for s in sections),
        })

    # 6. Prerequisites → "What should you know before taking this course?"
    prereqs = []
    in_prereq = False
    for line in lines:
        if "Prerequisites" in line or "prerequisites" in line.lower():
            in_prereq = True
            continue
        if in_prereq:
            if line.startswith("#"):
                in_prereq = False
                continue
            if line.strip():
                prereqs.append(line.strip())
    if prereqs:
        cards.append({
            "type": "prereq",
            "front": "What are the prerequisites for this course?",
            "back": "\n".join(f"- {p}" for p in prereqs[:5]),
        })

    return cards


def render_markdown(cards: list[dict], code: str) -> str:
    out = [f"# Flashcards — {code}\n"]
    for i, c in enumerate(cards, 1):
        out.append(f"## Card {i} ({c['type']})")
        out.append(f"**Q:** {c['front']}")
        out.append(f"\n**A:** {c['back']}\n")
    return "\n".join(out)


def render_anki_tsv(cards: list[dict]) -> str:
    out = []
    for c in cards:
        # TSV: front\tback — strip newlines from front/back
        front = c["front"].replace("\t", " ").replace("\n", " ")
        back = c["back"].replace("\t", " ").replace("\n", "<br>")
        out.append(f"{front}\t{back}")
    return "\n".join(out)


def render_json(cards: list[dict]) -> str:
    return json.dumps(cards, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", help="course code")
    ap.add_argument("--format", choices=["markdown", "anki", "json", "gpt"],
                    default="markdown")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    path = find_course(args.code)
    if not path:
        print(f"❌ course {args.code} not found", file=sys.stderr)
        return 2

    text = path.read_text()
    cards = extract_flashcards(text)[:args.limit]

    if args.format == "markdown":
        print(render_markdown(cards, args.code))
    elif args.format == "anki":
        print(render_anki_tsv(cards))
    elif args.format in ("json", "gpt"):
        print(render_json(cards))

    print(f"\n— {len(cards)} cards from {path.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())