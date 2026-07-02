# Bootcamp Orchestrator — Architecture

## What this skill solves

You have **two self-study bootcamps** running in parallel:

| Bootcamp | Cadence | Tracker file |
|---|---|---|
| MW01 RSE Bootcamp | Project-based (each report ~ 1–2 weeks) | `progress/Bootcamp_Progress.md` |
| 24-Week PolyU MSc IRE | Weekend-paced (Sat AM theory, Sat PM practice) | `progress.md` (24-row weekly table) |

Both are personal, owned by you, mirrored to `/app/bootcamps/` so this
agent can read them. Without automation, tracking both means opening
two repos, parsing markdown by hand, and figuring out what's due.

This skill does:

1. **Parse** both progress files into structured data.
2. **Compute** current focus (today's MW item, this week's MSC focus).
3. **Render** a digest: long form (memory log) or short form (Telegram).
4. **Look up** MW item requirements (MWTGe refs, key checks, local
   project folder).

---

## Components

```
            ┌──────────────────────────────────────────────────────────┐
            │                                                          │
            │   agent (chat)                                           │
            │     ├─ "bootcamp status"          → status.py            │
            │     ├─ "MW 1.1 要求"            → mw_lookup.py 1.1      │
            │     └─ "weekly digest"           → weekly.sh             │
            │                                                          │
            │   weekly.sh                                              │
            │     ├─ status.py (parse + render)                        │
            │     ├─ → memory/YYYY-MM-DD.md   (--memory)               │
            │     └─ → notify.sh              (--send via Telegram)    │
            │                                                          │
            │   cron (recommended)                                     │
            │     └─ Sat 09:00 HKT: weekly.sh --memory --send          │
            │                                                          │
            └──────────────────────────────────────────────────────────┘
                                       │
                                       ▼
              ┌──────────────────────────────────────────────────┐
              │  /app/bootcamps/MW01-RSE-Bootcamp/         (read) │
              │  /app/bootcamps/msc-ire/                   (read) │
              └──────────────────────────────────────────────────┘
```

## Configurable

`config/bootcamps.json` is the single source of truth for paths,
start dates, core items, status emojis. Edit it to add a third
bootcamp without touching the scripts.

## Two distinct cadences

| | MW01 | MSC-IRE |
|---|---|---|
| Cadence | Project-based | 24 fixed weeks |
| Trigger | "next report" | "this week's focus" |
| Done when | 4 core + Class I | all 24 weeks |
| Primary signal | markdown table count | date arithmetic from `startDate` |
| Secondary | per-item completion status emoji | per-week status emoji |

`status.py` keeps the two parsing paths separate (`parse_mw01_progress`
vs `parse_msc_ire_progress`) but renders them with a common shape.

---

## Why two Telegram modes?

- `--short` (one line per bootcamp) — header for a daily / weekly message.
- Full form — for memory log + weekly review.

The user can `grep` the short form into any digest and dive into the
full form when needed.

---

## How it differs from `bootcamp_weekly.py` (in the upstream MSC repo)

The upstream MSC repo already ships a per-week generator under
`24_Week_Weekend_Bootcamp/skill/bootcamp_weekly.py`. This skill:

- **Does not replace** the upstream scripts — they remain authoritative
  for MSC weekly messages.
- **Adds** the unified MW01 + MSC view.
- **Adds** the MW item lookup (which the upstream repo doesn't have).
- **Adds** cross-bootcamp memory logging into one place.

If both fire on Saturday, you'd get two Telegram messages. To avoid
that, either disable the upstream MSC cron, or wrap the upstream
`bootcamp_weekly.py` to suppress when our `weekly.sh` already fired.
(Simple `touch` flag in `logs/last-digest.txt` is enough.)

---

## Extending

| Want to… | How |
|---|---|
| Add a 3rd bootcamp | New entry in `config/bootcamps.json` + new `parse_<name>_progress()` in `status.py` |
| Auto-pull upstream repos before digest | Add `git -C <repo> pull --ff-only` line in `weekly.sh` (only if network OK) |
| Per-bootcamp Telegram channel | Change `notify.sh` target via `TELEGRAM_CHAT_ID_<NAME>` env |
| Push digest to GitHub gist | Append `gh gist create` line to `weekly.sh` |