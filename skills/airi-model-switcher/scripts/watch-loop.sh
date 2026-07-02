#!/usr/bin/env bash
# watch-loop.sh — background daemon that polls AIRI and auto-switches on failure.
#
# Usage:
#   watch-loop.sh [--interval <sec>] [--once] [--foreground]
#
# Defaults: interval=60s, daemonised (background), logs to logs/watcher.log
# State: logs/state.json (current model, cooldownUntil, lastError)
# PID:   logs/watcher.pid
#
# Behaviour:
#   - Periodically probe .primary via check-health.sh
#   - If primary is unhealthy AND current ≠ primary AND cooldown elapsed → switch back
#   - If current is unhealthy → switch to next healthy in chain
#   - Sends Telegram only on transitions, never on every poll

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${SKILL_DIR}/config/fallback-chain.json"
STATE_FILE="${SKILL_DIR}/logs/state.json"
LOG_FILE="${SKILL_DIR}/logs/watcher.log"
PID_FILE="${SKILL_DIR}/logs/watcher.pid"

interval=60
once=0
foreground=0
for arg in "$@"; do
  case "$arg" in
    --interval) shift; interval="${1:-60}" ;;
    --interval=*) interval="${arg#*=}" ;;
    --once) once=1 ;;
    --foreground) foreground=1 ;;
  esac
done

ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG_FILE" >&2; }

if [[ ! -f "$CONFIG_FILE" ]]; then
  log "❌ config not found: $CONFIG_FILE"
  exit 4
fi
mkdir -p "${SKILL_DIR}/logs"
touch "$LOG_FILE"

if [[ $foreground -eq 0 && $once -eq 0 ]]; then
  nohup "$0" --foreground --interval "$interval" >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  log "started daemon PID=$! interval=${interval}s — tail -f $LOG_FILE"
  exit 0
fi

trap 'log "SIGTERM — exiting"; rm -f "$PID_FILE"; exit 0' SIGTERM SIGINT
log "watcher started PID=$$ interval=${interval}s"

cycle=0
while true; do
  cycle=$((cycle + 1))

  current=$(jq -r '.current // empty' "$STATE_FILE" 2>/dev/null)
  primary=$(jq -r '.primary' "$CONFIG_FILE")
  cooldown_until=$(jq -r '.cooldownUntil // 0' "$STATE_FILE" 2>/dev/null)
  now=$(date +%s)
  in_cooldown=0
  [[ "$cooldown_until" != "0" && "$cooldown_until" != "null" && "$now" -lt "$cooldown_until" ]] && in_cooldown=1

  if [[ -n "$current" ]]; then
    rc=0
    "${SKILL_DIR}/scripts/check-health.sh" "$current" >/dev/null 2>&1 || rc=$?
    if [[ $rc -ne 0 && $in_cooldown -eq 0 ]]; then
      log "cycle $cycle: current '$current' unhealthy (rc=$rc) — failover"
      SWITCH_REASON="auto-failover" "${SKILL_DIR}/scripts/switch-model.sh" --next-healthy 2>>"$LOG_FILE" || log "failover failed"
    fi
  fi

  if [[ $((cycle % 10)) -eq 0 ]]; then
    rc=0
    "${SKILL_DIR}/scripts/check-health.sh" "$primary" >/dev/null 2>&1 || rc=$?
    cur_now=$(jq -r '.current // empty' "$STATE_FILE" 2>/dev/null)
    if [[ $rc -eq 0 && "$cur_now" != "$primary" ]]; then
      log "cycle $cycle: primary '$primary' recovered — switching back"
      SWITCH_REASON="auto-recovery" "${SKILL_DIR}/scripts/switch-model.sh" "$primary" 2>>"$LOG_FILE" || log "recovery switch failed"
    fi
  fi

  [[ $once -eq 1 ]] && exit 0
  sleep "$interval"
done