#!/usr/bin/env bash
# check-health.sh — probe one AIRI provider's health
#
# Usage:
#   check-health.sh <model-id>           # checks one entry from fallback-chain.json
#   check-health.sh --all                # checks all, prints table
#   check-health.sh --json <model-id>    # machine-readable single result
#
# Exit codes:
#   0 = healthy
#   1 = degraded (5xx, timeout, dns fail)
#   2 = rate-limited (429)
#   3 = auth-bad (401/403)
#   4 = config-missing / parse-fail
#
# Required tools: curl, jq, python3

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${SKILL_DIR}/config/fallback-chain.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "❌ Config not found: $CONFIG_FILE" >&2
  echo "   Copy: cp ${SKILL_DIR}/config/fallback-chain.example.json ${CONFIG_FILE}" >&2
  exit 4
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq required. Install: apt-get install jq" >&2
  exit 4
fi

# --- helpers ---------------------------------------------------------------

get_entry() {
  local id="$1"
  jq --arg id "$id" '.models[] | select(.id == $id)' "$CONFIG_FILE"
}

probe_base_url() {
  local url="$1"
  # 2xx/3xx/401/403/404/405 = reachable. 5xx / timeout = degraded.
  curl -sS -o /dev/null -w '%{http_code}|%{time_total}' \
       --max-time 5 --connect-timeout 3 \
       -X HEAD "$url" 2>/dev/null || echo "000|0"
}

probe_auth() {
  local entry_json="$1"
  local provider model base_url key
  provider=$(echo "$entry_json" | jq -r '.provider')
  model=$(echo "$entry_json" | jq -r '.model')
  base_url=$(echo "$entry_json" | jq -r '.baseUrl')
  key_env=$(echo "$entry_json" | jq -r '.apiKeyEnv // empty')

  local key=""
  if [[ -n "$key_env" ]]; then
    key="${!key_env:-}"
    if [[ -z "$key" ]]; then
      echo "no-key"
      return
    fi
  fi

  case "$provider" in
    openai|ollama|openai-compatible)
      local resp code
      resp=$(curl -sS -o /dev/null -w '%{http_code}' \
        --max-time 8 \
        -H "Authorization: Bearer ${key}" \
        -H "Content-Type: application/json" \
        -X POST "${base_url%/}/chat/completions" \
        -d "{\"model\":\"${model}\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":1}" \
        2>/dev/null) || resp="000"
      code="$resp"
      case "$code" in
        2*) echo "ok" ;;
        429) echo "rate-limited" ;;
        401|403) echo "auth-bad" ;;
        5*) echo "degraded" ;;
        000) echo "timeout" ;;
        *) echo "degraded" ;;
      esac
      ;;
    anthropic)
      local resp code
      resp=$(curl -sS -o /dev/null -w '%{http_code}' \
        --max-time 8 \
        -H "x-api-key: ${key}" \
        -H "anthropic-version: 2023-06-01" \
        -H "Content-Type: application/json" \
        -X POST "${base_url%/}/messages" \
        -d "{\"model\":\"${model}\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
        2>/dev/null) || resp="000"
      code="$resp"
      case "$code" in
        2*) echo "ok" ;;
        429) echo "rate-limited" ;;
        401|403) echo "auth-bad" ;;
        5*) echo "degraded" ;;
        000) echo "timeout" ;;
        *) echo "degraded" ;;
      esac
      ;;
    google-generative-ai)
      local resp code
      resp=$(curl -sS -o /dev/null -w '%{http_code}' \
        --max-time 8 \
        -X POST "${base_url%/}/models/${model}:generateContent?key=${key}" \
        -H "Content-Type: application/json" \
        -d '{"contents":[{"parts":[{"text":"ping"}]}],"generationConfig":{"maxOutputTokens":1}}' \
        2>/dev/null) || resp="000"
      code="$resp"
      case "$code" in
        2*) echo "ok" ;;
        429) echo "rate-limited" ;;
        401|403) echo "auth-bad" ;;
        5*) echo "degraded" ;;
        000) echo "timeout" ;;
        *) echo "degraded" ;;
      esac
      ;;
    *)
      echo "unknown-provider"
      ;;
  esac
}

health_one() {
  local id="$1"
  local json_mode="${2:-}"
  local entry base_url

  entry=$(get_entry "$id")
  if [[ -z "$entry" || "$entry" == "null" ]]; then
    [[ "$json_mode" == "--json" ]] && echo "{\"id\":\"$id\",\"status\":\"not-found\"}" || echo "❌ model id not found: $id"
    return 4
  fi

  base_url=$(echo "$entry" | jq -r '.baseUrl')
  local base_code base_time
  IFS='|' read -r base_code base_time <<< "$(probe_base_url "$base_url")"

  case "$base_code" in
    000)
      result="degraded"; detail="connection failed"
      ;;
    5*)
      result="degraded"; detail="server error ${base_code}"
      ;;
    2*|3*|401|403|404|405)
      local auth_result
      auth_result=$(probe_auth "$entry")
      case "$auth_result" in
        ok)            result="healthy";  detail="ok" ;;
        rate-limited)  result="rate-limited"; detail="429 from upstream" ;;
        auth-bad)      result="auth-bad"; detail="401/403 — check API key env" ;;
        degraded)      result="degraded"; detail="upstream 5xx during probe" ;;
        timeout)       result="degraded"; detail="upstream timeout" ;;
        no-key)        result="unknown";  detail="base reachable; no API key set in env" ;;
        *)             result="degraded"; detail="upstream: ${auth_result}" ;;
      esac
      ;;
    *)
      result="degraded"; detail="unexpected HTTP ${base_code}"
      ;;
  esac

  local http_time="${base_time}s"
  local model provider
  model=$(echo "$entry" | jq -r '.model')
  provider=$(echo "$entry" | jq -r '.provider')

  if [[ "$json_mode" == "--json" ]]; then
    jq -nc \
      --arg id "$id" --arg provider "$provider" --arg model "$model" \
      --arg status "$result" --arg detail "$detail" \
      --arg http "$base_code" --arg latency "$http_time" \
      '{id:$id, provider:$provider, model:$model, status:$status, detail:$detail, http:$http, latency:$latency}'
  else
    local icon="✅"
    [[ "$result" != "healthy" ]] && icon="⚠️"
    [[ "$result" == "degraded" || "$result" == "auth-bad" ]] && icon="❌"
    printf "%s %-30s %-20s %-15s HTTP=%s %-12s — %s\n" \
      "$icon" "$id" "$provider/$model" "$result" "$base_code" "$http_time" "$detail"
  fi

  case "$result" in
    healthy) return 0 ;;
    rate-limited) return 2 ;;
    auth-bad) return 3 ;;
    *) return 1 ;;
  esac
}

# --- main ------------------------------------------------------------------

if [[ "${1:-}" == "--all" ]]; then
  echo "AIRI provider health check — $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "----------------------------------------------------------------"
  ids=$(jq -r '.models[].id' "$CONFIG_FILE")
  overall=0
  for id in $ids; do
    health_one "$id" || overall=1
  done
  echo "----------------------------------------------------------------"
  echo "primary: $(jq -r '.primary' "$CONFIG_FILE")"
  exit $overall
elif [[ "${1:-}" == "--json" ]]; then
  health_one "${2:-}" "--json"
else
  health_one "${1:-}"
fi