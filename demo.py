#!/usr/bin/env python3
"""Demo: run the waylose.ai read-only audit triage on a BSC contract.

Usage:  python3 demo.py 0x70aB28D6d1569D35B6DcB58D0B2DA0363303C9f5
No wallet, no keys, no transactions — read-only checks against public BSC RPC.
"""
import json
import sys

from waylose.audit import audit

if __name__ == "__main__":
    address = sys.argv[1] if len(sys.argv) > 1 else \
        "0x70aB28D6d1569D35B6DcB58D0B2DA0363303C9f5"  # $WOJAK, BSC
    print(json.dumps(audit(address), indent=2))
