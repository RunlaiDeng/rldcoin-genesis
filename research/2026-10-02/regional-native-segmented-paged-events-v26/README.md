# Segmented native checkpoints and paged ordinary events — revision 26

This **no-value ground candidate** adds explicitly signed
`RLD-REGIONAL-SEGMENTED-UNANIMOUS-FIXTURE-V1` Admission rules. Four exact ordered
unanimous approvals remain mandatory. Legacy and BFT regions cannot adopt a
segmented base or lower thresholds; local epoch handoff refuses. New native
source requires fresh signed zero-allocation fixtures. Retired/adopted/test
balances and older private stores never migrate.

Each complete checkpoint suffix holds at most 256 native blocks. Its base must
equal the signed previous checkpoint and extend its exact height, parent and
anchor. Only the fully native-executed predecessor under identical trust supplies
state; no sender ledger, decoded cache, digest or signature alone authorizes value.
Every suffix executes ownership, maturity, issuance/conservation, finality,
permanent imports, command/state roots, work and incident checks. Clear only the
in-memory certified window, never durable proof bytes.

## Ordinary paged event storage

`RLD-NATIVE-HISTORY-PAGED-EVENTS-V1` retains complete immutable **16-event pages**
and an unsealed tail. Ordered references, offsets, height ranges and predecessor
hashes bind the exact history. Native open/commit/incident/image verification
streams every page from caller-pinned genesis and executes normal native rules.
Historical wallet/recipient reads propagate failures. Signing-height wallet
review advances a single ordered block cursor. Bad tails never move an anchor or
debit before complete verification. Failed publication preserves journal.next;
old partial tails and all orphans remain retained and counted.

The new profile replaces a single complete event vector with page references.
Legacy/BFT V2 stores retain their original **336-event / 256-block** bounds.
The archive remains **4,096 files / 256 MiB**, including residue. Each object,
metadata journal and full evidence remains **8 MiB**; snapshots remain **64**,
active segments **256 blocks**, and permanent indexes **4,096 entries**. Full
checkpoint evidence remains bounded in memory, and every cold/commit replay
still executes the retained history. This is neither unlimited history nor a
BFT long-history, compact complete remote-proof or 200,000-block-era upgrade.

## Distinct observed value paths

[The ordinary-store test](evidence/regional-native-paged-events-long-store-sample-20261002.json)
persists **1,029 blocks / 1,025 actual-owner signed payments**, wallet review and
inclusion, full cold genesis replay and exact fresh private ledger-image restore.
It retains **64 complete pages / 11 tail events**; all retained history objects
are **83 files / 2,686,657 bytes**.
This is a finite unanimous-profile observation, not arbitrary workload capacity.

[The actual CLI process test](evidence/regional-native-paged-events-frozen-process-sample-20261002.json)
reaches **361 blocks / 353 signed local payments**, newly created post-history
funds export and return **net 98**, idempotent re-delivery, permanent duplicate
import refusal and exact private fresh-target restore. It exceeds the prior
336-event ceiling through paged storage, rather than a larger event vector.

[The new twelve-node BFT cycle](evidence/regional-native-paged-events-fresh-cycle-20261002.json)
uses the original bounded BFT profile: **net 96 / 91 / 86**, fifteen conservation
checks and exact regional heights **7/4/4**. All Earth nodes are stopped during
remote onward/return exports. Controller consensus/proof/checkpoint construction
is zero. It does not inherit or qualify the unanimous profile's long history.

[The 762.388-second fresh finite fault profile](evidence/regional-native-paged-events-fresh-fault-20261002.json)
passes its unchanged offline-validator, contact-cut, restart/catch-up and
recipient import/maturity gates. Net 9 imports at height **12**
and matures at **14**. Separate cold checks authenticate
**1,974 BFT envelopes / 4,371 transport archives**, all twelve native
stores and four original recipient outputs. Cycle and fault image audits restore
**24 private ledger images** exactly with originals and frozen source unchanged.
No image, key, signer/replica, wallet, caller/pending, mesh or TLS state is public
or restored as signing custody. All owned processes stopped.

## Exact source and check scope

[254-file manifest](source-manifest.json), [reviewed source](source.tar.gz):
`699edda9fe44908a11828be2aa52f13e853460a1689a94ce8b023bad079de1e4`. Native implementation:
`21a89b186467cbf7dbb7f9061105b3c8340725ee5d845bdb69831ae0756aae7b`. Frozen documents retain pre-run status;
current reports describe subsequent outcomes. [Checks](checks.json) bind source,
binary and logs. **139 distinct native tests** are covered: **138** ran from
frozen source, and the long-store case ran against byte-identical workspace
native source and was not repeated from the frozen directory. **60 frozen
process tests**, checked release and strict all-target clippy pass. Earlier
**85 transport checks** have exact unchanged source and were **not rerun**.

Missing/corrupt/reordered pages, wrong storage/profile, rehashed invalid value,
invalid full-window anchor tails, interrupted publication and exhausted archive
capacity refuse without adoption, pruning, refund or head advancement. Historical
failed native-source captures, two failed process-test sources and the earlier
253-file segmented candidate are retained. Captures are expressly Native-only,
not full workspace freezes. A height-1,028 test was deliberately stopped during
repeated wallet prefix scans; it never counts as completed signing/recovery.
The later sequential cursor test above is a fresh complete run. Generated failed
stores remain private. Native source/runtime and lifecycle outcomes are distinct.

## Reproduce the observed path

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v26
tar -xzf source.tar.gz -C /absolute/source-v26
cd /absolute/source-v26
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
RLD_STREAM_TEST_BINARY=/absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --lib -- --nocapture
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v26 --manifest /absolute/package-v26/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py --runtime-tools /absolute/source-v26/tools --source-manifest /absolute/package-v26/source-manifest.json --cycle-report /absolute/cycle.json --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/NEW-private-cycle --root /absolute/NEW-private-fault --report /absolute/fault.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py --source /absolute/source-v26 --manifest /absolute/package-v26/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-fault --report /absolute/fault-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v26 --manifest /absolute/package-v26/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v26 --manifest /absolute/package-v26/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v26/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-fault --images /absolute/NEW-private-fault-images --report /absolute/fault-images.json
```

Run stopped audits only after all owned processes stop. Retain every failed source,
report and private fixture. Independent operations/latest-state protection,
power-loss/cross-device signing and wallet custody, BFT reconfiguration, complete
proof/index/history scaling, long-term cryptographic/archival eras and physical
routes remain open. Same-host finite evidence qualifies none of these broad
gates, and **no I1–I12 requirement is fully qualified**. A future mainnet requires
new signed adoption and zero initial issuance; old/test balances never migrate.
