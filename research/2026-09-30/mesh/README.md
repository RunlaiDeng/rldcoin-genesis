# Progressive discovery and multi-hop node relay — September 30, 2026

The node-network objective is to extend as users start nodes: discover reachable neighbors, learn distant identities through signed information, and relay evidence over paths such as **Earth ↔ Proxima Centauri ↔ Andromeda**. No direct Earth–Andromeda connection or always-online Earth directory is required. A real first contact is still necessary; discovery and delivery respect causal light-time.

This package is a **supplemental ground contact-spool prototype**, separately started alongside regional nodes. It does not change a signed consensus implementation, authorize a new mainnet, establish a physical stellar route, or automatically add discovery to the native ledger binary. It is not BPv7. Self-signed region labels are not genesis or monetary authority.

- [N1–N10 requirements, assumptions and open gates](docs/research/INTERSTELLAR_NODE_MESH_REQUIREMENTS.md)
- [Start a node, reproduce checks and operate contact adapters](docs/operations/INTERSTELLAR_NODE_MESH.md)
- [Three-process drill report](docs/operations/evidence/interstellar-mesh-20260930.json)
- [Fresh testnet qualification](../../../earth/testnet-20260930/README.md)
- [Current delivery plan](../../../MASTER_PLAN.md)

## Verified ground behavior

16 mesh checks and 18 existing transport/route-budget checks passed. Three actual local daemons, labelled Earth, Proxima and Andromeda, configured only two adjacent directory contacts and automatically learned all three identities. A frame crossed two signed hops unchanged. A stopped relay and sender restart preserved queued evidence; restoring the relay delivered it, returned a signed destination transport receipt and survived destination restart. All processes ran on one Earth host under one owner. Ledger import and physical signal delay were not exercised.

The signed destination outcome is `EVIDENCE_STORED_NOT_LEDGER_ACCEPTED`. Destination value still requires separately pinned source authority, replay, finality, unique import and maturity. A relay carries bytes without importing or issuing value. Lost replies, route failures and capacity refusal never refund an export.

## Reproduce

Verify `SHA256SUMS`, create a dedicated virtual environment, install the pinned requirement, then:

```sh
python3 -m venv /absolute/private-mesh-venv
/absolute/private-mesh-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
/absolute/private-mesh-venv/bin/python -m unittest discover -s tools -p 'test_interstellar_*.py' -v
/absolute/private-mesh-venv/bin/python tools/interstellar_mesh_drill.py --output /absolute/new-drill-report.json
```

`source.tar.gz` contains the same named supplemental inputs as `source-manifest.json`; both are covered by the checksums. The manifest is a content inventory, not a consensus-source adoption or a signed binary attestation. Private node identities and configs are not included. The daemon stores private transport identity only in its operator-supplied state directory.

Real radio/laser/BPv7 adapters, local broadcast discovery, directional contact scheduling and capacity, anti-eclipse review, long-silence ledger admission, key rotation and rollback resistance, independent operators, and archival/cryptographic survival over stellar or galactic times remain open. Bounded queues are ground admission controls, not evidence of interstellar throughput or million-year operation.
