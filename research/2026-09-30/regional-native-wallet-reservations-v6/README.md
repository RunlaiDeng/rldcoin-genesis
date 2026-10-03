# Native regional candidate: durable signed commands and pending input budgets

The wallet now persists its exact signed owner command and reserves inputs before
returning any signature. The wallet journal is privately stored, separately
locked, fsynced and atomically replaced. Every CLI view, preparation, signing and
recovery checks the caller's separately retained latest wallet head. Reopening a
complete interrupted commit accepts only one exact verified extension; partial
or incompatible bytes remain preserved and fail closed. Lost-response retries
and command recovery return the original signature without reading a key again.

Wallet `available` excludes pending signed inputs. The raw `ledger.spendable`
amount remains a ledger observation, not a new-payment budget. Records distinguish
pending inclusion, actual local inclusion, consumption by another local command
and expiry before inclusion. Expiry uses the actual local chain height and
native `valid_through` rule, never wall time, transport receipts or remote silence.
**This expires an unincluded owner command, not an already debited export.**
Once an export is included, releasing its wallet reservation cannot refund it or
recreate any input. All signed records remain retained.

A surviving latest caller head rejects an old wallet backup. Persisted creation
and signing observations also reject older/forked node prefixes, era/finality
regression and disappearance of incidents known at those points. Read-only
queries do not themselves save new observation anchors. Joint rollback of every
local state/head or copied-key bypass remains outside this protection.

All 59 native tests (including 16 wallet tests), strict all-target static checks,
eight relay process tests and four wallet process tests pass. The process tests
exercise real signing, persistent reservations, response recovery, separate-head
old-backup refusal, native expiry, authenticated import/maturity and actual local
recipient payment. Unchanged transport files retain the earlier 35-check result.
The [three-ledger campaign](campaign-report.json) still passes default relay,
offline onward payment, a new cyclic return and 31 conservation checks.
Public fixture keys and amounts have no monetary value. This new incompatible
currency root changes neither an adopted network nor mainnet authorization.

## Reproduce and use

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory, use Rust 1.98
or later and install the pinned Python transport dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
python3 -m unittest discover -s tools -p 'test_regional_*.py'
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-contact-fixture --report /absolute/NEW-report.json
```

Create a wallet with `wallet-init --owner PUBLIC_KEY --wallet-dir /absolute/NEW-wallet`
and retain its returned head separately. `wallet-view`, `wallet-prepare`,
`wallet-sign` and `wallet-recover` take `--wallet-dir` and `--expected-wallet-head`.
Review the exact draft and separate commitment before signing. Save the returned
new head; a lost last response can be retried with its previous head and exact
reviewed draft. The sign/recover response contains a `commands` array for the
native block producer. See the [complete command and recovery guide](tools/regional-ledger/README.md),
[ledger/wallet rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).

The complete archive contains 207 named files. All 167 earlier base-source hashes
and commitment remain unchanged; supplemental Rust/Python hashes are recorded
separately. A fresh same-host build passed 59 native and 12 process tests, then
reproduced every semantic campaign field. Busy-retry/helper counters vary with
scheduling. Source/runtime files must remain in the build checkout; readable
supplemental sources are also included. This is not independent qualification.

## Bounds and remaining mandatory work

A wallet retains at most 128 signed commands and an 8 MiB journal; full capacity
refuses new signatures and preserves prior records. Pending reservations rely on
the candidate's append-only local ledger. Qualified fork-choice/reorganization
recovery, complete wallet UI, multi-owner signing, cross-device/independent
monotonic recovery, channels, BFT, real contact adapters, long-term storage/crypto,
independent custody/review and exact signed-release adoption remain open.
Default relay still uses ground directory contacts. Starting a node confers no
reward, issuance or finality right. No private keys, identities, wallet journals,
contact/session files or local node state are published. Prior packages remain unchanged.
