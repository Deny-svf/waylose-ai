# waylose.ai — an on-chain agent that hunts free mints, claims and lists them

**waylose.ai** is an autonomous AI agent (Binance Agent ID `waylose.ai`) that watches
NFT mint trackers around the clock on BNB Chain (56) and Robinhood Chain (4663).
When a new free mint appears it does not ape in blindly — it verifies the contract
on-chain first, mints with a direct contract call, verifies the transaction on-chain,
and manages the listing afterwards.

## How it works

1. **Watch** — sweep mint trackers for new free / paid mints and fair launches.
2. **Audit triage (read-only, before any mint)** — check the contract on-chain:
   contract deployed, `name`/`symbol`/`totalSupply` readable, owner powers noted.
   `GO` = mint immediately. `CAUTION` / `BLOCK` = stop and report.
3. **Mint** — direct contract call, value 0 for free mints. Preview before money
   moves; paid mints only with explicit human approval of the exact amount.
4. **Verify** — confirm the mint on-chain after the transaction lands.
5. **List & track** — list the NFT, track the listing, report on a sale. Listing
   prices never change unless the human says so.

## Safety rules (the whole point)

- Free first. Paid only with explicit approval of the exact amount/contract.
- Preview before money moves; on-chain verification after every transaction.
- The wallet never connects to a mint website — all calls are direct contract calls.
- No silent spending, no surprises.

## Verified results (all on-chain)

- **12,500,000 $WOJAK** claimed in a free Agent ID mint
  (2026-11-11, contract `0x70aB28D6d1569D35B6DcB58D0B2DA0363303C9f5`, BSC).
- **AGC Pool B**: 0.004 BNB = 2 shares, 927,500 AGC vesting linearly over 14 days;
  596,381 AGC claimed so far (claim #9 landed 2026-11-14), one claim a day.
- Free mints listed afterwards: Hopkin Genesis **#2251**, Eclipse Court Genesis
  **#48**, RIGAI Badge **#331**.
- Agent wallet: `0xcD5676cEEA5E5acF8518CAd820A1B2e9818e5255`

## Run the audit triage (read-only, no wallet, no keys)

```bash
python3 demo.py 0x70aB28D6d1569D35B6DcB58D0B2DA0363303C9f5
```

Runs the same read-only contract checks the agent runs before any mint and
prints a `GO` / `CAUTION` / `BLOCK` verdict. Uses public BSC RPC endpoints.

## Run the demo endpoint (free-form, no auth)

```bash
python3 -m waylose.server
# GET /          — agent info
# GET /health    — {"ok": true}
# GET /status    — live agent stats (verified results above)
# GET /audit?address=0x... — live read-only audit triage as JSON
```

## Layout

- `waylose/audit.py` — read-only contract audit triage (BSC JSON-RPC).
- `waylose/server.py` — tiny stdlib HTTP demo endpoint.
- `demo.py` — CLI demo for the audit triage.
- `WHAT_IT_DOES.md` — the 2000-char project description used for submissions.

## Notes

- Stdlib Python only, plus `curl` for RPC transport (BSC dataseeds truncate
  large responses over plain urllib — curl with a browser User-Agent works;
  the code falls back to urllib if curl is missing). No keys, no wallet needed.
- Nothing in this repo sends a transaction. Minting lives in the agent's
  private runtime, behind human approval.
- Built for [Agent Games by zkVerify](https://agentgames.zkverify.io/) —
  Wildcard track. Submitted by @GilangPriawan (dashboard handle `gilangpriawan`).
