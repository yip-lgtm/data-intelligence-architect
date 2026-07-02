---
name: bootcamp-content-assistant
description: Generate study material from upstream bootcamp content — search MWTGe for MW clauses, draft RSE reports, read CUHK course .md files, generate flashcards + practice problems, build week content packs. Triggers on "MW 1.1 requirements", "MAEG1020 flashcards", "week 5 practice", "draft RSE report for MW 1.27", etc.
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "requires":
          {
            "bins": ["python3"],
            "env": [],
            "optionalEnv": []
          },
        "configPaths":
          ["/app/bootcamps/MW01-RSE-Bootcamp",
           "/app/bootcamps/msc-ire"]
      }
  }
---

# Bootcamp Content Assistant 📚

Generates **study material** from the cloned bootcamp repos. Reads source
content (MWTGe text, course .md files, project folders), extracts
structure, and produces flashcards / practice problems / report drafts.

**This skill COMPLEMENTS `bootcamp-orchestrator`** — that one tracks
status, this one generates content.

---

## ⚡ Quick start

```bash
cd /app/data-intelligence-architect/skills/bootcamp-content-assistant
```

### MW01 (RSE) scripts

```bash
# Search MWTGe text for an MW item
./scripts/mwtge_lookup.py 1.6
./scripts/mwtge_lookup.py --item-list          # 104 items found
./scripts/mwtge_lookup.py "protective barrier" --context 3

# Generate RSE report first draft
./scripts/rse_draft.py 1.1                     # default params, print to stdout
./scripts/rse_draft.py 1.6 --params my.json   # custom params from JSON
./scripts/rse_draft.py 1.6 --write             # save to projects/MW1.6_*/MW1.6_Report.md
```

### MSC-IRE scripts

```bash
# Read a course .md
./scripts/course_read.py MAEG2020 --summary    # just header + topics
./scripts/course_read.py MAEG2020 --topic "PID"

# Find courses by keyword
./scripts/course_search.py "robotics"
./scripts/course_search.py "kinematics" --category major-required

# Generate flashcards from a course
./scripts/flashcard_gen.py MAEG2020
./scripts/flashcard_gen.py MAEG2020 --format anki > cards.tsv
./scripts/flashcard_gen.py MAEG2020 --format json

# Generate practice problems
./scripts/practice_gen.py MAEG2020 --count 8
./scripts/practice_gen.py MAEG2020 --format json

# Full week content pack
./scripts/week_content.py 5                    # Week 5
./scripts/week_content.py --current            # auto-detect from today
./scripts/week_content.py --current --json
```

---

## 🧠 Trigger phrases for the agent

| User says                                              | Action                                       |
| ------------------------------------------------------ | -------------------------------------------- |
| "MW 1.6 要求 / MWTGe 點講 1.6"                       | `mwtge_lookup.py 1.6`                        |
| "search MWTGe 'cantilever'"                           | `mwtge_lookup.py 'cantilever'`               |
| "draft RSE report for MW 1.27"                        | `rse_draft.py 1.27`                          |
| "generate RSE report 1.6 寫去 projects"               | `rse_draft.py 1.6 --write`                   |
| "MAEG2020 summary"                                    | `course_read.py MAEG2020 --summary`          |
| "搵 courses about PID control"                       | `course_search.py "PID"`                     |
| "MAEG2020 flashcards"                                 | `flashcard_gen.py MAEG2020`                  |
| "MAEG2020 practice problems"                          | `practice_gen.py MAEG2020`                   |
| "Week 5 做咩 / Week 5 content pack"                  | `week_content.py 5`                         |
| "今個禮拜 bootcamp focus"                           | `week_content.py --current`                  |
| "flashcard Anki format for MAEG2020"                  | `flashcard_gen.py MAEG2020 --format anki`    |

---

## 🗂️ Files this skill owns

```
bootcamp-content-assistant/
├── SKILL.md
├── README.md
├── scripts/
│   ├── mwtge_lookup.py        ← search MWTGe text (104 items indexed)
│   ├── rse_draft.py            ← generate RSE report first draft (6 items)
│   ├── course_read.py         ← pretty-print course .md
│   ├── course_search.py       ← keyword search across all courses
│   ├── flashcard_gen.py       ← extract Q&A from course .md
│   ├── practice_gen.py        ← generate practice problems
│   └── week_content.py        ← full week-N content pack
└── outputs/                    ← generated drafts land here (when --write used)
```

---

## 📋 What each MW01 script produces

### `mwtge_lookup.py 1.6`

- Searches pre-extracted MWTGe text (16,553 lines, 104 MW items indexed).
- Returns the structured blocks mentioning item 1.6 (15 blocks for 1.6).
- Includes context lines for each match.

### `rse_draft.py 1.6 --write`

Generates a complete Markdown RSE report with:

1. Cover (item, name, project no, date)
2. Project Details (placeholders for location / scope)
3. Design Parameters (table, with default values from `ITEM_META`)
4. References (MWTGe + CoP list)
5. Structural Analysis (item-specific: load, moment, deflection formulas)
6. Material Specifications (placeholder)
7. Conclusions (placeholder)
8. RSE Signature block

Supports `--params <file.json>` to override defaults. The agent
should always review the draft before submitting — it's a starting
point, not a finished report.

---

## 📋 What each MSC-IRE script produces

### `course_read.py <code>`

Returns the full course .md (or summary). Also `--topic` mode greps
for a keyword inside the course.

### `course_search.py "keyword"`

Ranks courses by keyword frequency. Useful for "what courses cover X?"
questions. Searches across 75+ course .md files in `mae-cuhk/courses/`.

### `flashcard_gen.py <code>`

Extracts flashcards via 6 heuristics:
1. Course description → "What is this course about?"
2. Topics bullets → "List 3-5 key topics"
3. Formulas → "State and explain"
4. Code blocks → "What does this code do?"
5. Section headers → "Outline the sections"
6. Prerequisites → "What are the prerequisites?"

Three output formats:
- **markdown** — pretty-printed, human-readable
- **anki** — TSV (front\tback), paste into Anki
- **json** — for LLM use or further processing

### `practice_gen.py <code>`

Generates problems via 5 patterns:
1. Explain each topic
2. Apply formulas
3. Modify code snippets
4. Author-defined "Practice & Exercises" section (if present)
5. Synthesis + application questions

Heuristics skip metadata bullets (`**Code:** ...`) to focus on actual
content.

### `week_content.py <week>`

Pulls together for a given week:
- Date + Phase from progress.md
- Focus + simulator update
- List of courses referenced (auto-extracted from focus text)
- Suggested Sat/Sun schedule

`--current` auto-detects the current week from today's date.

---

## 🔁 How it differs from `bootcamp-orchestrator`

| | orchestrator | content-assistant |
|---|---|---|
| Purpose | Track status | Generate material |
| Reads | progress files | course .md, MWTGe text |
| Writes | nothing (read-only) | `--write` to projects/ |
| Cadence | weekly digest | on-demand |
| Scripts | status, weekly digest | lookup, draft, generate |

Together they cover the "what to do" (orchestrator) and "how to do
it" (content-assistant) halves of the bootcamp workflow.

---

## 🛠️ Extending

| Want to… | Edit… |
|---|---|
| Add an MW item to draft | `ITEM_META` dict in `rse_draft.py` |
| Add a new card heuristic | Add new extractor block in `flashcard_gen.py` |
| Improve flashcard quality | Tune the metadata filter / minimum-length checks |
| Support a 3rd bootcamp | Add a new script mirroring `course_read.py` / `mwtge_lookup.py` patterns |
| Cache generated content | Write to `outputs/` and reuse across sessions |