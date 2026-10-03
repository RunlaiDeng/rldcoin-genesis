# Bounded contact archive ground candidate: revision 16

The incompatible `RLD-CONTACT-MESH-V3` / `RLD-CONTACT-TCP-V4` candidate moves
completed transport custody into retained, signed-indexed, fully authenticated
archive files. It uses fresh fixture identities/configurations/state, refuses
legacy formats without rewrite, and adopts neither old balances nor a mainnet.

Workspace and exact frozen-source runs complete the twelve-node
Earth → Proxima → Andromeda → Earth value cycle with all Earth nodes stopped
during remote execution, four agreeing replicas per region at heights 7/4/4,
recipient fixture amounts 96/91/86 and all 15 I=U+T conservation observations.
Original debit remains permanent; receipts never credit value. These are
same-host, same-controller ground observations, not physical stellar routes.

The 226-file source archive is independently rebuilt with the pinned Rust
1.98.0 toolchain, overflow checks and debug assertions. Seventy-eight transport
checks and 36 native-process/HTTP checks pass. All 24 retained native stores
across both runs fully replay with identical monetary projections, events,
incidents and epoch proofs. Each frozen-run archived payload is independently
read and authenticated after its node process exits. Exact reports keep timing,
read-only retry counts and complete-journal observation hashes individually;
only those named fields may vary. A monetary or safety mutation refuses
comparison. The unchanged native source retains its earlier 81-test evidence;
that native suite was not rerun for these Python archive changes.

## Custody bounds and recovery

Active messages/receipts remain bounded at 256 each, with a high-water mark of
128 and at most 16 archive transitions per tick. Archives retain at most 4096
files and 256 MiB, including crash orphans/staging, and each payload/index is
bounded. This budget is a ground refusal boundary, not a retention horizon.
Capacity, corrupt/missing files and unsafe ownership refuse while preserving
evidence. Archiving never deletes historical evidence or authorizes a payment.
Repeated custody authenticates the retained bytes and fsyncs file/directory
before acknowledgment. An unchanged archive does not require replacement.

The separately named [process-crash drill](tools/interstellar_archive_crash_campaign.py)
kills an owned child at three exact boundaries: after payload link before sync,
after durable payload before index commit, and after durable index commit.
Restart preserves the active original or recovers the exact archived payload
and scoped receipt. Crash staging is retained. SIGKILL establishes process-loss
behavior; it does not model loss of power/storage caches, independent custody
or cross-device restoration. The drill has its own exact source hash and is
not silently added to the 226-file full-cycle source manifest.

## Reproduce from exact source

Download [source.tar.gz](source.tar.gz), [SHA256SUMS](SHA256SUMS) and the linked
reports from the same commit-pinned package. Check the archive against its
listed checksum, extract into a fresh source directory and inspect the
[source manifest](source-manifest.json). The original 167 base source files
are unchanged. Documentation inside the archive is the frozen pre-run source
snapshot; this README and terminal reports state the completed observation.

From the extracted source directory:

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m venv /absolute/private-contact-venv
/absolute/private-contact-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
/absolute/private-contact-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/sanitized-cycle-report.json
/absolute/private-contact-venv/bin/python /absolute/package/tools/interstellar_archive_crash_campaign.py --runtime-tools /absolute/source/tools --root /absolute/NEW-private-crash-drill --report /absolute/sanitized-crash-report.json
```

Retain private fixture directories for recovery and analysis. Never publish
identities, TLS private PEMs, configs, native journals, signer state, caller
heads, wallets, keys or backups. Public fixture key constants in the source
are for worthless ground experiments only. Observation limits stop the local
experiment, never release a debit or remove pending evidence.

## Evidence and remaining acceptance

- [Frozen cycle report](campaign-report.json), [full verification](verification.json), [process-crash report](process-crash-report.json)
- [Acceptance queue](ACCEPTANCE_QUEUE.md), [mandatory master plan](../../../MASTER_PLAN.md)
- [Historical V2/TCP-V3 revision 15](../../2026-09-30/regional-native-bft-multiregion-v15/README.md)

Sustained offered load and validator/contact faults, cross-host operation,
power-loss storage qualification, independent operators and private key custody,
full BFT membership handoff, channels E, complete wallets, long-term archive and
cryptographic evolution, exact new signed zero-issuance adoption and actual
physical route qualification remain mandatory. I1–I12 are not fully qualified.
No independent security audit, operating interstellar service or mainnet is claimed.
