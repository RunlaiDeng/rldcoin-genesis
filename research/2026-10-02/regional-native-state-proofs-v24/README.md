# Native certified state-record proofs — revision 24

The **no-value ground candidate** commits native block/checkpoint state to
ordered coin, export and permanent-import trees plus minted/received counters.
Historical record proofs bind the caller's exact native-replayed checkpoint,
collection and key. They never authorize spending, import, signing, freshness,
refund or deletion of permanent import records. Changed native state roots need
fresh signed fixture genesis/currency. Old/test balances never migrate; no
adopted network is upgraded.

## Exact native authority and proof rules

`RLD-REGIONAL-STATE-COMMITMENT-V1` binds exact typed keys/records and counts,
with separate domains for leaves, level-bound branches, odd-node padding and
empty roots. Membership checks exact position and path length. Nonmembership
requires authenticated adjacent neighbors or exact first/last endpoints.
Missing, reordered, wrong-position, cross-collection, altered-record, oversized
and nonadjacent witnesses refuse. Counters are committed; hashing them alone
never proves conservation or issuance.

`state-proof --checkpoint ID --collection coins|exports|imports --key HASH`
generates the bounded proof. `state-proof-check` additionally takes `--file`;
the requested checkpoint and query come from the caller, never from the proof.
The certificate must already exist in fully native-verified Evidence. Native
startup still completely replays currency/admission, signatures/finality/eras,
owner/value execution, maturity, imports and incidents. Current incident checks
remain separate. A proof that a coin existed historically does not make it
currently spendable; checking performs no ledger or custody mutation.

Full logical **8 MiB / 256 blocks / 64 snapshots**, permanent **4,096-entry**
indexes, physical **3 MiB** carriage and all storage/archive bounds remain.
Proofs are bounded to **64 KiB**. Generation currently rebuilds bounded maps;
full signed Evidence/history remains necessary. This is not incremental durable
indexing, compact complete remote value authorization, beyond-era execution or
independent/physical qualification.

## Frozen source, tests and measured proof cost

[The 247-file manifest](source-manifest.json) and [complete source](source.tar.gz)
commit `f0586e230a2f6f3b3cd13187d214c9c3a0c9acc5aa396ce2036e8ad7e51472ab`; native implementation is
`df0a2c8f1faf93273a9be0212021575879a1f01cc39b0c614ae1031600b4281f`. Frozen documents retain pre-run status;
later exact reports define outcomes. Checked release rebuild, **128 native /
59 real process tests** and strict all-target clippy pass. Six new native tests
cover empty/single/odd/even maps, exact membership/absence, all roots/counters,
query/domain/record/position/path/padding/size/count refusal, synthetic capacity
and actual signed export/spent-import cold replay. Two new real-CLI tests check
nonmutating refusals and full fresh-target private recovery of spent-original
absence and permanent-import membership. Ordinary duplicate import still refuses.

[The bounded sample](evidence/regional-native-state-proof-final-capacity-sample-20261002.json)
uses **4,096 synthetic records**: an absence proof is
**2,683 bytes / 24 sibling hashes**,
against **860,228 bytes** of complete synthetic state. This
measures map shape, not actual issuance, long-history execution or every proof's
cost. Transport's **85 prior rerun tests** come from byte-identical revision-23
transport source; they were **not rerun here**. [Checks](checks.json) bind the
exact prior transport report and all current source, binary and logs.

## Fresh signed lifecycle and private recovery

[The new twelve-node cycle](evidence/regional-native-state-proof-final-fresh-cycle-20261002.json)
delivers net **96 / 91 / 86**, passes fifteen conservation checks and agrees at
four-replica heights **7 / 4 / 4**. All Earth nodes stay stopped during remote
onward/return exports; controller vote/proof/checkpoint construction is zero.
[Separate cycle cold checks](evidence/regional-native-state-proof-final-cycle-cold-20261002.json)
fully authenticate native states, original outputs, retained control and transport
archives without changing private originals.

[The fresh finite fault profile](evidence/regional-native-state-proof-final-fresh-fault-20261002.json)
passes in **539.07 seconds**, exits normally and stops every owned process.
Original net 9 imports once at height **11**, maturing
at **13**. Original cycle files stay unchanged; no bound
increase, pruning, timeout refund or older candidate value obtains this pass.
[Separate fault cold checks](evidence/regional-native-state-proof-final-fault-cold-20261002.json)
replay twelve stores/four original outputs and fully authenticate **1,699
BFT envelopes / 3,861 transport archives**, with originals unchanged.

[Cycle](evidence/regional-native-state-proof-final-cycle-fresh-target-audit-20261002.json)
and [fault](evidence/regional-native-state-proof-final-fault-fresh-target-audit-20261002.json)
audits restore **24 private ledger images** to fresh targets with exact heads,
full state/value, imports, incidents and every retained byte. Images exclude
keys, signer/replica, wallet, caller/pending, mesh/TLS and transport custody.
No generated image/state is public. Originals and frozen source remain unchanged.
Same-host finite recovery is not independent latest anchoring, power-loss,
copied-key or signer/wallet custody qualification.

## Retained initial strict-check failure

[The initial native-source-only capture](historical/initial-native-files.tar.gz)
and [report](historical/initial-checks.json) bind 128 passing native tests and
strict clippy's refusal of a large enum variant and a manual divisibility test.
Members now use indirection and the native divisibility predicate, retaining
the exact serialized proof rules and all strict checks. This capture is **not
a complete workspace freeze**; no process/cycle/fault result belongs to it.
Initial logs remain retained. Revision-23 and earlier source/results stay separate;
this changed source never inherits their native lifecycle qualification.

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
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_interstellar_mesh test_interstellar_tcp test_interstellar_transfer test_interstellar_route_budget
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v24 --manifest /absolute/package-v24/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v24 --manifest /absolute/package-v24/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images-audit.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py --runtime-tools /absolute/source-v24/tools --source-manifest /absolute/package-v24/source-manifest.json --cycle-report /absolute/cycle.json --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/NEW-private-cycle --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py --source /absolute/source-v24 --manifest /absolute/package-v24/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v24 --manifest /absolute/package-v24/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v24/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --images /absolute/NEW-private-fault-images --report /absolute/fault-images-audit.json
```




Run stopped audits only after every owned node stops. Keep all generated fixture,
keys, signer, wallet, caller and image state private; retain exact failures and
source commitments. See [status](STATUS.zh-CN.md), [history obligations](HISTORY_RETENTION.md)
and [acceptance queue](ACCEPTANCE_QUEUE.md). Incremental permanent indexes, bounded
active long-history execution, compact complete remote authority, independent
anchors/archives, BFT reconfiguration, cryptographic horizons, cross-device custody,
independent review and causal physical routes remain open. No I1–I12 gate is
fully qualified.
