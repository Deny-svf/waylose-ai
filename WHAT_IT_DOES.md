# Wildcard submission texts

## PROJECT TITLE
waylose.ai — an on-chain agent that hunts free mints, claims and lists them

## WHAT IT DOES (max 2000 chars)
waylose.ai (Binance Agent ID waylose.ai) is an autonomous agent that hunts free
NFT mints on BNB Chain and Robinhood Chain. It watches mint trackers around the
clock; when a new mint appears it verifies the contract on-chain first with a
read-only audit triage (deployed code, name/symbol/totalSupply, owner powers),
then mints with a direct contract call, verifies the transaction on-chain, and
manages the listing afterwards. Safety rules: free first, paid only with explicit
human approval, a transaction preview before money moves, on-chain verification
after every transaction, and the wallet never connects to a mint website.
Verified on-chain results: 12,500,000 $WOJAK claimed in a free mint, 596,381 /
927,500 AGC claimed from a vested position, and free mints listed afterwards
(Hopkin #2251, Eclipse Court #48, RIGAI #331). This repo contains the real
read-only audit triage plus a demo HTTP endpoint; run `python3 demo.py <address>`
to audit any BSC contract, or `python3 -m waylose.server` for GET /status and
GET /audit?address=0x... No keys or wallet needed for the demo.

## MESSAGE TO JUDGES (max 1000 chars, optional)
Everything in this repo is real and runnable with no keys: the audit triage is
the same read-only check the agent runs before every mint, and the demo endpoint
serves the agent's verified on-chain results. The agent itself runs privately
behind human approval for any paid action — this repo is the verifiable,
open part of it. Thank you for reviewing waylose.ai.
