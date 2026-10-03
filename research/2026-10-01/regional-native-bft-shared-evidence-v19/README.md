# Exact shared BFT evidence storage — revision 19

The supplemental companion now shares snapshots by their complete canonical
bytes instead of repeating the same proof in every retained control envelope.
Original bodies, ordered and repeated snapshot references, value/local flags,
and full envelope digest and size survive exact reconstruction. Incoming and
cold-start envelopes still receive full native authentication. Hash agreement
never grants ledger, finality, signing or issuance rights.

The exact 234-file source completed a fresh twelve-node value cycle and a
653.438-second full fault profile. This is one finite, same-host/controller,
no-value ground experiment. It does not qualify sustained BFT liveness, long
history, independent custody, power loss or physical interstellar service.
Separate stopped-state reports and checks below define the observed scope.

A mainnet has not launched. Future adoption needs new signed
zero-issuance genesis; old/test balances never migrate. Native implementation
identity is unchanged from revision 18; private retention layout is incompatible.
Preserve legacy states and use fresh private fixture directories. Do not rewrite
old private state or run copied signer keys concurrently.

## Exact storage and refusal boundaries

`RLD-REGIONAL-BFT-RETENTION-V2` is a supplemental storage wrapper, not a new
consensus proof. It retains immutable canonical snapshot and message bytes.
Sharing uses the full snapshot byte digest, so different certificates for the
same statement remain distinct. A reconstructed envelope is a new object;
caller mutation cannot alter retained bytes. Exact expansion size is checked
before decoding snapshots, avoiding oversized repeated-reference expansion.

The combined index and snapshot payloads still refuse above **32 MiB**.
The limits remain **512 messages**, **64 snapshot references per envelope** and
**3 MiB network payloads**. No evidence is deleted. Broadcast rotates only
unsent message/recipient metadata and reconstructs selected payloads, rather
than retaining all pending expanded payloads at once. The native ledger's
256-block / 64-snapshot bounds remain unchanged.

Native verification precedes new retention and runs again on every reconstructed
envelope at startup and during the stopped-state checks. Missing, altered,
orphan or oversized snapshot bytes, changed envelope identity/size/digest,
noncanonical state and forged native certificates refuse. A self-consistent
new digest does not validate a forged certificate. Failed state writes preserve
the exact already-signed response in the separately retained caller-head outbox;
keyless recover-only cannot first-sign. Old inline storage refuses without
automatic migration. Full-state/head rollback and independent custody remain
unqualified.

## Byte accounting and actual checks

A [byte-only sample](evidence/regional-bft-shared-evidence-byte-sample-20261001.json)
round-tripped all 2,259 envelopes in the twelve stopped revision-18 failed stores.
Every body, full proof, value and local flag matched. Maximum inline state was
33,529,748 bytes; prospective exact shared representation was at most 1,628,727
bytes. Private files were unchanged and not migrated. The sample does not
perform native authentication or repair the original failure; its codec bytes
belong to the retained first source snapshot, described below. It is not a
throughput benchmark or evidence of long-history qualification.

The final frozen source was rebuilt as checked release with Rust 1.98.0 and
passed **47 process/controller/storage tests**, including 13 retention checks.
They cover exact reconstruction, immutable input/output boundaries, altered
metadata and proof refusal, expansion bounds, 512-message capacity, state-byte
refusal, loss before replacement, response acknowledgment loss after replacement,
keyless exact response recovery, legacy-state refusal and the controller reader.

Native source bytes are unchanged; earlier 86 native tests and strict clippy are
retained as evidence, not rerun. The earlier 84 transport checks are also retained
against identical transport runtime/test files. [checks.json](checks.json) records
these distinctions, source commitments and actual log/report hashes.

## Fresh autonomous value cycle

The [new cycle](evidence/regional-bft-shared-retention-observer-fresh-cycle-20261001.json)
starts fresh private stores under this implementation. Twelve ordinary pinned-TLS
nodes complete Earth → Proxima → Andromeda → Earth. All Earth nodes stop during
remote import, maturity, onward export and new return. Original source debit
remains deducted; return uses a new export and import.

Net recipient amounts are 96, 91 and 86. Four replicas agree at regional heights
7/4/4; all 15 native I=U+T checks pass. Controller-generated votes, proof carriage,
checkpoint installation and remote-phase Earth calls are zero. The separate
[cycle cold verification](evidence/regional-bft-shared-retention-observer-cycle-cold-20261001.json)
replays twelve native stores, checks twelve historical original outputs,
authenticates 627 retained BFT envelopes natively and authenticates 1,408 transport
archive payloads. Every private file remains unchanged. Maximum retained BFT
state is 414,719 bytes. Earlier recipient outputs were spent onward; original
returned output 86 remains spendable. Phase durations are observations, not
whole-run wall-time measurements.

[Five actual verifier refusals](evidence/regional-bft-shared-retention-verifier-refusals-20261001.json)
cover a boolean authority counter, altered implementation, altered return amount,
nonfinite duration and a running private fault fixture. None created a passing
verification report or changed the stopped cycle.

## Full finite fault profile

