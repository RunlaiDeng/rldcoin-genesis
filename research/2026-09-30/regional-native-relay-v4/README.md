# Native regional candidate: default relay and automatic evidence application

Normal fixture-node startup now enables authenticated discovery and bounded
durable relay within the same lifecycle. A separate relay launch is unnecessary.
An isolated node waits for contacts; relay service requires no miner key and earns
no automatic reward. Explicit `--miner PUBLIC_KEY` additionally enables local
import block production after Rust validates the carried evidence. Transport
receipts never grant credit. This is a new incompatible, public-key fixture
currency with no monetary value, not an adopted-testnet upgrade or mainnet.

All 43 Rust tests, 35 transport tests, eight actual-process integration tests and
strict all-target static checks pass. Incremental neighbor addition extends a
tested four-node topology; another branch delivers after the preferred relay
stops. Restart recovers identity/queues, full storage preserves prior evidence,
and relay-only startup does not mine. The [three-ledger campaign](campaign-report.json)
uses seven normal node starts, 269 native calls including busy retries and 31
conservation checks. Remote local payment and onward export proceed without Earth
calls; the new cyclic return imports once, while the original debit stays spent.
Foreign-currency evidence can receive a storage receipt yet is rejected for credit.

## Reproduce

Verify `SHA256SUMS`, extract `source.tar.gz` into a fresh directory and use Rust
1.98 or later plus Python with the pinned transport dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
python3 -m unittest discover -s tools -p 'test_interstellar_*.py'
python3 -m unittest discover -s tools -p 'test_regional_contact_node.py'
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-contact-fixture --report /absolute/NEW-report.json
```

After initializing a verified fixture ledger, ordinary startup is:

```sh
/absolute/rld-regional-ledger-candidate --dir /absolute/ledger --authority AUTHORITY_HEX --currency CURRENCY_HEX
```

Use `--transport-python /absolute/python` when necessary. Source/runtime files
must remain available at the build checkout. Adjacent contacts require explicit
authenticated configuration; distant routes are learned. See [startup and CLI](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[mesh requirements](docs/research/INTERSTELLAR_NODE_MESH_REQUIREMENTS.md) and
[current status](PLAN_STATUS.zh-CN.md).

The archive names 202 exact files. All 167 base files retain the earlier published
source hashes/commitment; the new candidate Rust commitment and Python runtime
hashes are separately recorded. A fresh same-host source build passed 43 Rust
tests and eight integration tests, then reproduced every semantic campaign
field. Scheduling changed only the two invocation counters (241 native calls and
eight helper calls in that run); [verification](verification.json) identifies them.
This is not independent or cross-platform qualification. Readable supplemental
sources are included; the archive supplies the complete core build tree.

## Limits and remaining gates

The Rust launcher runs the Python signed contact-spool companion. Directory
contacts are ground fixtures, not real stellar adapters, local radio discovery
or physical availability. Resource and adversarial contact qualification, recipient
wallets, channels, BFT/view changes, independent custody, external anti-rollback
anchors, long-term archives/cryptography and exact adopted-release qualification
remain mandatory. Default relay budgets are 16 contacts, 64 discovered identities,
256 retained messages/receipts, 64 MiB transport state and 16 hops; work/refusal
does not promise eventual delivery or consensus security from node count.
No node state, private transport identities, wallet/session files or contact
configuration is published. Previous signed/source packages remain unchanged.
