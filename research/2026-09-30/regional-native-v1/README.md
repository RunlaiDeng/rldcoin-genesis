# Generic native regional ledger fixture candidate V1

A separately built Rust candidate for white paper 1.10's offline regional value,
onward exports and new cyclic return imports. It uses a new incompatible fixture
currency root, public deterministic signing keys, and **no monetary value**.
It does not modify, upgrade or adopt the published testnet or retired mainnet.

The native campaign executes three on-disk regional ledgers through 52 separate
CLI process invocations. Multiple owners split/merge exact integer amounts, pay
local/destination fees, import from two regions, export onward, and return a new
export to Earth. Earth has no active process during distant local operations.
Only adjacent evidence transfers are provided. Every mutation and evidence
installation is replayed and checked for conservation. Fifteen native tests and
strict all-target static checks pass. See [the campaign](campaign-report.json),
[verification](verification.json), and [frozen candidate rules](SPEC.zh-CN.md).

## Rebuild

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory, then:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
tools/regional-ledger/target/debug/fixture-campaign /absolute/NEW-fixture-directory
```

Rust 1.98 or later is required. The archive contains the exact 167-file base
source manifest plus the candidate and its dependency lock. The candidate's
currency signature binds its exact implementation identity, which incorporates
the base and supplemental sources. `base-source-manifest.json` and
`supplemental-source-manifest.json` describe those sets. Named source commitments
are reproducibility inputs, not adoption certificates or compiler attestations.
The archive has been independently extracted and rebuilt on the same macOS host;
its campaign and implementation identity match the original local build. This
is not a second independent operator or cross-platform qualification.

## Remaining mandatory work

The chain is append-only with cheap actual fixture work and explicit unanimous
checkpoints. It has no fork selection, regional BFT view changes, persistent
signing service, epoch/revocation protocol or independent key custody. Valid
conflicting certificates are refused; permanent incident preservation, dependency
quarantine and exposure recovery remain unimplemented. There are no channels,
wallet signing UI, automatic native mesh or physical contact adapter. Journals
are bounded, atomically replaced and fully replayed, but have no independent
archives or external old-backup rollback root. Long-term cryptographic horizons
and physical aging are unqualified. Public fixture keys do not protect funds.

The full A–G/I1–I12 contract remains incomplete. This package is source and
sanitized ground reports only; node journals, contact/session files and private
identities are excluded. No route, mainnet or balance migration is authorized.
