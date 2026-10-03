# Native exact checkpoint-prefix carriage — revision 23

The **no-value ground candidate** now shares repeated history blocks within
native contact and BFT evidence messages. Receivers reconstruct the original
complete Evidence before full native signature/finality/era, owner/value,
permanent import and dependency replay. A prefix, digest or transport receipt
never grants value rights. Changed implementation requires fresh signed fixture
genesis. Old/test balances never migrate; no adopted network is upgraded.

## Wire representation and authority

`RLD-REGIONAL-CONTACT-V2` / `RLD-REGIONAL-BFT-NETWORK-V2` carry exact original
certificate/era metadata and new blocks, with optional earlier in-message
checkpoint statement IDs and prefix lengths. Missing, forward, cross-domain,
overflow and wrong-range references refuse. No disk orphan, peer cache, current
local balance or unchecked serialized state supplies a starting ledger. Expanded
bytes and the complete full logical envelope remain bounded. Exact repeats and
authenticated equivalent BFT certificates still follow normal native rules.

Full native Evidence/Journal serialization and signatures are unchanged. BFT
proposal/finality bodies remain complete snapshots, and vote/timeout bodies stay
unchanged. `bft-network-pack` verifies the full typed logical V2 envelope before
printing wire evidence; incoming/cold `bft-network-check` reconstructs and fully
authenticates, returning full checked evidence for Python's native sync. Durable
submission packing is native and typed; merely queueing never debits or signs.
Retained wire envelopes remain exact canonical bytes. Python does not reconstruct
or authorize prefixes. V1 payloads refuse without fallback or value migration.

Physical payload **3 MiB**, native logical **8 MiB / 256 blocks / 64 snapshots**,
permanent indexes and all disk/archive bounds remain unchanged. More admissible
logical proofs may fit the same physical budget. This is prefix carriage, not
compact Merkle/state witnesses, full history-memory/index scaling, 200,000-block
eras, long-horizon cryptography or independent/physical qualification.

## Exact frozen source, tests and measured cost

The [244-file manifest](source-manifest.json), [complete source](source.tar.gz)
and copied tools commit `b49b62072387b63720c64edc324788884ca117c45147166f69f2a9583ca692f0`; native implementation is
`e213d670da01c99ea34706a15b1f241d3bf5bbd137ca95d107f5a9b5841d6918`. Frozen documents retain pre-run status; later
reports define outcomes. Checked release rebuilding, **122 native / 57 real
process / 85 rerun transport tests** and strict all-target clippy pass.
[Checks](checks.json) bind source, binary and logs. Six new native checks cover
exact cold expansion, missing/forward/domain/range refusal, authentic repeats
and forged proofs, expansion overflow from a physically admissible message,
real owner export/import/spent-output replay, and BFT cold catch-up/forgery refusal.

[64-checkpoint evidence](evidence/regional-native-carriage-final-evidence-sample-20261002.json)
falls from **1,401,071** to **135,406**
bytes (**90.34%**), with all expanded bytes and cold native ledger fields exact.
[The twelve-checkpoint BFT envelope](evidence/regional-native-carriage-final-bft-sample-20261002.json)
falls from **139,693** to **103,171**
(**26.14%**). Signed BFT bodies remain full; these exact samples do not claim
the same reduction for every network, archive, signature or total storage cost.

## Fresh signed lifecycle and stopped recovery

[The new twelve-node cycle](evidence/regional-native-carriage-final-fresh-cycle-20261002.json)
delivers net **96 / 91 / 86**, passes fifteen conservation checks and agrees at
four-replica heights **7 / 4 / 4**. All Earth nodes stay stopped during remote
onward/return exports; controller vote/proof/checkpoint construction is zero.
[Separate cycle cold checks](evidence/regional-native-carriage-final-cycle-cold-20261002.json)
fully authenticate native states, original outputs, retained BFT and transport
archives without modifying private originals.

[The new finite fault profile](evidence/regional-native-carriage-final-fresh-fault-20261002.json)
passes in **560.168 seconds**, exits normally and stops every owned process.
Original net 9 imports uniquely at height **10** and
matures at **12**. Original cycle files stay unchanged;
no bound increase, pruning, timeout refund or reuse of older candidate value
obtains this pass. [Separate fault cold checks](evidence/regional-native-carriage-final-fault-cold-20261002.json)
replay twelve stores and four original outputs and fully authenticate
**1,674 BFT envelopes / 3,827 transport archives**, with originals unchanged.

[Cycle](evidence/regional-native-carriage-final-cycle-fresh-target-audit-20261002.json)
and [fault](evidence/regional-native-carriage-final-fault-fresh-target-audit-20261002.json)
image audits restore **24 private ledger images** to fresh targets with exact
heads, full state/value, permanent imports, incidents and every retained byte.
Images exclude keys, signer/replica, wallet, caller/pending, mesh/TLS and transport
custody. Originals and frozen source remain unchanged. No generated image/state
is public. Same-host/controller recovery is not independent latest anchoring,
power-loss, copied-key or signer/wallet custody qualification.

## Retained earlier failures

[The first complete 244-file freeze](historical/initial-source.tar.gz) and
[manifest](historical/initial-source-manifest.json) pass all 122 native tests,
but [strict clippy](historical/initial-frozen-clippy.log) rejects an explicit
counter in the expansion-bound test. The final height-range expression keeps
the same test and strict checks. No cycle/fault pass belongs to that first freeze.
[The report](historical/initial-frozen-failure.json) records its exact scope.

[Initial focused records](historical/initial-focused-checks.json) preserve an
8-pass/1-fail contact run whose alias test encoded the obsolete logical payload,
and a 121-pass/1-fail native run whose BFT cost assertion assumed an unmeasured
50% reduction. The corrected alias uses actual wire bytes; the BFT check measures
actual savings, exact prefixes and native semantics. Associated logs and two
native-source-only archives remain here. They are **not complete workspace
freezes**, and no preservation of every failed unit's private state is claimed.

## Reproduce the observed path



Verify SHA256SUMS, extract the named source to a fresh directory, use Rust 1.98.0
and a private Python virtual environment. Keep every generated directory private.
Never resolve the virtual environment's executable symlink into the base Python.

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_interstellar_mesh test_interstellar_tcp test_interstellar_transfer test_interstellar_route_budget
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v23 --manifest /absolute/package-v23/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v23 --manifest /absolute/package-v23/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images-audit.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py --runtime-tools /absolute/source-v23/tools --source-manifest /absolute/package-v23/source-manifest.json --cycle-report /absolute/cycle.json --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/NEW-private-cycle --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py --source /absolute/source-v23 --manifest /absolute/package-v23/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v23 --manifest /absolute/package-v23/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v23/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --images /absolute/NEW-private-fault-images --report /absolute/fault-images-audit.json
```



Run stopped audits only after every owned node stops. Keep generated fixture,
signer, wallet and archive state private; retain actual failures and exact sources.
Revision-22 and older results remain separate historical evidence. Source and
wire changes never inherit another candidate's qualification. See [status](STATUS.zh-CN.md),
[history requirements](HISTORY_RETENTION.md) and [acceptance queue](ACCEPTANCE_QUEUE.md).
Long-history/state/index scaling, independent latest anchors/archives, full BFT
reconfiguration, cryptographic horizons, cross-device custody, independent review
and causal physical routes remain open. No I1–I12 gate is fully qualified.
