# Generic regional ledger candidate

An incompatible, bounded Rust implementation for white paper 1.10's onward and
return value transitions. It runs three native regional ledger stores, replays
signed owner operations and mined blocks, and uses explicitly installed unanimous
checkpoints. **Public fixture keys, no monetary value, no mainnet mode.**

The existing source/destination nodes and their signed genesis commitments are
unchanged. This supplemental candidate is separately built and started. It is
not a qualified regional consensus protocol or a migration path.

This source revision adds [authenticated finality incidents and dependency quarantine](../../docs/research/REGIONAL_FINALITY_INCIDENTS_V1.md). It creates a new fixture root; the initial source/report package remains historical.

## Reproduce

Rust 1.98 or later is required. From the exact source tree:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
tools/regional-ledger/target/debug/fixture-campaign /absolute/NEW-fixture-directory
```

The campaign starts a separate native CLI process for every operation, using
three on-disk stores. It provides only Earth–Proxima and Proxima–Andromeda
contact transfers. Earth is not invoked while distant local payments and
onward exports execute. Each successful transition and evidence installation
replays all three stores and checks exact conservation. This is a ground
process/restart exercise, not elapsed years, independent owners or real links.

The report contains public currency/source commitments, export IDs, checks and
limitations. Node journals, contact files and other local state are not public
outputs. All signing seeds inside the campaign are deliberately public fixtures:
authority 1; validators 2–5, 22–25 and 42–45; local owners/miner 10–14.

## CLI

Every invocation requires `--dir`, `--authority` and the exact `--currency` root.
A currency root is checked against the caller's trusted authority and the exact
build's implementation commitment. Region names alone cannot authorize a ledger.

- `init --bootstrap FILE --region LABEL`: verify an offline signed package and
  create an empty store in a new absolute directory.
- `status`: independently replay persisted state and return identity, local
  coins, maturity heights, permanent import IDs, export dependencies and finality.
- `mine --miner PUBLIC_KEY [--commands FILE]`: verify signed commands, search for
  real fixture PoW and atomically commit one block.
- `statement`: output the actual local history and checkpoint signing statement.
- `finalize --file FILE`: check four ordered signatures and install the exact
  local checkpoint. Input signatures must be obtained separately.
- `incident --file FILE`: validate and retain an authenticated conflicting
  checkpoint pair without adopting either branch.
- `incidents`: export retained proofs for the next reachable neighbor.
- `recover-incident --file FILE`: restore exactly a guard/index-pinned proof;
  preserve damaged bytes and all quarantines.
- `proof`: output the retained signed checkpoint dependency archive; incident proofs are exported separately.
- `evidence --file FILE`: fully verify and atomically save an archive. This
  installs evidence only; it does not import value or alter local balances.

An authenticated conflict may be retained even while its accompanying value
archive is rejected; no value branch is adopted. At most 16 incident proofs are
retained separately. The persistent guard refuses restart when an observed proof
is missing or capacity prevents retaining it.

A proof archive's order is causal: previous checkpoints and import dependencies
must precede consumers. An incomplete or incompatible contact exchange is
rejected as a whole; the input file is never deleted. A later valid evidence
exchange may be supplied after the missing dependencies arrive.

## Rules and limits

See [the frozen candidate specification](../../docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md).
The fixture campaign issues 300 **runlai units**, not 300 RLD, in three origin
rewards after a zero-allocation genesis. Every other region issues zero.
Split/merge, multiple-owner inputs, explicit change and both local and destination
fees are integer-only. Export inputs require locally finalized creation history;
imported assets require local maturity and finality before onward export. A
return is a new export and import, with a new ID; no timeout or receipt refund
exists. Fees become explicit local outputs and never disappear from accounting.

Per store: 256 blocks, 64 retained snapshots, 4,096 coins/exports/import IDs and
8 MiB journal/evidence; per block 16 commands, per spend 16 inputs/outputs.
Limits reject new work and retain accepted evidence. There is no pruning.

The append-only chain has fixed cheap fixture PoW (one leading zero hash byte),
no timestamps, fork-choice, retargeting or automatic node service. Four public
keys sign a monotonic checkpoint; no BFT view changes, persistent signing agent,
validator reconfiguration or independent custody has been qualified. Authenticated conflicting certificate histories are now durably retained and
freeze local or dependency-scoped new operations. Existing values remain;
repairing a damaged proof never releases quarantines. There is no consensus
conflict resolution or authorized recovery of affected values. There are no
channels, live wallet, native mesh automation, radio/BPv7 adapter, independent
archives, crypto epochs or external backup rollback protection. An old complete
journal can be replayed as old state without an external latest-state anchor.
Fsync/rename and an exclusive OS lock protect local commits, not hostile local
filesystem writers or arbitrary storage hardware. These remaining gates cannot
be replaced by the campaign's successful result.
