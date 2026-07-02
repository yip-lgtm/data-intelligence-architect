---
name: bootcamp-orchestrator
description: Unified status / digest / lookup for the user's self-study bootcamps (MW01 RSE reports + 24-Week PolyU MSc IRE). Triggers on "bootcamp status", "MW 1.1 requirements", "week 3 focus", "bootcamp digest", or weekly cron reminders.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎓",
        "requires":
          {
            "bins": ["python3", "bash"],
            "env": [],
            "optionalEnv":
              ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
          },
        "configPaths":
          ["/app/data-intelligence-architect/skills/bootcamp-orchestrator/config/bootcamps.json"]
      }
  }
---

# Bootcamp Orchestrator 🎓

Unified automation for the user's **two self-study bootcamps**:

| Bootcamp | Domain | Source repo | Status |
|---|---|---|---|
| **MW01 RSE** 🏗️ | Hong Kong Minor Works Class I — RSE Calculation Reports | `github.com/yip-lgtm/MW01-RSE-Bootcamp` | 4/6 core items done |
| **MSC-IRE** 🤖 | PolyU MSc Intelligent Robotics Engineering — 24-week weekend pace | `github.com/yip-lgtm/Master-of-Science-in-Intelligent-Robotics-Engineering/tree/main/24_Week_Weekend_Bootcamp` | Week 3/24 in progress |

This skill parses each bootcamp's progress file, computes current
focus / next targets, and emits a Telegram-ready digest + memory log
on demand or via cron.

---

## ⚡ Quick start

The skill is preconfigured against the cloned repos at
`/app/bootcamps/MW01-RSE-Bootcamp/` and `/app/bootcamps/msc-ire/`.

```bash
# Unified status for both bootcamps
{baseDir}/scripts/status.py

# One bootcamp only
{baseDir}/scripts/status.py mw01
{baseDir}/scripts/status.py msc-ire

# Short form (one line per bootcamp — for Telegram headers)
{baseDir}/scripts/status.py --all --short

# MW item requirements lookup
{baseDir}/scripts/mw_lookup.py 1.1             # core item, MWTGe reference + key checks
{baseDir}/scripts/mw_lookup.py 1.1 --references # + CoP refs
{baseDir}/scripts/mw_lookup.py --core           # all 4 core items
{baseDir}/scripts/mw_lookup.py --list           # all known items

# Weekly digest + log to memory + send Telegram
{baseDir}/scripts/weekly.sh --memory --send
```

---

## 🧠 Trigger phrases for the agent

| User says (Cantonese / English examples)                | Action                                       |
| ------------------------------------------------------- | -------------------------------------------- |
| "bootcamp status" / "兩個 bootcamp 點？"              | `status.py`                                  |
| "MW01 進度" / "RSE 報告 status"                       | `status.py mw01`                             |
| "Week 3 focus" / "今個禮拜 bootcamp 做咩"            | `status.py msc-ire`                          |
| "MW 1.1 要求" / "MW 1.5 點做"                       | `mw_lookup.py <id>`                          |
| "bootcamp digest" / "weekly digest"                   | `weekly.sh --memory --send`                  |
| "bootcamp digest send" / "send digest 過嚟"           | `weekly.sh --send`                           |
| "log bootcamp progress"                                | `weekly.sh --memory`                         |

The agent should NEVER touch the original bootcamp repos
(`/app/bootcamps/MW01-RSE-Bootcamp`, `/app/bootcamps/msc-ire`) — they
are read-only mirrors. All edits should go to the user's local
`projects/` folders (separate from the cloned source).

---

## 🗂️ Files this skill owns

```
bootcamp-orchestrator/
├── SKILL.md
├── README.md
├── config/
│   └── bootcamps.json           ← registry, paths, start dates, core items
├── scripts/
│   ├── status.py                ← unified status (parse progress.md / Bootcamp_Progress.md)
│   ├── mw_lookup.py             ← MW item → MWTGe requirements + local project folder
│   └── weekly.sh                ← digest + Telegram + memory log
└── logs/
    └── last-digest.txt          ← latest digest output (for inspection)
```

---

## 📊 Status output format

Short form (one line per bootcamp):

```
🏗️ MW01: 4/6 (66%)
🤖 MSC-IRE: Week 3/24 — MAEG2020 Engineering Mechanics
```

Full form (per bootcamp):
- Progress summary + percentage
- Current focus / simulator update
- Upcoming items (next 3)
- Recent completions

---

## 🔁 Cron setup

Recommended crons (set in `openclaw.json → skills.entries.<name>` or via `openclaw cron add`):

| When | Action | Command |
|---|---|---|
| Saturday 09:00 HKT | Bootcamp weekly digest (memory + Telegram) | `weekly.sh --memory --send` |
| Sunday 20:00 HKT | MSC Sunday reflection (optional, uses existing `bootcamp_sunday_summary.py`) | run external MSC skill |

The MSC-IRE repo already has `bootcamp_weekly.py` etc. under
`24_Week_Weekend_Bootcamp/skill/` — this skill **complements** rather
than replaces them.

---

## 🛠️ Extending

| Want to… | Edit… |
|---|---|
| Add a new MW item to lookup | `KNOWN_ITEMS` dict in `mw_lookup.py` |
| Track a new bootcamp (e.g. a 3rd repo) | Add entry to `config/bootcamps.json` + parser in `status.py` |
| Change Telegram format | `fmt_*()` functions in `status.py` |
| Schedule digest at a different time | cron expression (no code change) |
| Pull live updates from upstream repos | add `git pull` step to `weekly.sh` (not done by default to keep it fast + offline) |

---

## 🔐 Security notes

- The skill only **reads** the upstream bootcamp repos — never writes.
- Telegram delivery reuses `notify.sh` from `airi-model-switcher` skill.
  No new credentials required if that skill is already wired up.
- `KNOWN_ITEMS` contains curated engineering knowledge from MWTGe.pdf /
  CoP — it's a *reference summary*, not a substitute for reading the
  actual code clauses before signing off an RSE report.