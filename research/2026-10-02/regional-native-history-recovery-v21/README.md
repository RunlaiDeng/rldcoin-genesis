# Private native ledger images and fresh-target recovery — revision 21

`history-archive` / `history-restore` implement bounded, private native ledger
images. They retain complete paged history, authenticated incident proofs and
unaccepted residue. Sealing and fresh-target recovery check a separately retained
exact latest storage head and fully replay native currency, finality, owner/value,
permanent imports and incidents. Image digests never grant native authority.

This incompatible **no-value ground candidate** needs fresh signed fixture
genesis. Old/test balances never migrate; no adopted or retired network upgrades.
It restores ledger evidence only. Keys, signers/BFT replicas, wallet journals,
caller heads/pending reviews, mesh/TLS configs and transport archives are excluded.
Generated images and fixture state are private and are **not in this package**.

## Exact image, durability and interruption boundary

`RLD-NATIVE-HISTORY-ARCHIVE-V1` binds currency, region, native head, exact named
file inventory, retained byte counts and file digests. Fixed native file names
are inventoried before copy; index paths never drive arbitrary traversal.
Canonical indexes, ownership, file/link types, permissions and bounds are checked.
Archived/restored files use 0600 and directories 0700, with file/directory fsync.
All history objects, including old tails and unaccepted orphan bytes, are copied;
no pruning, evidence repair, debit release or timeout refund is introduced.

Sealing holds the native OS lock. Restore locks the complete image, validates it
before target creation, then checks copied inventory and full native replay again.
Existing targets refuse without overwrite or merge. ARCHIVING prevents use of an
incomplete image; RESTORING prevents ordinary native startup, wallet/contact entry
and explicit incident recovery from using an interrupted target. Retain that
failed target; use a different fresh path. Source journal.next residue refuses
sealing unchanged. No resume or restored signing/caller custody is claimed.

History stays bounded at **4096 files / 256 MiB**. Each authenticated-incident
and damaged-residue set has at most 16 files, each at most 8 MiB. The manifest,
guard and both sets give a combined retained-native-payload ceiling of **4130
files / 520 MiB + 32 bytes**. The separate canonical archive index is also bounded
at 8 MiB; empty lock files and directory metadata are not native payload. Native logical **8 MiB / 256 blocks / 64 snapshots** still refuse.
These are ground capacity limits, not stellar archives or 200,000-block execution.

## Exact source and checks

The [241-file manifest](source-manifest.json), [archive](source.tar.gz) and copied
runtime tools commit `4af70053f541a67f967bbcfca3d647c46af663343c34e76d7c2e5d63cee6d258`.
Native implementation is `d713c6afc275d743b50059250815617b4a88bc97eef201c4d6ee18ab9cf80e6d`.
Frozen documentation retains pre-run status; later reports define outcomes.
Checked release rebuilding, **109 native tests**, strict all-target clippy and
**57 actual process/controller/storage/history tests** pass. Earlier **84
transport tests** use exact unchanged source/test bytes and were **not rerun**.
[checks.json](checks.json) identifies log commitments and separate lifecycle gates.

Ten new native tests cover real owner payment/finality, multiple event pages,
full import/incident quarantine recovery, missing and altered inventory, forged
self-consistently rehashed finality, stale head/cross-domain refusal, unsafe
links/permissions, OS locks, existing targets, source residue and interrupted
copy refusal. Five actual CLI tests cover exact fresh-target state, private
custody exclusions, old heads/domains, spent original-import identity and an
actual restore process killed after observing RESTORING. Every subsequent entry
refuses unchanged; source/image stay unchanged. A SIGKILL is a process observation,
**not power-loss or storage fault injection**.

The [initial check report](evidence/regional-native-history-image-initial-checks-20261002.json)
and [failure log](historical/initial-focused-test-failure.log) preserve an initial
9-pass/1-fail run. Native rejected a short forged signature with `expected 64
bytes`; the test incorrectly expected different text. The corrected test uses a
full-length invalid signature and exercises native cryptographic rejection.
[Six captured changed native files](historical/initial-changed-native-files.tar.gz)
are not represented as a complete initial frozen package. That failed unit
fixture was cleaned by the initial test helper; only its source/log are retained.

## New cycle, finite fault profile and fresh-target recovery

The [new twelve-node cycle](evidence/regional-native-history-image-fresh-cycle-20261002.json)
delivered net **96 / 91 / 86**, passed all fifteen `issued = liquid + pending
exports` checks and agreed at four-replica heights **7 / 4 / 4**. All Earth nodes
stayed stopped during remote onward/return exports. Controller vote generation,
value proof carriage and checkpoint installation were zero.
[Separate cycle cold checks](evidence/regional-native-history-image-cycle-cold-20261002.json)
replayed twelve stores and original outputs and authenticated **607 BFT
envelopes / 1,392 transport archives**, with private files unchanged.

The [new full finite fault profile](evidence/regional-native-history-image-fresh-fault-20261002.json)
passed in **583.24 seconds**, exited normally and stopped every owned node.
Original output **9** imported at height **11** and
matured at **13**. No observation bound was increased,
source debit stayed retained and the sealed cycle fixture stayed unchanged.
[Separate fault cold checks](evidence/regional-native-history-image-fault-cold-20261002.json)
replayed twelve stores and four original outputs and fully authenticated
**1,688 BFT envelopes / 3,844 transport archives** without private writes.

[Cycle fresh-target audit](evidence/regional-native-history-image-cycle-fresh-target-audit-20261002.json)
and [fault fresh-target audit](evidence/regional-native-history-image-fault-fresh-target-audit-20261002.json)
each sealed twelve stopped native stores and restored all twelve into fresh
private directories. **24 complete native images/restores** match exact history
heads, native state/value, permanent imports and incidents. Archive inventories
match every restored retained byte; original fixture files and frozen source are
unchanged. Separate observation files stay outside each image. This is same-host,
same-controller recovery; it establishes no independent latest-state protection
or signer, wallet or copied-key custody. No private image has been published.

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
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v21 --manifest /absolute/package-v21/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v21 --manifest /absolute/package-v21/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images-audit.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py --runtime-tools /absolute/source-v21/tools --source-manifest /absolute/package-v21/source-manifest.json --cycle-report /absolute/cycle.json --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/NEW-private-cycle --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py --source /absolute/source-v21 --manifest /absolute/package-v21/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v21 --manifest /absolute/package-v21/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v21/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --images /absolute/NEW-private-fault-images --report /absolute/fault-images-audit.json
```

Run stopped audits only after all owned nodes stop and the cycle/full-profile
verifier passes. Retain actual failures, their exact source and private state;
never reuse prior candidate value, raise bounds or prune evidence to obtain a pass.
Standalone history-archive/history-restore CLI commands and exact scope appear in
the frozen native README. Prior [revision-20 paging/fault evidence](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-paged-history-v20)
is retained, including earlier real failures; it does not certify this new source.

Long-history execution, compact remote dependency proofs, permanent-index scaling,
200,000-block issuance eras, independent latest anchors/archives, power-loss,
cross-device signing/wallet custody and complete BFT reconfiguration remain open.
So do channels, full wallets, cryptographic horizons, independent operation/review
and actual causal physical contacts. No I1–I12 requirement is fully qualified.
See [status](STATUS.zh-CN.md), [history obligations](HISTORY_RETENTION.md) and
[acceptance queue](ACCEPTANCE_QUEUE.md).
