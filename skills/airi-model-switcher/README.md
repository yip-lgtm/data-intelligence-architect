# AIRI Model Switcher — Architecture

## What this skill solves

When AIRI (moeru-ai/airi) is the long-running desktop companion, you want
the **chat model** to keep working even when:

- OpenAI rate-limits / 5xx
- Anthropic is in an outage
- Your local Ollama server is down
- The cheap model starts giving bad answers and you want to promote the
  expensive one temporarily

OpenClaw's built-in `agents.defaults.model.fallbacks` only applies to the
**OpenClaw agent itself**. AIRI is a separate process with its own model
selection. This skill automates AIRI's model selection.

## Components

```
            ┌──────────────────────────────────────────────────────────┐
            │                                                          │
            │   watch-loop.sh  (every Ns)                              │
            │     │                                                    │
            │     ├─ check-health.sh --primary                         │
            │     │     └─ curl / token-probe                          │
            │     │                                                    │
            │     ├─ if current unhealthy ───► switch-model.sh         │
            │     │                            --next-healthy          │
            │     │                              │                     │
            │     │                              ├─ airi-rpc.py        │
            │     │                              │   (WebSocket)       │
            │     │                              ├─ edit settings.json │
            │     │                              └─ notify.sh          │
            │     │                                  │                 │
            │     │                                  └─ Telegram Bot   │
            │     │                                                    │
            │     └─ every 10 cycles: recovery probe → switch back     │
            │                                                          │
            │   Agent (chat)                                           │
            │     ├─ "AIRI 切去 gpt-4o"  → switch-model.sh gpt-4o      │
            │     ├─ "AIRI status"       → check-health.sh --all       │
            │     └─ "停 auto-switch"    → kill $(cat watcher.pid)     │
            │                                                          │
            └──────────────────────────────────────────────────────────┘
                                       │
                                       ▼
              ┌──────────────────────────────────────────────────┐
              │  AIRI server-runtime  ws://127.0.0.1:6121        │
              │  AIRI stage-tamagotchi / stage-web  (UI)          │
              └──────────────────────────────────────────────────┘
```

## State machine

`logs/state.json`:

```json
{
  "current": "openai-gpt-4o",
  "previous": "anthropic-claude-sonnet",
  "reason": "auto-failover",
  "transport": "ws-rpc",
  "result": "ok",
  "ts": "2026-07-02T05:00:00Z"
}
```

`cooldownUntil` is added by the watcher to avoid flapping when a provider
is intermittently degraded.

## Why three switch strategies?

| Strategy | When it works | Pros | Cons |
|---|---|---|---|
| WS RPC (`airi-rpc.py`) | AIRI server-runtime is running | Instant, atomic | Requires the exact protocol event name; if AIRI changes it, breaks |
| File edit (`AIRI_SETTINGS_FILE`) | You point us at AIRI's persisted settings file | Works even when AIRI is closed | Needs a restart or hot-reload hook on AIRI side |
| Notify-only | Always | Always works | Requires user intervention |

The orchestrator tries in order and stops at the first success — this is
deliberate so a future AIRI protocol change can be replaced without
breaking the other paths.

## How to install / configure

```bash
cd ~/.openclaw/workspace/skills/airi-model-switcher    # or your workspace
cp config/fallback-chain.example.json config/fallback-chain.json
$EDITOR config/fallback-chain.json                     # fill in apiKeyEnv, baseUrl
chmod 600 config/fallback-chain.json                   # protect keys

# Set environment (or in openclaw.json → skills.entries.<name>.env)
export AIRI_WS_URL=ws://127.0.0.1:6121
export AIRI_SETTINGS_FILE=/path/to/airi-settings.json
export TELEGRAM_BOT_TOKEN=...      # optional
export TELEGRAM_CHAT_ID=...        # optional

# One-off health check
./scripts/check-health.sh --all

# One-off switch
./scripts/switch-model.sh openai-gpt-4o

# Start the auto-failover watcher
./scripts/watch-loop.sh --interval 60 &
echo $! > logs/watcher.pid

# Stop it
kill $(cat logs/watcher.pid)
```

## Logging

Every switch is appended to `logs/switch.log` (machine) and the agent
mirrors the same record into `/app/data-intelligence-architect/memory/<YYYY-MM-DD>.md`
under the `## 🌀 AIRI model switch` heading so future-you can search
decisions over time.

## Extending

| Want to… | Edit… |
|---|---|
| Add a provider | `config/fallback-chain.json` only |
| Change switch protocol | `scripts/airi-rpc.py` + add a new `try_*` in `switch-model.sh` |
| Add Discord/Slack notification | copy `scripts/notify.sh` → `scripts/notify-discord.sh` |
| Tune probe sensitivity | `--interval` flag + `watcher.testPrompt` / `recoveryProbeInterval` in config |
| Run on a cron instead of the daemon | `crontab: */5 * * * * /path/switch-model.sh --next-healthy` |