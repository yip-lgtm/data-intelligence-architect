# PolyU MSc IRE — Context + Automation Preferences

## What is IRE?

- **Program:** PolyU MSc — **Intelligent Robotics Engineering** (24-week weekend-paced self-study bootcamp)
- **Source repo (read-only mirror):** `/app/bootcamps/msc-ire/24_Week_Weekend_Bootcamp/` + `/app/bootcamps/msc-ire/mae-cuhk/`
- **Start date:** 2026-06-13
- **Today anchor (2026-07-05):** Week 4/24, Phase 1 Foundations
- **Studying to:** BEng MAE + Portfolio (per `bootcamps.json`)
- **Off-limits when working on IRE** (do NOT cross-pollinate):
  - Minor Works (MW) items
  - RSE inspection reports
  - Class I Minor Works (CI Minor Works)
  - Anything from `skills/bootcamp-orchestrator/` for `mw01` bootcamp

## User's IRE focus

- **Current week:** 4 → MAEG3010 Mechanics of Materials
- **Simulator project (in `builds/soft_gripper/`):** soft gripper build, progressing through phases
- **Earlier weeks still marked ⬜ in upstream `progress.md`** — user hasn't been logging study completions; weekly session log here is our local canonical tracker.

## 🤖 Automation preferences (declared 2026-07-05)

> **Pick first option by default** — when given choices, do NOT ping back asking which; just execute option #1.
> **Auto-run weekend bootcamp** — every weekend session, generate study material, write notes, commit, push.
> **`git push` at the end of every session** — if push fails, surface to user, don't silently drop.

## 🧭 Auto-study workflow (weekend session)

```
1. status.py msc-ire                                → confirm current week + course
2. week_content.py <N> --json                       → structured week spec
3. course_read.py <CODE>                            → source content
4. flashcard_gen.py <CODE> --format anki            → .tsv (gitignored)
5. practice_gen.py <CODE> --count 6 --format json   → .json (gitignored)
6. Write: study/msc-ire/week-NN/<CODE>-notes.md     → COMMITTED
7. Write: study/msc-ire/week-NN/practice.md         → COMMITTED
8. Update: memory/<today>.md                        → COMMITTED
9. Update: this file                                → COMMITTED
10. git add -A && git commit -m "..." && git push
```

## Files

- Source markdown: `/app/bootcamps/msc-ire/mae-cuhk/courses/<category>/<CODE>.md` (read-only)
- Generated study outputs: `skills/bootcamp-content-assistant/outputs/` (gitignored)
- Committed study notes: `study/msc-ire/week-NN/`
- Weekly session log: `memory/YYYY-MM-DD.md`
- Persistent prefs: this file

## Notes

### Progress tracker

| Week | Status | Notes |
|---|---|---|
| 1–3 | ⬜ upstream not marked | Not yet summarized locally |
| 4 / 2026-07-04–05 | ✅ | MAEG3010 Mechanics of Materials — committed Sun 2026-07-05 |
| 5 / 2026-07-11–12 | 🟡 prepped | EEEN3030 Materials + ELEG2202 Circuits — midweek scaffolds Wed 2026-07-08; Saturday cron will generate flashcards + practice |

### Week 5 IRE relevance hooks (planned for sensor modeling sim)
- Materials: sensor housing, gripper pad selection, motor material limits
- Circuits: sensor signal conditioning (op-amp), motor driver H-bridge + PWM, PID electronics, RC anti-aliasing


