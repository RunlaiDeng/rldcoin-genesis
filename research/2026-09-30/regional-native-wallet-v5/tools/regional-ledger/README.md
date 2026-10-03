# Generic regional ledger candidate

An incompatible, bounded Rust implementation for white paper 1.11's onward and
return value transitions. It runs three native regional ledger stores, replays
signed owner operations and mined blocks, and uses explicitly installed unanimous
checkpoints. **Public fixture keys, no monetary value, no mainnet mode.**

The existing source/destination nodes and their signed genesis commitments are
unchanged. This supplemental candidate is separately built and started. It is
not a qualified regional consensus protocol or a migration path.

This source revision adds [durable signer locks and joint validator epochs](../../docs/research/REGIONAL_SIGNER_EPOCHS_V1.md), retaining the previous incident/quarantine policy. It creates a new fixture root; earlier source/report packages remain historical.

## Reproduce

Rust 1.98 or later is required. From the exact source tree:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
tools/regional-ledger/target/debug/fixture-campaign /absolute/NEW-fixture-directory
```

The campaign starts a separate native CLI process for every operation, using
three on-disk stores. It provides only Earth–Proxima and Proxima–Andromeda
contact transfers. Earth is not invoked while distant local payments and
onward exports execute. Each successful transition and evidence installation
replays all three stores and checks exact conservation. This is a ground
process/restart exercise, not elapsed years, independent owners or real links.

The report contains public currency/source commitments, export IDs, checks and
limitations. Node journals, contact files and other local state are not public
outputs. All signing seeds inside the campaign are deliberately public fixtures:
authority 1; initial validators 2–5, 22–25 and 42–45; new Earth validators 62–65; local owners/miner 10–14. All normal checkpoints use persisted native signer agents; the helper retains latest heads outside their directories. Adversarial conflict injection deliberately bypasses those agents with public fixture keys.

## Default network-node startup

After verifying and initializing a fixture ledger, ordinary startup enables
signed discovery and bounded relay in the same process lifecycle:

```sh
/absolute/rld-regional-ledger-candidate --dir /absolute/ledger --authority AUTHORITY_HEX --currency CURRENCY_HEX
```

A persistent, separate transport identity and queue are initialized or recovered
in the ledger's `transport/` directory. Without real neighbors the node waits;
there is no invented route, central registration or automatic mining reward.
Add authenticated adjacent directory contacts to `transport/config.json`, then
restart the same node. Alternatively provide `--mesh-config /absolute/config.json`.
Only local adjacent contacts are configured; distant routes are learned through
signed advertisements. A wallet-only client is not a full relay node.

Use `--transport-python /absolute/python` with the dependencies in
`tools/interstellar-mesh-requirements.txt`. The Rust launcher replaces itself
with the bounded Python contact runtime; native Rust replays and validates every
ledger application. Both sources must remain available in the build checkout.
`contact-node` remains a compatible explicit alias, but is not required.

Relay service requires no miner or signing key. An explicitly supplied
`--miner PUBLIC_KEY` additionally enables local import block production after
native evidence validation. Without it verified evidence stays pending until a
local block producer fulfills it; storage acknowledgments never credit value.
Normal checkpoints still require separately authorized native signer agents.

Each eligible neighboring path can carry the same signed packet ID, within
per-contact batch/byte bounds and signed hop limits. Permanent packet/import
deduplication preserves value when paths converge. New useful contacts can
extend reach or survive one relay loss; extra identities alone do not establish
consensus security. Full storage refuses new custody and retains existing data.
Default limits are 16 adjacent contacts, 64 learned nodes, 256 retained transport
messages/receipts, 64 MiB state, 16 hops and four application attempts per poll.
Real adapters, contact capacity/fairness and independent security qualification
remain separate gates.

## CLI

Every invocation requires `--dir`, `--authority` and the exact `--currency` root.
A currency root is checked against the caller's trusted authority and the exact
build's implementation commitment. Region names alone cannot authorize a ledger.

- `init --bootstrap FILE --region LABEL`: verify an offline signed package and
  create an empty store in a new absolute directory.
- `status`: independently replay persisted state and return identity, local
  coins, maturity heights, permanent import IDs, export dependencies and finality.
- `wallet-view --owner PUBLIC_KEY`: report currently spendable, immature,
  quarantined and onward-eligible outputs from the independently replayed store.
- `wallet-prepare --file REQUEST`: select owned eligible inputs, calculate explicit
  change and return an unsigned draft plus its separate review commitment.
- `wallet-sign --file REVIEWED_DRAFT --review COMMITMENT --key-file PRIVATE_FILE`:
  recheck the exact local journal, incidents and draft under the ledger lock, then
  sign and validate using the actual native command rules. Returns a command
  array for a block producer; signing neither mines nor reserves inputs.
- `wallet-receipt --file EXPECTATION`: verify the exact currency, source,
  destination, export ID, recipient and net amount against local evidence/import
  history. Report pending evidence, immature import, spendable original output,
  spent original output or quarantine separately. A spent output does not undo
  the import; its new change/payment is shown by `wallet-view`.
- `mine --miner PUBLIC_KEY [--commands FILE]`: verify signed commands, search for
  real fixture PoW and atomically commit one block.
- `statement`: output the actual local history and checkpoint signing statement.
- `finalize --file FILE`: check the active era's four ordered signatures and install
  the exact local checkpoint. Signatures are obtained separately.
- `signer-init --signer-dir DIR --key PUBLIC_KEY`: create a separate locked signer
  journal; retain its returned head outside that directory.
- `sign-checkpoint --signer-dir DIR --key-file FILE --expected-lock HEAD`: persist
  the exact local signing lock before returning an approval and next head.
- `propose-epoch --validators FILE`: construct an unsigned handoff from the exact
  installed closing tip to a different ordered four-key set.
- `sign-handoff --signer-dir DIR --key-file FILE --expected-lock HEAD --file FILE`:
  persist consent and seal the old era; collect approvals from all old/new keys.
- `install-epoch --file FILE`: verify joint consent and install a durable era event.
- `signer-status --signer-dir DIR`: replay local signer state; the displayed head
  is not an independent monotonic rollback anchor.
- `incident --file FILE`: validate and retain an authenticated conflicting
  checkpoint pair without adopting either branch.
- `incidents`: export retained proofs for the next reachable neighbor.
- `recover-incident --file FILE`: restore exactly a guard/index-pinned proof;
  preserve damaged bytes and all quarantines.
- `proof`: output the retained signed checkpoint dependency archive; incident proofs are exported separately.
- `evidence --file FILE`: fully verify and atomically save an archive. This
  installs evidence only; it does not import value or alter local balances.

An authenticated conflict may be retained even while its accompanying value
archive is rejected; no value branch is adopted. At most 16 incident proofs are
retained separately. The persistent guard refuses restart when an observed proof
is missing or capacity prevents retaining it.

A proof archive's order is causal: previous checkpoints and import dependencies
must precede consumers. An incomplete or incompatible contact exchange is
rejected as a whole; the input file is never deleted. A later valid evidence
exchange may be supplied after the missing dependencies arrive.

## Wallet request and review

The current native wallet interface is a verified command layer; the complete
wallet UI, pending-intent reservation, device recovery and external rollback
protection remain mandatory work. It supports one signing owner per request;
the underlying ledger still accepts explicitly combined multi-owner approvals.
Amounts below are integer runlai strings, never floating point or RLD decimals.

```json
{"owner":"OWNER_PUBLIC_KEY","inputs":null,"outputs":[{"owner":"RECIPIENT_PUBLIC_KEY","amount":"30"}],"remote":null,"fee":"1","valid_for_blocks":8}
```

For a remote payment, `remote` is
`{"destination":"EXACT_ADMITTED_REGION_ID","recipient":{"owner":"RECIPIENT_PUBLIC_KEY","amount":"80"},"destination_fee":"2"}`.
The remote amount is the gross source debit; the destination recipient gets
gross minus destination fee. Local fee, explicit outputs and change also count
in source conservation. Only finalized, mature, unaffected inputs are selected
for export; local spending does not require finality of already mature outputs.
Optional `inputs` permits at most 16 ordered unique IDs owned by this wallet.

Save the exact `wallet-prepare` response for review. The response exposes the
intent ID, input total, change, recipients, fees, domains and a local state pin.
Retain the displayed `review_commitment` separately and pass it to `wallet-sign`.
Do not derive approval from an untrusted replacement draft. Any ledger, evidence,
epoch or incident change requires a new preparation and review. A private key file
has shape `{"secret_key":"64_HEX_SEED"}` and owner-only file permissions;
symlinked, public-readable and mismatched keys are rejected. Keys never appear
in drafts or signed commands. The node revalidates commands again at inclusion.
No remote endpoint or returned transport receipt is required for local signing.

Receipt expectations have shape
`{"currency":"CURRENCY_ID","source":"SOURCE_REGION_ID","destination":"LOCAL_REGION_ID","export":"EXPORT_ID","recipient":"RECIPIENT_PUBLIC_KEY","net_amount":"78"}`.
Missing independently verified evidence returns an error; a transport receipt
alone cannot create a wallet credit. Local maturity and onward-export finality
remain separate. These local observations are not external monotonic anchors;
restoring all node state can still defeat local rollback detection.

## Rules and limits

See [the frozen candidate specification](../../docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md).
The fixture campaign issues 300 **runlai units**, not 300 RLD, in three origin
rewards after a zero-allocation genesis. Every other region issues zero.
Split/merge, multiple-owner inputs, explicit change and both local and destination
fees are integer-only. Export inputs require locally finalized creation history;
imported assets require local maturity and finality before onward export. A
return is a new export and import, with a new ID; no timeout or receipt refund
exists. Fees become explicit local outputs and never disappear from accounting.

Per store: 256 blocks, 64 retained snapshots, 4,096 coins/exports/import IDs and
8 MiB journal/evidence; per block 16 commands, per spend 16 inputs/outputs.
Limits reject new work and retain accepted evidence. There is no pruning.

The append-only chain has fixed cheap fixture PoW (one leading zero hash byte),
no timestamps, fork-choice or retargeting. Default node startup now enables the supplemental contact service. Four public
keys sign a monotonic checkpoint; separately locked signing agents persist before
releasing signatures and require caller-retained latest heads. Joint four-old plus
four-new handoffs fence validator eras without changing balances. There are no
BFT view changes or missing-signer liveness guarantees. Authenticated forks,
incompatible joint handoffs and old-era certificates past a closing fence are
durably retained and quarantine new related operations. Repair never unfreezes.
Consensus incident resolution, independent recovery/custody, channels, live wallet,
qualified real adapters, radio/BPv7 integration, independent archives and crypto
algorithm eras remain open. A surviving external latest signer head detects stale
signer backups; restoring all heads/state together or bypassing agents with copied
keys defeats that protection. An old complete ledger journal still replays as old
state without an external latest-state anchor. At most 16 validator handoffs and
128 signer requests are retained. See the new specification for exact assumptions.
Fsync/rename and an exclusive OS lock protect local commits, not hostile local
filesystem writers or arbitrary storage hardware. These remaining gates cannot
be replaced by the campaign's successful result.
