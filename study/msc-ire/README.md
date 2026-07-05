# MSC-IRE Study Notes — Index

Self-paced study notes for **PolyU MSc Intelligent Robotics Engineering** weekend bootcamp.
Source content lives in the read-only bootcamp mirror at `/app/bootcamps/msc-ire/mae-cuhk/`.

⚠️ **Boundary:** This folder is for **IRE** study only. Do NOT bring in MW01 / RSE / Minor Works content.

## Structure

```
study/msc-ire/
├── README.md                    ← this file (week index)
└── week-NN/                     ← one folder per weekend session
    ├── <COURSE>-notes.md       ← synthesized notes per course
    └── practice.md              ← prompts from practice_gen + my answers
```

## Week Index

| Week | Date       | Phase | Focus | Folder |
|------|------------|-------|-------|--------|
| 1    | 2026-06-13 | 1 Foundations | ENGG1110/1120/1130 | `week-01/` |
| 2    | 2026-06-20 | 1 Foundations | MATH1510 + PHYS1110 + MAEG1020 | `week-02/` |
| 3    | 2026-06-27 | 1 Foundations | MAEG2020 Engineering Mechanics | `week-03/` |
| **4**| **2026-07-04** | **1 Foundations** | **MAEG3010 Mechanics of Materials** | **`week-04/` ← current** |
| 5    | 2026-07-11 | 1 Foundations | EEEN3030 Materials + ELEG2202 Circuits | `week-05/` |

## How the auto-study session works

When triggered (weekly cron OR user prompt "bootcamp status" / "week N content"):

1. Run `skills/bootcamp-content-assistant/scripts/week_content.py N` to get the week's course(s).
2. Run `course_read.py <CODE>` + `flashcard_gen.py <CODE>` + `practice_gen.py <CODE>`.
3. Save flashcards (.tsv) + practice prompts (.json) under `skills/bootcamp-content-assistant/outputs/` (gitignored).
4. Synthesize concise notes under `study/msc-ire/week-NN/<CODE>-notes.md` (committed).
5. Log session to `memory/YYYY-MM-DD.md` and update `memory/polyu-ire.md`.

The original bootcamp repo (`/app/bootcamps/msc-ire/`) is **read-only** — we never modify upstream.
