---
name: airi-model-switcher
description: Automate AIRI (moeru-ai/airi) chat-model switching across providers with health checks, fallback chains, and Telegram notifications. Triggers on requests like "switch AIRI model", "AIRI fall back", "why is AIRI slow", or "set up AIRI failover".
metadata:
  {
    "openclaw":
      {
        "emoji": "🌀",
        "requires":
          {
            "bins": ["curl", "python3"],
            "env": [],
            "optionalEnv":
              ["AIRI_WS_URL", "AIRI_SETTINGS_FILE", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
          },
        "primaryEnv": "AIRI_WS_URL",
        "configPaths":
          ["/app/data-intelligence-architect/skills/airi-model-switcher/config/fallback-chain.json"]
      }
  }
---

# AIRI Model Switcher 🌀

Automate **chat-model** switching in a running **Project AIRI** instance
(`moeru-ai/airi`, Electron / web). Detects provider failure (timeout, 4xx/5xx,
rate limit), rotates through a user-defined **fallback chain**, optionally
restores the original model when the primary recovers, and notifies the user
via Telegram.

> Use when AIRI is the long-running desktop/web companion and the user wants
> "set and forget" model failover. This is **not** for OpenClaw's own model
> failover — that's already handled by `agents.defaults.model.fallbacks`.

---

## ⚡ Quick start

1. **Copy example config**

   ```bash
   cp {baseDir}/config/fallback-chain.example.json \
      {baseDir}/config/fallback-chain.json
   ```

2. **Edit `fallback-chain.json`** with your real providers / API keys / base URLs.

3. **Tell the agent** (in chat):
   > "AIRI 健康檢查"
   > "AIRI 而家用咗咩 model？"
   > "切 AIRI 去 claude-sonnet-4.6"
   > "AIRI auto-failover 開咗未？"

4. **Optional: start the watcher daemon**

   ```bash
   {baseDir}/scripts/watch-loop.sh --interval 60 &
   ```

---

## 🧠 When the agent should invoke this skill

| Trigger phrase (examples)                              | Action                                   |
| ------------------------------------------------------ | ---------------------------------------- |
| "AIRI 切去 \<model\>" / "switch AIRI to \<model\>"     | `scripts/switch-model.sh <model-id>`     |
| "AIRI health check" / "AIRI status"                    | `scripts/check-health.sh --all`          |
| "AIRI fail-over" / "AIRI fallback 開咗"               | `scripts/switch-model.sh --next-healthy` |
| "AIRI 自動切 model 開咗未？"                          | show watcher PID + last log lines        |
| "停 AIRI auto-switch"                                  | `kill $(cat logs/watcher.pid)`           |
| "AIRI 復原返主 model"                                  | `scripts/switch-model.sh --primary`      |
| "睇下 AIRI fallback chain"                            | `cat config/fallback-chain.json`         |

The agent should NEVER issue `pnpm install` / build commands inside the
AIRI source tree during a switch — those affect a different lifecycle.

---

## 🗂️ Files this skill owns

```
airi-model-switcher/
├── SKILL.md                  ← this file
├── config/
│   ├── fallback-chain.example.json
│   └── fallback-chain.json   ← user-edited, gitignored in real use
├── scripts/
│   ├── check-health.sh       ← probe one provider
│   ├── switch-model.sh       ← orchestrator (calls WS RPC or file edit)
│   ├── airi-rpc.py           ← tiny WebSocket client for AIRI server-runtime
│   ├── watch-loop.sh         ← background daemon
│   └── notify.sh             ← send Telegram message
├── logs/                     ← state.json, watcher.log, switch.log
└── README.md                 ← architecture + advanced config
```

---

## 🔌 How `switch-model.sh` actually switches AIRI's model

AIRI stores active provider / model in **two** places; this skill tries
them in order and stops at the first that succeeds:

1. **WebSocket RPC** — connects to `AIRI_WS_URL` (default
   `ws://127.0.0.1:6121`, the AIRI `server-runtime`).
   Sends an `@moeru/eventa`-style event:

   ```json
   { "type": "proj-airi:plugin-sdk:apis:protocol:resources:providers:select",
     "payload": { "providerId": "<id>", "modelId": "<model>" } }
   ```

   Reference: `packages/plugin-sdk/src/plugin/apis/protocol/resources/providers/index.ts`.

2. **Settings file edit** — if `AIRI_SETTINGS_FILE` env var is set,
   `jq`-patches the active provider/model in AIRI's persisted settings
   (electron-store JSON for desktop, IndexedDB-shimmed JSON for web/PWA).

3. **Notification only** — if both above fail, the script writes a
   structured "please switch manually" log + sends a Telegram message,
   then exits non-zero so the caller can retry / escalate.

The agent **must log every switch attempt** to
`/app/data-intelligence-architect/memory/<YYYY-MM-DD>.md` with:

```md
## 🌀 AIRI model switch — <timestamp>
- from: <prev-provider>/<prev-model>
- to:   <new-provider>/<new-model>
- reason: <health|user|cooldown|recovery>
- transport: <ws-rpc|file-edit|notify-only>
- result: <ok|failed>
```

---

## 🚦 Health-check policy

`check-health.sh` for one provider:

1. DNS resolve base URL (timeout 3 s).
2. `HEAD` base URL (timeout 5 s) — must return 2xx/3xx/401/403 (provider up).
3. If API key available, send a **minimal token request** (1 token, max-tokens 1)
   to confirm auth + quota. Heuristic: `429` → rate-limited; `401/403` → bad key;
   `5xx` → provider degraded; timeout → network failure.

Output: exit code `0` healthy / `1` degraded / `2` rate-limited / `3` auth bad.

`--all` flag runs every entry in `fallback-chain.json` and prints a table.

---

## 🔁 Watch-loop semantics (`watch-loop.sh`)

- Polls every `--interval` seconds (default 60).
- Sends one tiny prompt through the current AIRI model — if it fails,
  tries the next healthy entry in the chain.
- Maintains `logs/state.json` with `currentIndex`, `lastError`,
  `cooldownUntil`. Cooldown avoids flapping when a provider is flaky.
- Telegram notification on every **transition** (not on every poll).
- Graceful shutdown on SIGTERM; writes final state.

---

## 🔐 Security notes

- API keys live ONLY in `config/fallback-chain.json` — that file must be
  gitignored (`echo "config/fallback-chain.json" >> .gitignore`).
- `airi-rpc.py` connects only to the loopback or LAN WS endpoint — never
  call out to a public relay.
- Telegram `notify.sh` uses Bot API via `curl`; never echo the bot token
  in agent replies.

---

## 🛠️ Extending

To add a new provider: edit `fallback-chain.json` (no code change needed).
To add a new switch transport: extend `switch-model.sh` with another
`try_*` function — keep it idempotent and always log.
To add Slack/Discord notification: copy `notify.sh` and swap the endpoint.