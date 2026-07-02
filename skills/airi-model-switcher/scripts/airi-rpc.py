#!/usr/bin/env python3
"""airi-rpc.py — minimal WebSocket client for AIRI server-runtime.

Sends an @moeru/eventa-style event to switch AIRI's active chat provider/model.

Usage:
  airi-rpc.py --list                              # list providers
  airi-rpc.py --select <provider-id> <model-id>   # switch active model
  airi-rpc.py --ping                              # liveness check

Connects to AIRI_WS_URL (default ws://127.0.0.1:6121).
Reference: packages/plugin-sdk/src/plugin/apis/protocol/resources/providers/index.ts
"""

import argparse
import json
import os
import sys
import time
from typing import Any


def _ensure_ws_client():
    try:
        import websocket  # type: ignore  # noqa: F401  # pip install websocket-client OR apt install python3-websocket
        return websocket
    except ImportError:
        print("❌ websocket module required. Install: apt-get install python3-websocket (Debian) OR pip install websocket-client", file=sys.stderr)
        sys.exit(2)


def get_ws_url() -> str:
    return os.environ.get("AIRI_WS_URL", "ws://127.0.0.1:6121")


def rpc_call(payload: dict[str, Any], timeout: float = 5.0) -> dict[str, Any]:
    websocket = _ensure_ws_client()
    url = get_ws_url()
    ws = websocket.create_connection(url, timeout=timeout)
    try:
        ws.send(json.dumps(payload))
        ws.settimeout(timeout)
        raw = ws.recv()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}
    finally:
        ws.close()


def cmd_list(_args: argparse.Namespace) -> int:
    payload = {
        "type": "proj-airi:plugin-sdk:apis:protocol:resources:providers:list-providers",
        "payload": {},
        "ts": int(time.time() * 1000),
    }
    print(f"→ {get_ws_url()}")
    print(f"→ {json.dumps(payload)}")
    try:
        resp = rpc_call(payload)
    except Exception as e:
        print(f"❌ {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"← {json.dumps(resp, indent=2)}")
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    payload = {
        "type": "proj-airi:plugin-sdk:apis:protocol:resources:providers:select",
        "payload": {
            "providerId": args.provider,
            "modelId": args.model,
        },
        "ts": int(time.time() * 1000),
    }
    print(f"→ {get_ws_url()}")
    print(f"→ {json.dumps(payload)}")
    try:
        resp = rpc_call(payload)
    except Exception as e:
        print(f"❌ {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"← {json.dumps(resp, indent=2)}")
    if isinstance(resp, dict) and "error" in resp:
        return 1
    return 0


def cmd_ping(_args: argparse.Namespace) -> int:
    payload = {
        "type": "proj-airi:plugin-sdk:apis:protocol:liveness:ping",
        "payload": {},
        "ts": int(time.time() * 1000),
    }
    print(f"→ {get_ws_url()}")
    try:
        resp = rpc_call(payload)
    except Exception as e:
        print(f"❌ {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"← {json.dumps(resp)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Minimal AIRI server-runtime RPC client")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="List available providers")
    g.add_argument("--select", nargs=2, metavar=("PROVIDER", "MODEL"),
                   help="Switch active provider/model")
    g.add_argument("--ping", action="store_true", help="Liveness ping")
    args = p.parse_args()

    if args.list:
        return cmd_list(args)
    if args.select:
        return cmd_select(argparse.Namespace(provider=args.select[0], model=args.select[1]))
    if args.ping:
        return cmd_ping(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())