# Exact incremental native state-index computation — revision 27

This no-value candidate reduces repeated state-root and record-proof hashing
while preserving the exact V1 ordered commitment and proof encoding. Complete
native owner/value/finality/incident replay, conservation, permanent imports
and all admission bounds remain mandatory. A cached digest never initializes
value or authorizes a payment. New native source requires a fresh signed
zero-allocation fixture genesis; old/adopted/test currency never migrates.

One private process-local witness compares every current typed record. Reuse
requires exact collection/key/value leaves and exact collection/level/ordered
child pairs. Current counts and audited counters are recomputed. No witness is
serialized. Retention accounting includes canonical values, fixed entry overhead
and hashes, refuses above 8 MiB and falls back to complete original hashing
without pruning or new acceptance. A poisoned lock clears the witness before
reconstruction. This accounting is not measured peak RSS: current ledger and
transient construction are separate allocations. Ordered inserts/deletes can
shift every position and still require linear work.

## Exact source and observed results

[256-file manifest](source-manifest.json), [source](source.tar.gz):
`f3ddc138e5ea97ce57b9eacd20614bcfdca9200901f7401b4609a7dde48ecb7f`. Native implementation:
`87f7bfdf37f12b4bc734f87c7ca55717ccfcb1f4cf868177ad5be8e20a8143ed`.

[Checks](checks.json): checked release, strict all-target checking, **145 native
and 60 process tests**. All 145, including the ordinary long-store case, run from
frozen source; the real native CLI archive subcheck is enabled. No earlier source
qualification is inherited. Frozen documents retain pre-run status; these bound
reports describe later outcomes.

- [Synthetic 4,096-entry cost](evidence/regional-native-incremental-index-final-frozen-cost-20261002.json): 4,096 new leaf hashes / 4,095 branches cold; zero new leaf/branch hashes for an exact unchanged state; one leaf / twelve branches after one existing record changes. Independent complete reconstruction agrees. Retained accounting is 1,998,816 bytes. This measures hashing work, not issuance, elapsed speedup, arbitrary insertion/deletion or long-history capacity.
- [Ordinary storage](evidence/regional-native-incremental-index-final-frozen-long-store-20261002.json): 1,029 blocks / 1,025 actual-owner signed payments, native wallet review/inclusion, genesis cold replay and exact private fresh-target ledger restoration. Retained 64 sealed 16-event pages, eleven tail events and 83 files / 2,686,684 bytes.
- [Actual process](evidence/regional-native-incremental-index-final-frozen-process-sample-20261002.json): 361 blocks / 353 signed local payments, cross-region return net 98, idempotent delivery, permanent duplicate-import refusal and exact private restoration. These segmented unanimous observations do not upgrade bounded BFT history.
- [New twelve-node cycle](evidence/regional-native-incremental-index-fresh-cycle-20261002.json): original four-validator/three-vote BFT profile, net 96/91/86 and fifteen conservation checks. All Earth nodes stop during onward/return exports; controller consensus/proof/checkpoint construction is zero. Separate stopped cold checks authenticate twelve stores and twelve original recipient observations; twelve private ledger images restore exactly to fresh targets. Originals and frozen source are unchanged. Same host/controller, no independent operations.

No generated image, key, signer/replica, wallet, caller/pending, mesh or TLS state
is public or restored as signing custody. **No fresh full fault profile runs for
revision 27**; [revision 26 fault results](../regional-native-segmented-paged-events-v26)
remain bound to their own source and are not inherited. No transport-test rerun
or physical-link qualification is claimed.

## Historical observations

The historical directory retains the initial complete 256-file reviewed source,
its corrected manifest and the separately retained incorrect manifest that
confused the native-source digest with combined native/core implementation
identity. Validation refused before remaining checks. Metadata correction was
followed by passing initial checked release/strict checking; test compilation
was intentionally stopped to correct fallback-work accounting. Final accounting
includes discarded preparation and full fallback hashing. The final build
completed across a turn interruption; its terminal log and exact binary identity
were checked before remaining checks resumed. Neither interruption counts as a
completed regression. Sanitized build/check/test logs and their exact local
and published hashes are retained in the log inventory. Workspace prefixes are
redacted; no generated private state is included.

## Reproduce

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v27
tar -xzf source.tar.gz -C /absolute/source-v27
cd /absolute/source-v27
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
RLD_STREAM_TEST_BINARY=/absolute/source-v27/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --lib -- --nocapture
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v27/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v27/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v27 --manifest /absolute/package-v27/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v27/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v27 --manifest /absolute/package-v27/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v27/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-images --report /absolute/images.json
```

Stop owned nodes before cold/image audits. Preserve every failed source/report
and private fixture. Persistent incremental indexes, compact complete remote
authority, BFT and beyond-200,000-block-era history, independent latest-state
protection/archives, power loss/cross-device custody, cryptographic evolution
and physical routes remain open. No I1–I12 gate is fully qualified. A future
mainnet needs separately qualified signed zero issuance.
