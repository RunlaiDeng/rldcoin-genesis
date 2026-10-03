# Native paged disk history — revision 20

The default native store now keeps complete canonical snapshot, epoch and contact
objects in an immutable archive and orders local events in sixteen-event pages.
A compact manifest commits the exact reconstructed journal. Cold open reconstructs
these bytes and executes normal native currency, finality, owner consent, value,
permanent-import and incident checks. Storage hashes never grant ledger authority.

This is an incompatible **no-value ground candidate**, with a new native
implementation and fresh signed fixture genesis. Earlier candidate currencies keep their own source commitments and private
state. Test balances never migrate. Legacy inline storage refuses without
rewrite. This phase is native disk paging, **not long-history execution**.

## Exact representation and durable publication

`RLD-NATIVE-HISTORY-MANIFEST-V1` commits the signed bootstrap, region, ordered
complete snapshots, local event pages, epoch proofs, contact records, incident
identities, canonical native journal digest and logical byte count. Immutable
`RLD-NATIVE-HISTORY-OBJECT-V1` records bind complete bytes, currency and local
store region. Foreign snapshots still require their own admitted native authority.

Event pages commit event offsets, before/after local heights and the exact previous
page hash. Missing, reordered, altered, incorrectly sized/scoped/typed or
noncanonical records refuse. Reads check private file ownership, permissions,
link count, type and byte bounds, and use no-follow descriptors on Unix.
Authenticated incident proofs remain in the existing durable native incident
archive and are committed by their exact native identities.

New objects and their directory are fsynced before publishing the manifest.
An identical retained object must match exact bytes and is synchronized again.
Prior partial-tail versions and unaccepted write residue are never deleted or
silently overwritten. A failed manifest publication retains the old visible native
tip and the newly written unaccepted objects. Orphan bytes never authorize progress.

Archive admission counts **all retained objects**, including old tails and orphans,
under **4,096 files / 256 MiB**. Every logical journal still refuses above **8 MiB**;
native **256-block / 64-snapshot** and permanent ledger index limits stay unchanged.
A 256-block native test reaches and preserves the real refusal boundary. None of
these limits describes 200,000-block capacity or an adopted-network upgrade.

## Exact externally retained storage head

`history-head` returns a fully replayed native observation, an exact storage head
and a permanent-import commitment. It is not a signature, independent freshness,
new issuance or global finality. The caller must retain its latest exact head
outside the rollback domain.

`history-check --expected-head ...` acquires the native OS lock and checks that
exact retained head before replay or incident reconciliation. Pending incidents
refuse. After authenticating the retained incident archive, the pinned open also
requires every authenticated incident to appear in the manifest index. A newly
retained unindexed proof refuses without changing the manifest or proof.

An actual regression reproduced the missing incident-index check before the fix:
a valid newly retained conflict quarantined its source, while the older storage
head could still pass. The retained
[baseline source](historical/unindexed-incident-baseline-source.tar.gz) and
[manifest](historical/unindexed-incident-baseline-source-manifest.json) identify
that failing test. The corrected native regression passes. An old valid manifest
can still replay through the ordinary **unpinned** open; rolling every archive
and external head back together remains unqualified.

The ordinary unpinned open preserves the existing native incident-recovery
behavior. These commands do not replace signer/caller or wallet heads and do not
implement fresh-target archive restore.

## Exact source and checks

The [237-file manifest](source-manifest.json) commits
`1756c85e876dbca24275c77e7d035673d2b3fd4a90c5c67b0cbbbf99cd0d445b`.
The [archive](source.tar.gz) and copied runtime tools use those exact bytes.
Native implementation is
`55342fdef7568fadbd9d0c6d529a081e3ccd490b62b37b3d10e28b900ca773f8`.
Frozen documentation retains its pre-run status; later terminal reports define
actual outcomes. The standalone stopped-history audit is separately committed
and cannot sign, install evidence or substitute for the frozen native validator.

Checked release rebuilding, **99 native tests**, strict clippy and **52 real
process/controller/storage/history tests** pass against this frozen source.
The earlier **84 transport tests** are retained against identical runtime/test
bytes, not rerun. [checks.json](checks.json) distinguishes them and commits logs.

The native checks cover actual owner payments, full finality, exact reconstruction,
immutable completed pages, old tail retention, forged self-consistent certificates,
missing/corrupt/symlinked/incorrectly scoped pages, storage admission, failed
manifest publication, old inline refusal, pending incidents and exact external-head
rollback refusal. Actual CLI checks include an original import identity surviving
maturity and a spent original output; a duplicate import still refuses natively.

The [first frozen source](historical/initial-storage-source.tar.gz) and
[manifest](historical/initial-storage-source-manifest.json) preserve source
`b0df4102859ee85f1101ef94b8626446bab4bd5ed7d4c10303ba665f8d218e6f`.
It rebuilt and passed 98 native tests and clippy. One of 52 process tests omitted
explicit selection of its actual 100-value input and correctly failed native
conservation. No fresh full cycle was started for that source. The request was
corrected before freezing this version; the native conservation rule was not
weakened. See [initial checks](evidence/regional-native-history-initial-checks-20261001.json).

## Fresh native cycle and stopped storage checks

The new signed fixture currency completed the ordinary twelve-node
Earth–Proxima–Andromeda–Earth cycle. Net recipient amounts were **96, 91 and 86**,
all fifteen `issued = liquid + pending exports` checks passed, and the four
replicas in each region agreed at heights **7 / 4 / 4**. All Earth nodes were
stopped during remote onward and return exports; the controller generated no
consensus votes, carried no payment proof and installed no checkpoint.

