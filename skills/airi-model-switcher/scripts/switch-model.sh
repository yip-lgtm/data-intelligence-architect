#!/usr/bin/env bash
# switch-model.sh — orchestrate an AIRI model switch.
#
# Usage:
#   switch-model.sh <model-id>          # switch to specific model in fallback-chain.json
#   switch-model.sh --primary           # switch to .primary entry
#   switch-model.sh --next-healthy      # auto-pick first healthy model (after current)
#   switch-model.sh --dry-run <model-id> # show what would happen, no changes
#
# Exit codes:
#   0 = switched (or already on target)
#   1 = all strategies failed
#   2 = user intervention required (notify-only mode)
#   4 = config-missing / parse-fail

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${SKILL_DIR}/config/fallback-chain.json"
STATE_FILE="${SKILL_DIR}/logs/state.json"
LOG_FILE="${SKILL_DIR}/logs/switch.log"
AIRI_WS_URL="${AIRI_WS_URL:-ws://127.0.0.1:6121}"
AIRI_SETTINGS_FILE="${AIRI_SETTINGS_FILE:-}"

ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG_FILE" >&2; }

if [[ ! -f "$CONFIG_FILE" ]]; then
  log "❌ config not found: $CONFIG_FILE"
  exit 4
fi
mkdir -p "${SKILL_DIR}/logs"
touch "$LOG_FILE"

# --- state management ------------------------------------------------------

get_current() {
  if [[ -f "$STATE_FILE" ]]; then
    jq -r '.current // empty' "$STATE_FILE"
  fi
}

set_current() {
  local new_id="$1" reason="$2" transport="$3" result="$4"
  local prev
  prev=$(get_current)
  jq -n \
    --arg current "$new_id" \
    --arg prev "${prev:-}" \
    --arg reason "$reason" \
    --arg transport "$transport" \
    --arg result "$result" \
    --arg ts "$(ts)" \
    '{current:$current, previous:$prev, reason:$reason, transport:$transport, result:$result, ts:$ts}' \
    > "$STATE_FILE"
}

# --- switch strategies ------------------------------------------------------

# Strategy A: WebSocket RPC via airi-rpc.py
try_ws_rpc() {
  local id="$1"
  local entry provider model_name
  entry=$(jq -c --arg m "$id" '.models[] | select(.id == $m)' "$CONFIG_FILE")
  if [[ -z "$entry" || "$entry" == "null" ]]; then
    log "  [ws-rpc] model '$id' not in chain"
    return 1
  fi
  provider=$(echo "$entry" | jq -r '.provider')
  model_name=$(echo "$entry" | jq -r '.model')
  log "  [ws-rpc] sending: provider=$provider model=$model_name (chain id=$id) → $AIRI_WS_URL"
  local out rc
  out=$(python3 "${SKILL_DIR}/scripts/airi-rpc.py" --select "$provider" "$model_name" 2>&1) && rc=0 || rc=$?
  echo "$out" | tee -a "$LOG_FILE" >&2
  if [[ $rc -eq 0 ]]; then
    log "  [ws-rpc] ✅ switched"
    return 0
  fi
  log "  [ws-rpc] ❌ failed (rc=$rc)"
  return 1
}

# Strategy B: edit AIRI's settings file
try_file_edit() {
  local id="$1"
  if [[ -z "$AIRI_SETTINGS_FILE" || ! -f "$AIRI_SETTINGS_FILE" ]]; then
    log "  [file-edit] skipped (AIRI_SETTINGS_FILE unset or file missing)"
    return 1
  fi
  log "  [file-edit] patching $AIRI_SETTINGS_FILE"
  local provider model_name
  provider=$(jq -r --arg m "$id" '.models[] | select(.id == $m) | .provider' "$CONFIG_FILE")
  model_name=$(jq -r --arg m "$id" '.models[] | select(.id == $m) | .model' "$CONFIG_FILE")
  local tmp
  tmp=$(mktemp)
  if jq --arg p "$provider" --arg mn "$model_name" \
       '.activeProvider = $p | .activeModel = $mn' \
       "$AIRI_SETTINGS_FILE" > "$tmp" 2>>"$LOG_FILE"; then
    mv "$tmp" "$AIRI_SETTINGS_FILE"
    log "  [file-edit] ✅ patched"
    return 0
  fi
  rm -f "$tmp"
  log "  [file-edit] ❌ jq failed"
  return 1
}

# Strategy C: notify-only
try_notify_only() {
  local model="$1" reason="$2"
  log "  [notify] user must switch manually"
  "${SKILL_DIR}/scripts/notify.sh" \
    "🌀 AIRI: failed to switch automatically to *${model}* (${reason}). Please switch manually in AIRI settings." \
    2>>"$LOG_FILE" || true
  return 0
}

# --- helpers ---------------------------------------------------------------

pick_next_healthy() {
  local current="$1"
  local ids
  ids=$(jq -r '.models[].id' "$CONFIG_FILE")
  local found=0
  for id in $ids; do
    if [[ $found -eq 1 ]]; then
      local rc
      "${SKILL_DIR}/scripts/check-health.sh" "$id" >/dev/null 2>&1
      rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "$id"
        return 0
      fi
    fi
    [[ "$id" == "$current" ]] && found=1
  done
  for id in $ids; do
    if [[ "$id" != "$current" ]]; then
      local rc
      "${SKILL_DIR}/scripts/check-health.sh" "$id" >/dev/null 2>&1
      rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "$id"
        return 0
      fi
    fi
  done
  return 1
}

# --- main ------------------------------------------------------------------

target="${1:-}"
dry_run=0
reason="${SWITCH_REASON:-user}"
[[ "${2:-}" == "--dry-run" ]] && dry_run=1

case "$target" in
  --primary)
    target=$(jq -r '.primary' "$CONFIG_FILE")
    ;;
  --next-healthy)
    cur=$(get_current)
    target=$(pick_next_healthy "$cur") || { log "❌ no healthy model in chain"; exit 1; }
    reason="auto-failover"
    ;;
  --dry-run)
    dry_run=1
    target="${2:-}"
    ;;
esac

if [[ -z "$target" || "$target" == "null" ]]; then
  log "❌ no target model specified"
  exit 4
fi

cur=$(get_current)
if [[ "$cur" == "$target" ]]; then
  log "✓ already on $target — no-op"
  exit 0
fi

log "═══ switch requested: $cur → $target (reason=$reason)"

if [[ $dry_run -eq 1 ]]; then
  log "DRY RUN — no changes"
  echo "would switch: $cur → $target"
  exit 0
fi

transport="none"; result="failed"; rc=1

if try_ws_rpc "$target"; then
  transport="ws-rpc"; result="ok"; rc=0
elif try_file_edit "$target"; then
  transport="file-edit"; result="ok"; rc=0
elif try_notify_only "$target" "$reason"; then
  transport="notify-only"; result="notify-only"; rc=2
fi

set_current "$target" "$reason" "$transport" "$result"
log "═══ result: $result via $transport (rc=$rc)"

if [[ "$transport" != "none" ]]; then
  "${SKILL_DIR}/scripts/notify.sh" \
    "🌀 AIRI switched: \`${cur:-none}\` → \`${target}\` (${result}, ${transport})" \
    2>>"$LOG_FILE" || true
fi

exit $rc