# BFT unanimous epoch activation — revision 28

This fresh no-value native candidate adds the separately signed
`RLD-REGIONAL-BFT-UNANIMOUS-EPOCH-FIXTURE-V1` admission. Normal blocks still
require three ordered prepare votes and three ordered commit votes. Epoch
activation requires **all four old and all four fresh new validators** over the
exact closing checkpoint and new set. Legacy BFT/unanimous/segmented admissions
never silently acquire this authority. No old/adopted/test balances migrate.

Old approvals are released only after `EpochFence` is durable in the original
BFT signer journal. A signer that has acted on a successor proposal, prepare,
commit or timeout cannot fence the earlier closing point. A released fence
permanently prohibits new votes, even if activation remains incomplete. Exact
retained response recovery cannot first-sign. A separate late old-key legacy
signer cannot bypass BFT locks. Fresh candidate approval journals cannot vote
legacy checkpoints. Historical validator keys cannot return in later sets;
new BFT journals initialize only at their exact installed activation boundary.

The existing full native closing-history/value replay, finality certificates,
incident checks, wallet consent/conservation and caller-retained heads remain
mandatory. The complete certificate installs via normal native `install-epoch`
without changing balances. Blocks after activation must use the new epoch's
ordinary prepare/commit certificates. Current complete evidence/history bounds
are unchanged. This does not implement arbitrary overlapping validator sets,
reactivation, threshold changes, autonomous epoch configuration, cancellation,
unsealing, missing-signer liveness or fault-tolerant dynamic membership.

## Bound source and local results

[259 reviewed files](source-manifest.json), [complete source](source.tar.gz):
`7e9b5d8cea28839313d91ed5cfc6df42dac66f85403324de858be304810ad33e`. Native implementation:
`a1911d35bf70ee98a6fefb7f05b003f508144b19d265d152587b7b956a3911a2`.

[Checks](evidence/regional-native-bft-epoch-frozen-checks-20261002.json): checked
release, strict all-target checks, **149 native / 60 process tests**, from the
retained exact [pre-CLI-fix freeze](historical/native-process-pass-cli-refusal-manifest.json),
with the real archive CLI subcheck enabled. The final package changes only one
line in the supplemental ceremony input selector: require maturity at current
wallet review height, not the next block. Every native source and existing
process-test/runtime file is byte-identical to that passing freeze; the native
implementation identity remains unchanged. Those successful tests were not
rerun or relabeled as a new final-source run. The corrected actual CLI ceremony
runs separately from the final package source.

[Four-replica CLI ceremony](evidence/regional-native-bft-epoch-cli-campaign-20261002.json):
separate native stores, four durable old fences, four durable new approvals,
actual owner-signed payments before and after activation, all four native tips
at height 6, minted 300, no new allocation, exact old fence recovery without
private keys, separately retained caller heads and full cold replay on each CLI
call. Controller-carried consensus messages; same host/controller. This is
not an autonomous multiregion campaign or a full fault profile.

[Native regressions](evidence/regional-native-bft-epoch-native-sample-20261002.json)
also cover missing/changed/duplicate approvals, legacy admission refusal,
prepared-successor refusal, old-key legacy bypass refusal, interrupted durable
fence promotion/exact recovery, stale backup refusal under a surviving latest
head, late new-signer refusal, historical-key reactivation refusal, new-set
three-vote continuation and native reopening with the original payment intact.
No all-state/head rollback, copied-key concurrent custody, power-loss or external
operator/security qualification is inferred.

No new twelve-node value/fault result is inherited from revision 27 or earlier
sources. No generated key, native state, signer/wallet/caller journal, mesh/TLS
identity or private restoration image is published. The historical directory
retains initial test-compilation errors, three focused refusals caused by the
remaining legacy store guard, and the first frozen strict-check refusal for an
oversized message enum. Final code boxes that statement without changing its
serialized bytes. The first actual CLI run then correctly refused an immature
wallet input before signing/debit. Four stopped native replicas replay at height
3 with minted 300; every private file is unchanged and retained. The corrected
controller uses a fresh private directory; no failed state/value is migrated.
Reports/archives preserve exact sources; logs redact workspace
prefixes and normalize trailing blank lines, with both local/public hashes.

## Reproduce

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v28
tar -xzf source.tar.gz -C /absolute/source-v28
cd /absolute/source-v28
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
RLD_STREAM_TEST_BINARY=/absolute/source-v28/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --lib -- --nocapture
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v28/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history
/absolute/private-venv/bin/python tools/regional_bft_epoch_campaign.py --binary /absolute/source-v28/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-ceremony --report /absolute/ceremony.json
```

Preserve stopped old signer/caller state and partial activation evidence.
No timeout or missing receipt restores old signing rights or refunds value.
I1–I12 remain mandatory; fault-tolerant membership, long history/beyond-era
execution, compact complete proofs, independent operators/archives/custody,
cryptographic evolution and physical routes remain open. Future mainnet needs
separate qualification and a newly signed zero-issuance genesis.
