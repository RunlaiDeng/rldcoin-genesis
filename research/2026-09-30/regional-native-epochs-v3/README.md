# Native regional candidate: durable signer locks and joint validator epochs

This revision extends [incident retention](../regional-native-conflict-v2/README.md)
with separately locked signing agents and unanimous validator handoffs. It uses a
**new incompatible fixture currency, public keys and no monetary value**. Existing
signed network adoption and balances are unchanged; no testnet deployment or
mainnet is authorized.

All 35 native tests and strict all-target static checks pass. The
[128-process campaign](campaign-report.json) uses persistent native signers for
all normal checkpoints. Earth rotates from its initial four keys to four new keys
with all old and new approvals. The closing fence remains valid offline, the
currency and value state stay unchanged, and post-handoff exports are verified
through adjacent regions. Three-region local payments, onward value and a new
cyclic return remain conserved. Authenticated Proxima faults still preserve and
quarantine 74 returned fixture runlai; unrelated local assets pay, and exact
incident repair never unfreezes them. See [verification](verification.json),
[signer/epoch rules](SIGNER-EPOCHS.zh-CN.md), [incident rules](INCIDENTS.zh-CN.md)
and [ledger rules](SPEC.zh-CN.md).

## Reproduce

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory and use Rust
1.98 or later:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
tools/regional-ledger/target/debug/fixture-campaign /absolute/NEW-fixture-directory
```

The archive contains 185 exact named files, with base, supplemental and complete
archive manifests. A fresh same-host extraction rebuilt all compiled inputs,
passed 35 tests and reproduced the campaign report byte for byte. Final archive
file hashes and unchanged compiled inputs were checked after a documentation-only
revision reference correction. Readable [candidate sources](tools/regional-ledger/src/lib.rs)
are provided; the archive is the complete build tree. Publication copies adapt
some document links. This is not independent or cross-platform acceptance.

## Limits and remaining gates

Each signature is durably journaled before release. Increasing prefix and
checkpoint-predecessor locks survive restart. Joint handoff consent seals the old
era before activation; new members must consent before signing. Missing any old
or new approval pauses the handoff. Overlapping membership and a second era are
also tested. Incompatible joint handoffs and old-era certificates after the
joint closing fence become authenticated retained incidents, even when block
prefixes agree. Source closing ledgers must be replayed before adopting new eras.

Every signing call requires the caller's separately retained latest journal head.
A surviving newer head rejects a restored stale signer directory; restoring all
state/pins together or bypassing the agents with copied keys defeats this check.
The campaign's pin is outside signer directories but under the same owner on the
same host. This does not qualify an independent monotonic service. Ledger backups
still need an external latest-state anchor. Key files, signer journals, ledger
state and contact/session files are excluded from public outputs.

The candidate remains append-only PoW plus four-key unanimity, with no BFT view
changes, missing-signer liveness, qualified fork choice or independently qualified
reconfiguration. Key rotation is not cryptographic algorithm migration or incident
resolution. Native contact automation, wallet UI, channels, authorized recovery,
long-term archive/crypto qualification, independent operators/custody/review and
physical routes remain open. Bounds are 16 handoffs, 128 signing records, 16
incidents, 256 blocks per region and 8 MiB journals. All I1-I12 completion claims
remain unproven; see the [current plan status](PLAN_STATUS.zh-CN.md).

Historical v1 and v2 source/report packages remain unchanged.