The [fresh fault run](evidence/regional-bft-shared-retention-fresh-fault-20261001.json)
uses an isolated copy of this completed stopped cycle, not the previous failed
fixture. Earth validator 0 is offline and Earth–Proxima contacts are cut in both
directions. Ordinary companions authenticate a view change and advance three
online Earth replicas past height 9 in 115.191 seconds. Both isolated remote
local payments execute. The restarted Earth replica catches up in 29.934 seconds;
interregion contact returns 214.932 seconds from start.

The original net output 9 imports once at Proxima height 12 and matures at 14.
The maturity observation after restoration takes 337.251 seconds, within the
unchanged 600-second phase bound. Pausing new signatures while retaining keys
allows complete native certificates to drain in 13.192 seconds. The complete
finite run takes 653.438 seconds. Regional final heights are 15/14/15, with four
agreeing replicas per region. Source debit, exact original import and conservation
remain native requirements; local timeouts never refund exports or erase evidence.

The separate [fault cold verification](evidence/regional-bft-shared-retention-fresh-fault-cold-20261001.json)
replays all twelve native stores, verifies all four original recipient outputs,
authenticates 1,898 retained BFT envelopes and 4,324 transport archive payloads,
and matches each separate caller head. Issued 300 = liquid 300 + in-transit 0.
All private files remain unchanged. Maximum retained BFT state is 1,378,543 bytes
under the unchanged 32 MiB bound.

The local signing stop height remains 24. Neither this finite signing cap nor
one passed profile proves general BFT liveness or capacity. The previous
[revision-18 failure](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-prefix-replay-v18)
is retained unchanged. Different observations do not establish the storage
change as the sole cause of improved progress; transport contention also varies.

## First frozen controller-reader interruption

The initial 234-file snapshot
`24fb58eda0a3fcea0744b12e6b2587656a1d740ede5c93b25b6a4291133f6042`
rebuilt and passed 84 transport and 46 process/storage checks. The cycle observer
still read the old inline layout and swallowed a deterministic KeyError while
all four Earth replicas already retained the actual owner submission. A controlled
interrupt ran normal cleanup. [Stopped-state checks](evidence/regional-bft-shared-retention-observer-interruption-20261001.json)
replayed twelve native stores and authenticated 128 retained control envelopes;
private files and exact source stayed unchanged. No cycle or fault pass is claimed.

The [historical archive](historical/observer-interruption-source.tar.gz) and
[manifest](historical/observer-interruption-source-manifest.json) preserve that
source. The final source fixes both campaign readers with bounded read-only
wrapper inspection; it neither carries proofs nor authorizes ledger inclusion.
The subsequent fresh cycle and fault run use the final source exclusively.

## Reproduce the observed path

[source-manifest.json](source-manifest.json) names the exact 234 files in
[source.tar.gz](source.tar.gz), committed by
`5ab9e125172125c34ecd81d811c2f00097a59801d7b326afa017559476c52bc0`.
Native implementation remains
`d268bd83be7f87afa2db26603ae4597d711aa85eaaf265bccdce8d1426b2e971`.
Supplemental tool copies match those same bytes. Frozen documentation records
pre-run status; immutable terminal reports record the subsequent outcomes.

Verify [SHA256SUMS](SHA256SUMS), then extract to a fresh source directory. Use
Rust 1.98.0, absolute paths and private Python requirements. Build all binaries,
including `contact-fixture`. Keep your own stopped cycle directory and newly
produced reports; published reports are not substitutes for your own run.

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v19/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py \
  --binary /absolute/source-v19/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-cycle-report.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py \
  --source /absolute/source-v19 --manifest /absolute/package-v19/source-manifest.json \
  --run-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v19/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-cycle-cold-report.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py \
  --runtime-tools /absolute/source-v19/tools --source-manifest /absolute/package-v19/source-manifest.json \
  --cycle-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v19/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --source-root /absolute/NEW-private-cycle --root /absolute/NEW-private-fault-copy \
  --report /absolute/your-fault-report.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py \
  --source /absolute/source-v19 --manifest /absolute/package-v19/source-manifest.json \
  --run-report /absolute/your-fault-report.json \
  --binary /absolute/source-v19/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-fault-copy --report /absolute/your-fault-cold-report.json
```

Run cold checks only after owned processes stop. Preserve failures and private
fixtures; a recovery stage cannot replace a full-profile pass. Private identities,
TLS/configuration files, native journals, signer/caller heads, keys, wallet state
and backups are excluded. Source fixture keys are for worthless experiments.

Mesh V3/TCP-V4 limits remain unchanged: 256 active messages, completion-only
archive high-water 32, 16 archive transitions per tick, 4096 archive files /
256 MiB per node and 512 immutable transit witnesses. Configured TLS endpoints
and pins never come from advertisements. A three-second socket attempt does not
bound total tick or verification CPU. Custody and transport receipt never grant
native value. Full BFT reconfiguration, channels, complete wallets, long-term
archives/crypto, independent custody/operations and physical routes remain
mandatory. See [status](STATUS.zh-CN.md), [history obligations](HISTORY_RETENTION.md)
and [acceptance queue](ACCEPTANCE_QUEUE.md).
