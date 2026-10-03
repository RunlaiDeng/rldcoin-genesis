# Verified native prefix replay and retained-capacity observation — revision 18

This ground candidate reuses only an exact predecessor ledger already fully
replayed in this process under the same complete verified trust set. Every new
block still undergoes normal native identity, work, owner, value and state-root
checks. Cold startup reconstructs from genesis; no serialized ledger cache can
supply authority. Rejected tails leave finality and ledger state unchanged.

The fresh twelve-node value cycle and separate stopped-state verifier passed.
The subsequent full fault profile **failed** its recipient-maturity deadline;
BFT companion state reached its retained byte bound. These are distinct results.
This package preserves exact source, successful checks and the failure. It does
not qualify sustained BFT liveness, long history or independent operation.

A mainnet has not launched. All fixtures here have no monetary value.
The native implementation identity changed: create a fresh fixture genesis.
Never reuse prior currency or migrate old/test balances. A future mainnet needs
new signed zero-issuance genesis and separate complete qualification.

## Native change and checks

The exact source contains 230 files, committed by
`47b07d586f58914881c98e32dd7abc93b8cdbfb449b7d6f15538594dd95ecd62`.
The native implementation is
`d268bd83be7f87afa2db26603ae4597d711aa85eaaf265bccdce8d1426b2e971`.
The [manifest](source-manifest.json) and [archive](source.tar.gz) identify every
runtime source byte; supplemental tool copies match it. The separate
`tools/verify_regional_bft_cycle.py` is committed separately in [checks](checks.json).
Frozen documentation describes the pre-run snapshot; terminal reports below
record later actual outcomes without rewriting that snapshot.

A checked release rebuild with Rust 1.98.0 passed 86 native tests, strict
all-target clippy, 84 transport tests and 34 process/controller tests. Five new
native regressions cover exact complete trust, rejected tails, retained imported
and onward value, 64-checkpoint cold replay against a genesis oracle, and actual
BFT proposal/certificate replay. [The baseline regression](evidence/regional-native-prefix-trust-regression-20261001.json)
actually failed on revision-17 runtime code with only the appended
[behavioral test](baseline-regression-test.rs). Because source-bound implementation
identity includes the test source, this augmented build is not the original
revision-17 binary. This new reuse condition is not an independent security audit.

The [64-checkpoint sample](evidence/regional-native-prefix-replay-sample-20261001.json)
executes 64 native blocks during cold verification; replaying every prefix from
genesis executes 2,080. Every ledger field and root agrees. Timings cover different
certificate-check workloads and are not end-to-end throughput claims. The
256-block / 64-snapshot limits remain unchanged; the 65th snapshot still refuses.
[Long-history obligations](HISTORY_RETENTION.md), including the 200,000-block
era, permanent deduplication, external latest-state protection and independent
recovery, are still unimplemented or unqualified.

## Fresh autonomous cycle — passed

The [fresh cycle](evidence/regional-native-prefix-fresh-cycle-20261001.json)
uses this implementation and a new fixture currency. Twelve ordinary node
processes relay through pinned TLS neighbors. All Earth nodes stop while
Proxima and Andromeda import, mature, onward-export and create a new return.
Original source debit remains deducted; return uses new export/import IDs.

- Original recipient net amounts: 96, 91 and 86.
- Four agreeing replicas per region: Earth 7, Proxima 4, Andromeda 4.
- All 15 native I=U+T checks conserve value.
- Controller-generated votes, value-proof carriage, checkpoint installation and
  remote-phase Earth calls: zero.
- [Separate stopped-state verification](evidence/regional-native-prefix-fresh-cycle-cold-20261001.json):
  twelve native replays, twelve historical recipient checks, 1,472 fully
  authenticated retained archive payloads; private files unchanged.

Original Proxima/Andromeda outputs were subsequently spent; original returned
Earth output 86 remains spendable. The 71 phase observations sum to 378.802
seconds; that sum is **not** measured whole-run wall time. [Five actual verifier refusals](evidence/regional-native-prefix-cycle-verifier-refusals-20261001.json)
cover altered authority counters, implementation, time bounds, amount and a
running private fixture. No verification output was created for those refusals.

