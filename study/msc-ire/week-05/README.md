# Week 5 — 2026-07-11 (Saturday)

**Phase:** 1 — Foundations
**Focus courses:**
- **EEEN3030 Engineering Materials** (3 units, Major Required)
- **ELEG2202 Fundamentals of Electric Circuits** (3 units, Major Required)
**Simulator update:** Sensor modeling (per standing plan)

## Files

| File | Purpose |
|---|---|
| `EEEN3030-notes.md` | Synthesized theory + key topics + my-project hooks |
| `ELEG2202-notes.md` | Synthesized theory + key topics + my-project hooks |
| `practice.md` | Combined explain-as-teacher prompts for both courses (Saturday) |
| `../../skills/bootcamp-content-assistant/outputs/EEEN3030_practice.json` | raw JSON (gitignored, Saturday) |
| `../../skills/bootcamp-content-assistant/outputs/ELEG2202_practice.json` | raw JSON (gitignored, Saturday) |
| `../../skills/bootcamp-content-assistant/cards.tsv` | Anki-importable flashcards (gitignored, Saturday) |

## Auto-generated material

_(Sat 2026-07-11 cron will fire `flashcard_gen.py` + `practice_gen.py` for both courses.)_

Midweek prep committed 2026-07-08:
- Source content pulled
- Week index + notes skeletons written
- Pending: flashcards + practice JSON + final notes synthesis

## Source content overview (previewed 2026-07-08)

### EEEN3030 — Engineering Materials
- Atomic bonding; crystal structures & defects
- Mechanical properties; phase diagrams
- Metals, alloys, ceramics, polymers, semiconductors, composites
- Electrical / optical / magnetic / thermal properties
- Materials selection & design for engineering
- IRE relevance ⭐⭐⭐ (sensor materials, gripper pad selection, structural choices)

### ELEG2202 — Fundamentals of Electric Circuits
- Basic circuit laws & theorems (KVL, KCL, Thevenin/Norton)
- Circuit analysis methods (nodal, mesh)
- Op-amp circuits; linear feedback
- AC: impedance, phasors, sinusoids, frequency response
- Power: transient, 3-phase, inductors, transformers
- Mandatory lab modules
- IRE relevance ⭐⭐⭐ (sensor signal conditioning, motor drive circuits, PID electronics)

## How to use

1. Read `EEEN3030-notes.md` and `ELEG2202-notes.md` first.
2. After Saturday cron: import `cards.tsv` into Anki (one combined deck for both courses).
3. Work through `practice.md` — write answers before checking source `.md`.
4. Update simulator sensor-modeling module after both theories sink in.

## Status

- [x] Pull source content for both courses (Wed 2026-07-08)
- [x] Write week index + notes skeletons (Wed 2026-07-08)
- [ ] Generate flashcards (Saturday cron)
- [ ] Generate practice problems (Saturday cron)
- [ ] Finalize notes — synthesize after Anki/practice review
- [ ] Sensor-modeling sim update
- [ ] User reviews notes + runs through Anki deck
- [ ] User fills in practice.md answers
- [ ] Mark completion in `memory/polyu-ire.md` progress table
