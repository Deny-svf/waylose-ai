"""Read-only contract audit triage for waylose.ai.

The same checks the agent runs on-chain BEFORE any mint. Read-only:
no wallet, no keys, no transactions. Uses public BSC JSON-RPC endpoints.

Verdict:
  GO       — contract deployed, basic reads work, nothing blocking seen.
  CAUTION  — something could not be verified (e.g. a standard read reverted).
  BLOCK    — no code at the address (not a contract) or RPC unreachable.
"""

import http.client
import json
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) waylose.ai/1.0"}
RPCS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-rpc.publicnode.com",
]

# function selectors
SEL = {
    "name": "0x06fdde03",
    "symbol": "0x95d89b41",
    "totalSupply": "0x18160ddd",
    "owner": "0x8da5cb5b",
}


def _rpc_curl(url, method, params):
    """Transport via curl: Python urllib gets IncompleteRead on large BSC
    responses (dataseed truncates the connection); curl with a browser UA
    works reliably. Falls back to urllib if curl is missing."""
    import subprocess
    payload = json.dumps({"jsonrpc": "2.0", "id": 1,
                          "method": method, "params": params})
    cmd = ["curl", "-s", "-m", "20", "-A", UA["User-Agent"],
           "-H", "Content-Type: application/json", "-d", payload, url]
    out = subprocess.run(cmd, capture_output=True, timeout=25)
    if out.returncode != 0 or not out.stdout:
        raise ConnectionError(f"curl failed rc={out.returncode}")
    return json.loads(out.stdout)


def _rpc_urllib(url, method, params):
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _rpc(url, method, params, tries=3):
    """BSC public RPCs are flaky (cut connections, intermittent 403s) —
    retry each call a few times with a pause before giving up."""
    last = None
    for attempt in range(tries):
        try:
            return _rpc_curl(url, method, params)
        except FileNotFoundError:
            return _rpc_urllib(url, method, params)
        except (urllib.error.URLError, urllib.error.HTTPError,
                http.client.HTTPException,  # IncompleteRead, RemoteDisconnected
                ConnectionError, TimeoutError, OSError,
                json.JSONDecodeError, ValueError) as e:
            last = e
            time.sleep(1 + attempt)
    raise last


def _call(rpc, to, data, block="latest"):
    res = _rpc(rpc, "eth_call", [{"to": to, "data": data}, block])
    if "error" in res:
        raise ValueError(res["error"].get("message", "eth_call error"))
    return res["result"]


def _decode_string(hexdata):
    # ABI-encoded string: offset(32) + length(32) + data
    try:
        raw = bytes.fromhex(hexdata[2:])
        if len(raw) < 64:
            return None
        length = int.from_bytes(raw[32:64], "big")
        return raw[64:64 + length].decode("utf-8", "replace")
    except Exception:
        return None


def _decode_uint(hexdata):
    try:
        return int(hexdata, 16)
    except Exception:
        return None


def _first_working_rpc():
    for url in RPCS:
        try:
            _rpc(url, "eth_blockNumber", [])
            return url
        except Exception:
            continue
    return None


def audit(address):
    """Run the read-only triage on a BSC contract address. Returns a dict."""
    address = address.strip()
    checks = {}
    rpc = _first_working_rpc()
    if rpc is None:
        return {"address": address, "verdict": "BLOCK",
                "reasons": ["no BSC RPC reachable"], "checks": checks}

    # 1. is there code at the address?
    try:
        code = _rpc(rpc, "eth_getCode", [address, "latest"])["result"]
        checks["deployed"] = code not in ("0x", "0x0", "")
    except Exception as e:
        return {"address": address, "verdict": "BLOCK",
                "reasons": [f"eth_getCode failed: {e}"], "checks": checks}
    if not checks["deployed"]:
        return {"address": address, "verdict": "BLOCK",
                "reasons": ["no code at address — not a contract"],
                "checks": checks}

    # 2. standard reads (each optional — a revert is a CAUTION, not a BLOCK)
    reasons = []
    for name in ("name", "symbol"):
        try:
            checks[name] = _decode_string(_call(rpc, address, SEL[name]))
            if not checks[name]:
                reasons.append(f"{name}() unreadable")
        except Exception:
            checks[name] = None
            reasons.append(f"{name}() reverted")
    try:
        checks["totalSupply"] = _decode_uint(_call(rpc, address, SEL["totalSupply"]))
        if checks["totalSupply"] is None:
            reasons.append("totalSupply() unreadable")
    except Exception:
        checks["totalSupply"] = None
        reasons.append("totalSupply() reverted")
    try:
        owner = _call(rpc, address, SEL["owner"])
        checks["owner"] = "0x" + owner[-40:] if owner and len(owner) >= 42 else None
        if checks["owner"]:
            reasons.append(f"has owner {checks['owner']} (owner powers apply)")
    except Exception:
        checks["owner"] = None

    verdict = "CAUTION" if reasons else "GO"
    return {"address": address, "verdict": verdict, "reasons": reasons,
            "checks": checks, "rpc": rpc}