## Subsequent full fault profile — failed, retained

The [1,059.417-second fresh fault run](evidence/regional-native-prefix-fresh-fault-20261001.json)
continued an isolated copy of this new stopped cycle. Earth validator 0 stayed
offline, Earth–Proxima contacts were cut, three online validators passed height
9 in 342.234 seconds, and the restarted node caught up in 6.170 seconds.
Contacts returned 426.039 seconds from startup. Both isolated remote local
payments executed. The original new export stayed deducted during disconnection.

Recipient maturity did not complete within its 600-second observation bound.
After shutdown, native heights were 16/16/17 with four equal heights in each
region; the campaign's stopped-prefix conservation observation records issued
300 = liquid 300 + in transit 0. Height equality alone is not full state agreement.
The [separate diagnostic reads](evidence/regional-native-prefix-failed-fault-diagnostic-20261001.json)
replay all twelve native stores and check all four exact recipient outputs:
net 9 imported at Proxima height 15, requires height 17, and remains unspent
and unquarantined at height 16, **not spendable**. Every private file stayed
unchanged. The full-profile verifier actually refused this failed run.

Andromeda retained state approached 32 MiB despite only 189 messages, below the
512-message bound. Exact repeated evidence snapshots accounted for up to
32,723,146 bytes, whereas distinct complete snapshot bytes totalled at most
585,876 in the inspected states. This is byte accounting, not an implemented
storage repair or proof of the sole cause of the maturity failure. Native lock
contention and refused TCP custody also occurred. Next implement bounded exact
shared evidence storage and rerun the full profile; do not increase limits,
prune signed evidence or replace this failure with a recovery result.

All owned nodes stopped, original sealed cycle and frozen source stayed
unchanged. The passing [revision-17 fault profile](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-bft-fault-recovery-v17)
is historical evidence for its different implementation, not a pass for this one.

## Reproduce the observed path

Verify [SHA256SUMS](SHA256SUMS) before extraction. Build all binaries, including
`contact-fixture`, using Rust 1.98.0. Use absolute paths and a private environment
with the exact Python requirements. Start a new cycle; do not supply published
reports in place of reports from your own private fixture.

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo test --locked --release --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --all-targets --manifest-path tools/regional-ledger/Cargo.toml -- -D warnings
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools /absolute/private-venv/bin/python -m unittest test_interstellar_mesh test_interstellar_tcp test_interstellar_transfer test_interstellar_route_budget
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v18/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py \
  --binary /absolute/source-v18/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle \
  --report /absolute/your-cycle-report.json
/absolute/private-venv/bin/python /absolute/package-v18/tools/verify_regional_bft_cycle.py \
  --source /absolute/source-v18 --manifest /absolute/package-v18/source-manifest.json \
  --run-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v18/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-cycle --report /absolute/your-cycle-cold-report.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py \
  --runtime-tools /absolute/source-v18/tools --source-manifest /absolute/package-v18/source-manifest.json \
  --cycle-report /absolute/your-cycle-report.json \
  --binary /absolute/source-v18/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --source-root /absolute/NEW-private-cycle --root /absolute/NEW-private-fault-copy \
  --report /absolute/your-fault-report.json
```

Run stopped-state verification only after owned processes stop. A failed fault
report cannot pass `tools/verify_regional_bft_sustained.py`; preserve the failure
and private fixture. Never run copied signer keys concurrently. Observation
deadlines do not refund exports, release reservations or delete evidence.

Mesh V3/TCP-V4 limits remain 256 active messages, completed archive high-water 32,
16 transitions per tick, 4096 archive files / 256 MiB per node and 512 immutable
process-local transit witnesses. Configured endpoints and TLS pins never come
from advertisements; socket waits hold no mesh lock. A three-second socket
attempt does not bound total tick/CPU. Transport custody never authorizes value.

Private identities, TLS/configuration files, journals, signer/caller heads,
wallet state, keys and backups are excluded. Source fixture keys are worthless.
Full BFT reconfiguration, channels, complete wallets, long-term archives/crypto,
independent operation/custody and physical routes remain mandatory. See
[status](STATUS.zh-CN.md) and [acceptance queue](ACCEPTANCE_QUEUE.md).
