# Bounded native archive replay — revision 25

This **no-value ground candidate** introduces a separate read-only stream
archive verifier. From caller-pinned signed genesis, it executes every block
through the same native owner/value/import/issuance kernel as ordinary chains.
No decoded ledger, cached state, snapshot digest or peer observation can
initialize its cursor. The ordinary chain's execution rule body remains exact
after replacing context accessors with already-derived fields; see the
[kernel review](evidence/regional-native-stream-replay-final-kernel-review-20261002.json).

The rolling cursor retains at most **256 history observations** and **64 exact
native-verified local anchors**. Complete permanent state maps retain their
**4,096-entry** bounds. The archive is private and singly linked, at most **256
MiB**, with at most **8 MiB** per complete newline-terminated record. Records
carry full Evidence, one native Block or one Finalize ID. Evidence receives full
native verification; exact prefix observations bind local certificates.
Invalid tails stage all fallible checks before changing value, history or anchor.

`history-stream-check --bootstrap GENESIS.json --region earth --file PRIVATE.jsonl
--expected-head EXACT_HEAD` requires the separately retained exact replay head.
It never opens/adopts a node store and leaves archive bytes unchanged. It
refuses RESTORING targets, wrong heads, truncated/malformed/oversized records,
unsafe links/permissions, unsigned ledger records and incompatible trust.

## Real bounded replay observation

[The new frozen sample](evidence/regional-native-stream-replay-final-stream-sample-20261002.json)
contains **1,032 native blocks / 1,024 actual-owner signed local payments**,
a delayed return import of **net 59**, permanent duplicate-import refusal and
exact cold replay. Only **256 history observations** remain; the private
archive is **1,338,021 bytes**. This measures this fixture, not
arbitrary workload memory or long-range finality. Real native CLI subprocesses
check this archive and refuse wrong heads, truncation and interrupted restore;
no store is created and all original bytes remain unchanged.

## Explicit unfinished authority and capacity

The profile supports only an **initial unanimous PoW region**. Local epoch
handoff and BFT refuse; admission thresholds are never lowered. The stream
format **does not reconcile incidents/quarantine**. Passing it grants no
recovered ledger, current spendability, new finality, wallet/signer custody or
independent freshness. Its CLI reports these limits. Existing fully authenticated
foreign snapshots still require their complete native evidence. New long-range
snapshot authority and ordinary live-node history are not implemented here.

Ordinary stores, snapshots, BFT, wallets/signers retain **256 blocks / 64
snapshots / 8 MiB** logical bounds; permanent indexes and transport/archive
bounds remain. The changed source uses fresh signed zero-allocation fixture
genesis/currency; old candidate/adopted/test balances never migrate. This is not
200,000-block-era recovery, incremental durable indexing, complete compact
remote value authority, independent latest-state protection, physical-link or
cross-device qualification. No I1–I12 gate is fully qualified.

## Exact frozen source and current verification

[250 source files](source-manifest.json), [complete reviewed source](source.tar.gz):
`1593d355e4bf94514ce596c06aaaae0c58b0464fe1e8ecb788f646d594073b53`. Native implementation:
`601b7153fe673292ede3c23ced9f765d0e4cd572532f0e9563f3cf01664cafe8`. Frozen documents retain pre-run status;
current reports define actual results.

The checked release build, **133 native tests**, strict all-target clippy and
**59 process/controller/retention/history/state-proof tests** pass. Five new
native regressions cover full-chain equivalence and preserved legacy refusal,
atomic invalid tails, incompatible BFT/trust/unsigned-state refusal, actual
long signed payments/delayed imports/cold and CLI replay, and private file/
record/capacity refusal. The final test run enables `RLD_STREAM_TEST_BINARY`;
the sample explicitly confirms CLI checks ran. Prior **85 transport tests**
come from exact unchanged transport source and were **not rerun here**.
[Checks](checks.json) bind the source, binary and current/prior report hashes.

[The fresh twelve-node cycle](evidence/regional-native-stream-replay-final-fresh-cycle-20261002.json)
passes the native three-region value path with net **96 / 91 / 86** and fifteen
conservation checks. All Earth nodes stay stopped during remote onward/return;
controller vote/proof/checkpoint construction stays zero. Separate
[cold verification](evidence/regional-native-stream-replay-final-cycle-cold-20261002.json)
and [12 private ledger-image fresh-target audits](evidence/regional-native-stream-replay-final-cycle-fresh-target-audit-20261002.json)
pass with exact state, heads, permanent imports, incidents and retained bytes.
Images exclude key/signer/replica/wallet/caller/mesh/TLS/transport custody.
Generated archives/images/state remain private; originals and frozen source
remain unchanged. **No fresh full fault profile was run for revision 25**;
revision-24 fault qualification is not inherited. This cycle uses ordinary
bounded node stores and does not qualify long-history ordinary BFT operation.

[Two initial native-source-only captures](historical/captures.json) retain the
compiler failure from an unavailable test-only uuid reference and strict
clippy's large enum refusal. Use the existing unique fixture directory
constructor and indirect Block allocation; no rule/bound/warning is relaxed.
Their sanitized raw logs are inside the named reviewed archives, preserving
all bytes except the declared workspace path substitution. Neither capture
is a full workspace freeze or receives current process/lifecycle qualification.

A report-controller variable error occurred after all 133 native tests passed.
[The resume record](evidence/regional-native-stream-replay-final-controller-resume-20261002.json)
binds the successful native log and saved helper; remaining checks continued
against unchanged frozen source. Passed tests were not repeated.

## Reproduce

Verify SHA256SUMS, extract source into a fresh directory, use Rust 1.98.0 and
a private Python virtual environment. Never resolve the venv executable symlink.
Keep generated fixtures and images private.

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
RLD_STREAM_TEST_BINARY=/absolute/source-v25/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- --nocapture
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v25/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v25/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v25 --manifest /absolute/package-v25/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v25/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v25 --manifest /absolute/package-v25/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v25/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images-audit.json
```

Run stopped audits only after all owned processes stop. The two private ledger
archive formats have separate authority: ordinary ledger images fully replay
native incidents; the stream checker does not adopt/recover such a ledger.
Keep exact failures and source commitments. See [status](STATUS.zh-CN.md) and
[history obligations](HISTORY_RETENTION.md). Work continues on ordinary-node
bounded history, new long-range native finality, durable permanent indexes,
independent archives/anchors and cryptographic/physical qualification.