[Separate cold verification](evidence/regional-native-history-pinned-cycle-cold-20261001.json)
replayed twelve native stores, checked twelve historical recipient observations,
and authenticated **639 retained BFT envelopes / 1,424 transport archives**.
The initial and onward original outputs had been spent onward; the return
original output 86 remained spendable. All private files stayed unchanged.

[Separate native-history audit](evidence/regional-native-history-pinned-cycle-storage-audit-20261001.json)
reconstructed all twelve stores and checked each exact externally retained
storage head in fresh native processes. The largest manifest was **4,522 bytes**;
the largest reconstructed logical journal was **165,304 bytes**. This short
cycle had one event page per replica, so it does not demonstrate long-history
execution. Private files and all frozen source bytes stayed unchanged. A local
head retained during this check does not establish an independent latest anchor.

## Fresh full fault profile and stopped page reconstruction

The new [full fault profile](evidence/regional-native-history-pinned-fresh-fault-20261001.json)
passed in **723.342 seconds**, exited normally and stopped all
owned nodes. The actual net output **9** imported uniquely at Proxima height
**12** and matured at **14**. Final four-replica heights agreed at
**Earth 14 / Proxima 14 / Andromeda 16**. Local phase bounds were not extended,
source debit stayed retained, and the sealed cycle fixture stayed unchanged.

[Separate full cold verification](evidence/regional-native-history-pinned-fault-cold-20261001.json)
replayed twelve native stores, checked four original recipient outputs and
fully authenticated **1,922 BFT envelopes / 4,359 transport archives**.
Final native conservation was **300 = 300 + 0**. Private fixture files stayed
unchanged; the largest BFT retention state was **1,380,398 bytes** under the
unchanged 32 MiB bound.

[The additional native page audit](evidence/regional-native-history-pinned-fault-storage-audit-20261001.json)
reconstructed and checked exact retained heads for all twelve stores in fresh
native processes. Every replica crossed into **two event pages**; the largest
manifest was **6,791 bytes**, and the largest logical journal **434,232 bytes**.
All private files and frozen source stayed unchanged. This exercises a real
page boundary during ordinary BFT operation; it does not qualify long-history
execution, independent latest anchors or fresh-target restore.

The first additional fault-page audit stopped with a tool `KeyError: currency`
before its first native call: the fault report has no top-level currency field.
The [retained tool failure](evidence/regional-native-history-pinned-audit-tool-failure-20261001.json)
and [initial auditor](historical/audit-native-history-stopped-initial.py)
preserve that result. The separately committed corrected auditor binds currency
to the bootstrap and exact cycle/fault report and refuses owned running nodes.
Native runtime bytes did not change. [The corrected auditor also rechecked the stopped cycle](evidence/regional-native-history-pinned-cycle-storage-audit-current-20261001.json), with twelve full replays/exact heads and all private files unchanged. The initial cycle audit above used the
retained initial tool; the corrected fault audit is a separate passing result.

## Reproduce the observed path

Verify [SHA256SUMS](SHA256SUMS), extract into a fresh source directory and use
Rust 1.98.0. Build **all binaries**, including `contact-fixture`. Use absolute
paths and a private Python virtual environment; never resolve its executable
symlink into the base interpreter. The fixture and report directories below
must be new and must remain private.

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-cycle-report.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py \
  --source /absolute/source-v20 --manifest /absolute/package-v20/source-manifest.json \
  --run-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-cycle-cold-report.json
/absolute/private-venv/bin/python /absolute/package-v20/tools/audit-native-history-stopped.py \
  --source /absolute/source-v20 --manifest /absolute/package-v20/source-manifest.json \
  --run-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-native-history-audit.json
```

For a fresh full fault profile, preserve the completed, stopped cycle above;
the drill creates a separate new private root and retains that sealed source.
Do not copy an earlier failed fixture or rerun a payment from a replaced source.
The bounded local drill tests one offline Earth validator, cut Earth/Proxima
contacts, actual owner payments, native view change and local progress, restart
catch-up, restored-contact import/maturity and keyless certificate draining.

```sh
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py \
  --runtime-tools /absolute/source-v20/tools \
  --source-manifest /absolute/package-v20/source-manifest.json \
  --cycle-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --source-root /absolute/NEW-private-cycle --root /absolute/ANOTHER-NEW-private-fault \
  --report /absolute/your-fault-report.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py \
  --source /absolute/source-v20 --manifest /absolute/package-v20/source-manifest.json \
  --run-report /absolute/your-fault-report.json \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/ANOTHER-NEW-private-fault --report /absolute/your-fault-cold-report.json
/absolute/private-venv/bin/python /absolute/package-v20/tools/audit-native-history-stopped.py \
  --source /absolute/source-v20 --manifest /absolute/package-v20/source-manifest.json \
  --run-report /absolute/your-fault-report.json \
  --binary /absolute/source-v20/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/ANOTHER-NEW-private-fault --report /absolute/your-fault-storage-audit.json
```

Only run stopped-state audits after all owned nodes stop and the preceding
cycle/full-fault verifier passes. Keep actual failures and their exact source. A fresh native implementation
must never inherit the previous
[revision-19 finite fault pass](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-bft-shared-evidence-v19).
Private identities, keys, TLS/configuration files, native journals, protected
heads, wallet state and backups are excluded from publication.

Long-history native execution, bounded remote proof closure, permanent-index
scaling, independently retained latest roots, fresh-target recovery and an actual
200,000-block era remain required. So do full BFT reconfiguration, channels,
complete wallets, cryptographic horizons, independent custody/operations and
physical causal contacts. No I1–I12 requirement is fully qualified. See
[status](STATUS.zh-CN.md), [history obligations](HISTORY_RETENTION.md) and
[acceptance queue](ACCEPTANCE_QUEUE.md).
