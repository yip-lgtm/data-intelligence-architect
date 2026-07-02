# Bootcamp Content Assistant — Architecture

Generates study material from cloned bootcamp repos. Read-only by
default — only writes when `--write` is passed.

## Two content domains

### MW01 (RSE Bootcamp)

Source content:
- `MWTGe_English_text.txt` — official MWTGe text, 16,553 lines, 104 items indexed
- `projects/MW*/MW*_Report.md` — sample completed reports (used as templates)
- `REFERENCES/*.pdf` — real RSE reports (CS-222, CS-223, W21027, etc.)

Scripts:
- `mwtge_lookup.py` — full-text search across MWTGe
- `rse_draft.py` — generate report first draft with item-specific calculations

### MSC-IRE (24-Week Bootcamp)

Source content:
- `mae-cuhk/courses/**/*.md` — 75+ course .md files
- `mae-cuhk/COURSE_TEMPLATE.md` — template structure
- `mae-cuhk/COURSE_LISTS.md` — course catalog
- `24_Week_Weekend_Bootcamp/progress.md` — week-by-week table
- `demos/` — simulator code (Python, HTML)

Scripts:
- `course_read.py` — read & pretty-print a course
- `course_search.py` — keyword search across courses
- `flashcard_gen.py` — extract Q&A cards from a course
- `practice_gen.py` — generate practice problems
- `week_content.py` — full week content pack

## Components

```
            ┌──────────────────────────────────────────────────────────┐
            │                                                          │
            │   agent (chat)                                           │
            │     ├─ "MW 1.6 requirements"  → mwtge_lookup.py 1.6      │
            │     ├─ "draft RSE 1.6"        → rse_draft.py 1.6 --write │
            │     ├─ "MAEG2020 flashcards"  → flashcard_gen.py MAEG2020│
            │     ├─ "courses on kinematics"→ course_search.py        │
            │     └─ "week 5 content"       → week_content.py 5       │
            │                                                          │
            │   (read-only by default; --write to projects/)           │
            │                                                          │
            └──────────────────────────────────────────────────────────┘
                                       │
                                       ▼
              ┌──────────────────────────────────────────────────┐
              │  /app/bootcamps/MW01-RSE-Bootcamp/         (read) │
              │   ├── MWTGe_English_text.txt                      │
              │   └── projects/MW*/MW*_Report.md                  │
              │  /app/bootcamps/msc-ire/                   (read) │
              │   ├── mae-cuhk/courses/**/*.md                   │
              │   └── 24_Week_Weekend_Bootcamp/progress.md        │
              └──────────────────────────────────────────────────┘
```

## Two stages of generation

For MW01 reports:

1. **mwtge_lookup.py** — what does MWTGe say about item X?
2. **rse_draft.py** — generate the first draft using that context
3. **YOU review, edit, sign** — agent never replaces human judgment

For MSC courses:

1. **course_search.py** — find courses on topic T
2. **course_read.py --summary** — get a quick overview
3. **flashcard_gen.py / practice_gen.py** — generate study material
4. **YOU study, code, integrate into simulator**

The agent's job is to *seed* the workflow. The human's job is to
*review, decide, and ship*.

## Why heuristic extractors instead of LLM?

- **Fast** — runs in <1 second per call
- **Offline** — no API needed
- **Reproducible** — same input → same output
- **Inspectable** — you can read the regex and see what was extracted
- **Tunable** — extend heuristics without prompt-engineering

The heuristics won't replace an LLM for nuanced Q&A, but they
produce a solid 80% solution that's always available.

For higher-quality output, pipe the heuristic output through an LLM:
```
./scripts/flashcard_gen.py MAEG2020 --format json | \
  openclaw chat --prompt "Refine these flashcards into study-quality Q&A"
```

## Adding a new MW item

Add an entry to `ITEM_META` in `rse_draft.py`:

```python
"1.X": {
    "name": "...",
    "mwtge_ref": "Part X - ...",
    "cop_refs": ["..."],
    "default_params": {...},
},
```

Plus a `render_analysis()` branch if you want item-specific
calculations (otherwise generic placeholder is used).

## Adding a new course heuristic

The flashcards and practice scripts are modular — each "card type"
or "problem type" is a self-contained block. To add a new type:

1. Add a new extractor in `extract_flashcards()` / `generate_problems()`
2. Add a corresponding render case (or rely on the generic render)

The heuristics are intentionally simple (regex + line matching) so
they're easy to extend without breaking existing behavior.