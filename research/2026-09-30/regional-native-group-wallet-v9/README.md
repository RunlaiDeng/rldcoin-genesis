# Native regional candidate: independent group wallet approvals

Group payments now use separate owner wallets and private keys. Every owner
reviews exact native input ownership/amounts, recipients, refunds, fees, currency,
regions and expiry. Inputs and local refunds are explicit; no group change is
assigned automatically. Each owner durably retains only their own approval and
reserves only their inputs before returning a signature. The normal block
validator still requires every actual input owner in exact order. A partial
command cannot form or enter a block.

`wallet-recover` returns the exact retained contribution without a key.
`wallet-combine --file CONTRIBUTIONS` accepts one command per owner in a JSON
array and rechecks identical intent, all signatures and current native
eligibility. Missing, duplicate, foreign, forged and different-intent approvals
are refused. Combination does not sign, mine or mutate the ledger. Each owner's
journal tracks inclusion of the same intent ID; its retained partial command
remains partial even after complete native inclusion. Unknown other signatures
are not inferred from a local wallet record.

The [actual group payment report](payment-report.json) records two separate
fixture wallets contributing inputs 39 and 60. The exact 99 units pay local fee
1, explicit local refund 1 and gross remote payment 97; destination fee 2 leaves
95 spendable after native import maturity. Missing approval/duplicate approval
and partial mining are rejected without ledger mutation; recovered contributions
combine after CLI restarts. Inclusion never refunds the remote debit. Every
recorded conservation check passes. These are public fixture keys under the
same controller on one machine, not independent operators or live currency.

Four new native tests cover independent reservations/recovery, incomplete block
rejection, forged reviews/retained ownership and amounts, expiry and consumed
peer inputs. All 63 native tests and strict all-target static checks pass, as do
13 process integrations (8 relay, 5 wallet) and 59 transport tests. A fresh
named-source build reproduces every group report field and the semantic fields
of the [three-native-process TLS campaign](campaign-report.json); only busy
retry/helper counts vary. All 31 contact-campaign conservation checks pass.
Earth is unavailable during distant local payment/onward export, with no Earth
CLI call; a new cyclic return requires restored contact and never unlocks the
original debit. Default relay/TLS behavior is retained.

## Reproduce

Verify SHA256SUMS and extract source.tar.gz into a new directory. Use Rust 1.98
or later and Python 3.11 or later with the pinned TLS dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
RLD_GROUP_WALLET_REPORT=/absolute/NEW-group-report.json python3 -m unittest discover -s tools -p 'test_regional_*.py' -v
python3 -m unittest discover -s tools -p 'test_interstellar_*.py' -v
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-fixture --report /absolute/NEW-contact-report.json --adapter tcp
```

See the [wallet/startup guide](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).
The source archive has 209 named files with all 167 base hashes unchanged.
No private key, mesh identity/configuration, wallet/session/signer journal or
node state is published. The new fixture root does not upgrade an adopted
network. Earlier signed source commitments and historical releases remain intact.

## Mandatory qualification still open

This is bounded append-only fixture operation. Complete wallet UI, device
recovery/independent rollback anchors, cross-device group custody and
reorganization recovery remain required, as do BFT, payment channels, long-term
archives/cryptography, independent review/operators/custody and actual signed
release adoption. Cross-host/physical contacts and sustained resource budgets
remain unqualified. TLS certificate expiry and local contact waits never expire
value or refund exports. No I1–I12 completion or actual stellar route is claimed.
