#!/usr/bin/env bash
# notify.sh — send a Telegram message via Bot API. Best-effort; never fails the caller.
#
# Usage:
#   notify.sh "<message>" [chat-id] [bot-token]
#
# Env fallback: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
#
# Exit codes:
#   0 = sent (or skipped because disabled)
#   1 = curl/parse failure (logged, not fatal)

set -uo pipefail

msg="${1:-}"
chat_id="${2:-${TELEGRAM_CHAT_ID:-}}"
bot_token="${3:-${TELEGRAM_BOT_TOKEN:-}}"

if [[ -z "$msg" ]]; then
  echo "notify.sh: empty message" >&2
  exit 1
fi
if [[ -z "$bot_token" || -z "$chat_id" ]]; then
  echo "notify.sh: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping" >&2
  exit 0
fi

if [[ ${#msg} -gt 4000 ]]; then
  msg="${msg:0:3990}…(truncated)"
fi

esc=$(printf '%s' "$msg" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read())[1:-1])')

http_code=$(curl -sS -o /tmp/notify-resp.$$.json -w '%{http_code}' \
  --max-time 8 \
  -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":\"${chat_id}\",\"text\":\"${esc}\",\"parse_mode\":\"MarkdownV2\",\"disable_web_page_preview\":true}" \
  2>/dev/null) || http_code=000

if [[ "$http_code" =~ ^2 ]]; then
  echo "notify: sent (HTTP $http_code)" >&2
  rm -f /tmp/notify-resp.$$.json
  exit 0
fi

echo "notify: HTTP $http_code — $(cat /tmp/notify-resp.$$.json 2>/dev/null)" >&2
rm -f /tmp/notify-resp.$$.json
exit 1