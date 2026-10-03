# Native regional ledger candidate: retained finality incidents

This source revision extends the [initial value-return candidate](../regional-native-v1/README.md)
with authenticated conflicting checkpoint histories, durable incident retention,
dependency-scoped quarantine and exact proof-file repair. It uses a **new
incompatible fixture root**, public keys and no monetary value. Existing signed
network code/adoption and old balances are unchanged.

Twenty-six native tests and strict all-target static checks pass. The
[67-process campaign](campaign-report.json) completes three-region value return,
then injects conflicting Proxima certificates. Earth automatically retains the
incident and propagates it through adjacent steps. The 74 returned fixture
runlai are retained and quarantined; Earth-native coins without that dependency
still pay locally. Proxima itself refuses new blocks, Andromeda can still advance,
and damaged proof recovery preserves the same incident and all quarantines.
Conservation is checked throughout. See [verification](verification.json),
[incident rules](INCIDENTS.zh-CN.md) and [ledger rules](SPEC.zh-CN.md).

## Reproduce

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory and use Rust
1.98 or later:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
tools/regional-ledger/target/debug/fixture-campaign /absolute/NEW-fixture-directory
```

The exact base and supplemental source manifests are included. Readable
[candidate sources](tools/regional-ledger/src/lib.rs) are also provided for review;
use the archive for a complete build tree. A fresh same-host archive extraction
has passed all 26 tests and reproduced the exact implementation identity and
campaign report. This is not independent operation or cross-platform acceptance.

## Evidence and remaining gates

An incident authenticates four signers' incompatible header ancestry under one
admission, even at different heights. It does **not** adopt either branch or
assert that both ledgers are valid. Header/body tampering, compatible prefixes,
wrong domains and forged approvals cannot authorize a quarantine. Incident
identity ignores equivalent signature encodings. Accepted state remains intact;
new related spends, imports and exports are refused, with retained exposure shown
separately from balances or actual losses.

A pre-existing persistent guard names each pending incident before retention.
Missing/corrupt/indexed proofs and incident capacity exhaustion refuse restart.
Exact proof recovery preserves damaged bytes and never unfreezes funds. The
bound is 16 incident proofs; archival expansion is still unimplemented. There is
no external monotonic backup root or guarantee for failed storage hardware.

Regional BFT view changes, persistent signing-service locks, epochs, authorized
incident resolution/compensation, channels, automatic native contact submission,
wallet UI, cryptographic horizons, independent archives/operators/review and
physical routes remain open. Explicit fixture unanimity and manual neighboring
proof transfers do not establish those qualifications. All A–G/I1–I12 completion
claims remain unproven. No testnet upgrade, mainnet or asset migration is authorized.

Only source and sanitized reports are published. Native journals, incident-store
files, contact/session state and private identities are excluded. The previous
source and report package remains unchanged for historical reproduction.
