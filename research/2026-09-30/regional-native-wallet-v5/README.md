# Native regional candidate: reviewed wallet signing and recipient verification

This revision adds a native wallet command layer to the default-relay candidate.
`wallet-view` reports current spendable, immature, quarantined and onward-eligible
amounts. `wallet-prepare` selects owned eligible inputs and exposes the exact
recipients, regional domains, fees and change for review. `wallet-sign` requires a
separately retained review commitment, replays/locks current state and incidents,
then verifies its signed command through actual ledger execution. Stale reviews,
changed intents and wrong or unsafe key files are rejected. Signing does not mine.

`wallet-receipt` independently checks currency, source/destination, export ID,
recipient and net amount against verified source evidence and local import
history. Pending evidence, immature import, original output spendability, original
output already spent and quarantine are separate states. Spending a received
output retains its import tombstone; current change/payment outputs are verified
through the wallet view. A transport receipt cannot credit a wallet. Local
spendability never waits for Earth or a returned receipt; onward export needs
local finality as well.

All 51 native tests (including eight wallet tests), strict all-target static
checks, eight relay integration tests and two wallet process tests pass. Wallet
process tests execute real signed local and remote debit, authenticated import,
maturity, local recipient payment, current-balance replay and rejection cases.
The unchanged transport files retain the earlier 35-check verification.
The [three-ledger campaign](campaign-report.json) still demonstrates default
relay, offline onward payment, a new cyclic return and 31 conservation checks.
All keys and amounts are public fixtures with no monetary value; this is a new
incompatible currency root, not an adopted-testnet upgrade or mainnet.

## Reproduce

Verify `SHA256SUMS`, extract `source.tar.gz` into a fresh directory and use Rust
1.98 or later and Python with the pinned dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
python3 -m unittest discover -s tools -p 'test_regional_*.py'
python3 -m unittest discover -s tools -p 'test_interstellar_*.py'
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-contact-fixture --report /absolute/NEW-report.json
```

See the [wallet request/review and startup guide](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).
Source/runtime files must remain available at the build checkout. Starting a
verified fixture node normally enables the same bounded relay lifecycle without
implicit mining; explicit adjacent contacts are still required.

The complete archive names 205 files; all 167 earlier base-source hashes and
commitment remain unchanged. Candidate Rust and Python/test file hashes are
recorded separately. A fresh same-host named-source build passed 51 native tests,
10 integration tests and reproduced all semantic campaign fields. Only native
busy-retry/helper invocation counters may vary with scheduling. Readable
supplemental sources are also included. This is not independent qualification.

## Remaining mandatory work

The current wallet command layer handles one signing owner and does not persist
pending signed-intent reservations. Complete wallet UI, pending-input accounting,
multi-owner signing, cross-device recovery and external rollback protection remain
open. Current local view pins are not independent monotonic anchors. Relay still
uses directory contact fixtures; real adapters, BFT/view changes, channels,
long-term storage/cryptography, independent operations/custody/review and exact
signed-release qualification remain required. Starting a node confers no reward,
issuance or finality right. No private identities, key files, wallet/session or
contact configuration, or node journals are published. Prior packages are unchanged.
