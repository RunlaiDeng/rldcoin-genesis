# Exact native disk checkpoint prefixes — revision 22

The incompatible **no-value ground candidate** now stores repeated checkpoint
block prefixes by exact predecessor object reference. It reconstructs the
complete original signed native snapshots and journal before normal native
authentication. Neither object hashes nor compression grant value authority.
Changed native source requires fresh signed fixture genesis; old/test balances
never migrate and no adopted or retired network is upgraded.

## Storage and refusal boundaries

`RLD-NATIVE-HISTORY-MANIFEST-V2` / `RLD-NATIVE-HISTORY-OBJECT-V2` retain a full
first checkpoint. Later objects carry new blocks, complete certificate/era
metadata and the exact earlier predecessor object's digest, length and prefix
height. Only already directly listed objects may supply that prefix: no recursive
traversal, orphan adoption, forward reference or cross-region/currency reuse.
Expanded complete snapshot bytes must fit the declared logical journal budget;
the complete reconstructed journal commitment and full native replay must pass.

Exact repeats and authenticated equivalent BFT quorum encodings remain native
evidence. Every listed proof is retained, with the earliest exact predecessor
object providing deterministic sharing. Unchecked normalization never replaces
native certificate validation. V1 directories refuse unchanged. All previous
objects, tails and failure residue remain retained and counted against capacity.

Logical **8 MiB / 256 blocks / 64 snapshots**, permanent ledger indexes and
**4096 history files / 256 MiB** remain unchanged. Full logical memory state and
signed transport snapshots still contain complete prefixes. This is disk sharing,
not compact remote proofs, 200,000-block execution or long-term qualification.
Private image recovery still excludes keys, signer/replica, wallet, caller-head,
pending, TLS and transport custody. No private image or generated state is here.

## Exact frozen checks and measured cost

The [242-file manifest](source-manifest.json), [complete source](source.tar.gz)
and copied runtime tools commit `a108ec7da7e8707d0c46093e33af64ae6893fb2529ea22eb5a773e0a23a1d928`. Native implementation
is `64c09ec0696918b42f0c91fe82cb66c9ea833e1e205d873f89d9174bad24a2a6`. Frozen documentation retains pre-run status;
these later results define outcomes. Checked release rebuilding, **116 native
tests**, strict all-target clippy and **57 real process/controller/history tests**
pass. Earlier **84 transport tests** use exact unchanged files and were **not
rerun**; [checks](checks.json) identifies their preceding record and log hashes.

[The exact 64-checkpoint sample](evidence/regional-native-history-prefix-final-storage-sample-20261002.json)
reduces referenced snapshot object bytes from **1,314,584** to **149,192**,
**88.65%**. This compares complete V2 objects for the exact same snapshots;
it is not a claim about transport bytes, total residue or unlimited history.
Reconstructed logical bytes, ledger state and a fresh private image restore
match exactly. Seven new checks cover full replay/recovery, missing/corrupt and
unlisted/forward/type/range references, compressed expansion limits, forged
certificates and duplicates, valid exact repeats and V1 refusal without rewrite.
Existing real owner/payment/import/incident/BFT tests also pass the new storage.

The [first complete frozen source](historical/initial-source.tar.gz),
[manifest](historical/initial-source-manifest.json), [terminal failure report](historical/initial-failure.json)
and [native log](historical/initial-native-tests.log) preserve the unintended
duplicate-checkpoint refusal exposed by full regression: 87
passed / 28 failed. The final fix preserves native
duplicate equivalence and adds a focused regression. The initial source never
received a cycle/fault pass; it is not qualification for this final source.

## Fresh signed lifecycle and stopped recovery

[The new twelve-node cycle](evidence/regional-native-history-prefix-final-fresh-cycle-20261002.json)
delivers net **96 / 91 / 86**, passes all fifteen conservation checks and agrees
at four-replica heights **7 / 4 / 4**. All Earth nodes remain stopped during
remote onward/return exports; controller vote/proof/checkpoint construction is
zero. [Separate cycle cold checks](evidence/regional-native-history-prefix-final-cycle-cold-20261002.json)
replay every stopped store and original output, authenticate retained control and
transport evidence, and leave private state unchanged.

[The new full finite fault profile](evidence/regional-native-history-prefix-final-fresh-fault-20261002.json)
passes in **705.36 seconds**, exits normally and stops every owned process.
Original net **9** imports at height **12**, matures at
**14** and remains unique. No bound increase, pruning,
deadline refund or reuse of prior candidate value obtains this pass.
[Separate fault cold checks](evidence/regional-native-history-prefix-final-fault-cold-20261002.json)
replay twelve stores and four original outputs and authenticate **1,918 BFT
envelopes / 4,352 transport archives**, without writing private state.

[Cycle](evidence/regional-native-history-prefix-final-cycle-fresh-target-audit-20261002.json)
and [fault](evidence/regional-native-history-prefix-final-fault-fresh-target-audit-20261002.json)
private image audits each restore twelve stopped native stores into fresh targets:
**24 complete ledger images/restores** match exact native heads, full state/value,
permanent imports, incidents and retained bytes. Originals and frozen source stay
unchanged. These same-host/controller observations provide no independent latest
anchor, power-loss, copied-key or signer/wallet custody qualification.

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
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive
/absolute/private-venv/bin/python tools/regional_bft_multiregion_campaign.py --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_cycle.py --source /absolute/source-v22 --manifest /absolute/package-v22/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v22 --manifest /absolute/package-v22/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --images /absolute/NEW-private-cycle-images --report /absolute/cycle-images-audit.json
/absolute/private-venv/bin/python tools/regional_bft_sustained_campaign.py --runtime-tools /absolute/source-v22/tools --source-manifest /absolute/package-v22/source-manifest.json --cycle-report /absolute/cycle.json --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/NEW-private-cycle --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault.json
/absolute/private-venv/bin/python tools/verify_regional_bft_sustained.py --source /absolute/source-v22 --manifest /absolute/package-v22/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --report /absolute/fault-cold.json
/absolute/private-venv/bin/python tools/verify_regional_history_archive.py --source /absolute/source-v22 --manifest /absolute/package-v22/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v22/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/ANOTHER-NEW-private-fault --images /absolute/NEW-private-fault-images --report /absolute/fault-images-audit.json
```


Run stopped audits only after owned processes stop. Keep all generated state and
images private; retain failures with exact source. Revision-21 and older failed
sources remain separate historical evidence. Independent latest anchors/archives,
long-history memory/proofs/index scaling, 200,000-block eras, cryptographic
horizons, cross-device custody, complete BFT reconfiguration, independent review
and actual causal physical contacts remain open. No I1–I12 gate is fully qualified.
See [status](STATUS.zh-CN.md), [history obligations](HISTORY_RETENTION.md) and
[acceptance queue](ACCEPTANCE_QUEUE.md).
