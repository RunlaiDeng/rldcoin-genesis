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
Add authenticated adjacent contacts to `transport/config.json`, then
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
Qualified physical adapters, contact capacity and independent security qualification
remain separate gates.

## IPv4 TCP ground contacts

Normal startup also opens a loopback listener on an automatically assigned port.
Use `--mesh-listen 127.0.0.1:PORT` for a stable local endpoint, or explicitly bind
an available IPv4 interface for an operator-configured network. No firewall,
public exposure or NAT traversal is configured automatically. Configure each
adjacent endpoint and independently pin its transport identity on both sides:

```json
{"contacts":[{"host":"127.0.0.1","peer":"PINNED_NEIGHBOR_NODE_HEX","port":39001}],"format":"RLD-CONTACT-MESH-V1","network":"CURRENCY_HEX","state":"/absolute/private/mesh"}
```

Addresses are literal IPv4 and ports are integers; no DNS, URLs or endpoints from
remote advertisements are followed. `tools/interstellar_tcp.py` uses bounded
length-prefixed canonical signed exchanges. Each request names its recipient and
fresh nonce; the signed reply binds that nonce and exact exchange hash. Custody is
acknowledged only after complete verification and durable storage. A failed or
lost reply keeps the source evidence; duplicate delivery stays idempotent. Socket
waits hold no mesh lock. Persistent batch rotation gives later queued evidence a
turn even when early deliveries fail. Native Rust still determines every credit.

At most two inbound workers and four outbound contacts per tick are admitted.
The outer wire frame is at most 20 MiB plus 4,096 bytes; its exchange remains
within 20 MiB. A three-second local attempt bounds ground connection waits;
it neither expires evidence nor refunds exports and is not a stellar RTT limit.
Local contact observations are process-local history, separate from advertised
routes, destination custody, native acceptance and spendability.

```sh
python3 -m unittest discover -s tools -p 'test_interstellar_*.py' -v
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-tcp-fixture --report /absolute/NEW-tcp-report.json --adapter tcp
```

The TCP campaign uses three actual native processes and loopback sockets with no
shared contact spools. Earth disconnects only after actual neighboring custody;
remote native imports, local payment and onward export then proceed without it.
A new return waits for restored contact. This same-host duplex adapter is signed
but **unencrypted**. Cross-host operation, confidentiality, one-way/radio/BPv7
links, contact schedules, hostile availability and physical routes remain
unqualified. Directory contacts remain available; standalone mesh `run` only
pumps those directories, while the normal native lifecycle runs both adapters.

## CLI

Every invocation requires `--dir`, `--authority` and the exact `--currency` root.
A currency root is checked against the caller's trusted authority and the exact
build's implementation commitment. Region names alone cannot authorize a ledger.

- `init --bootstrap FILE --region LABEL`: verify an offline signed package and
  create an empty store in a new absolute directory.
- `status`: independently replay persisted state and return identity, local
  coins, maturity heights, permanent import IDs, export dependencies and finality.
- `wallet-init --owner PUBLIC_KEY --wallet-dir DIR`: create a new private,
  separately locked wallet journal; retain its returned head outside that directory.
- `wallet-view --wallet-dir DIR --expected-wallet-head HEAD`: report verified
  ledger amounts, currently available funds, reserved inputs and retained signed
  commands. A stale wallet head is rejected rather than displayed as available money.
- `wallet-prepare --file REQUEST --wallet-dir DIR --expected-wallet-head HEAD`:
  select owned eligible, unreserved inputs, calculate explicit change and return
  an unsigned draft plus its separate review commitment and wallet head.
- `wallet-sign --file REVIEWED_DRAFT --review COMMITMENT --key-file PRIVATE_FILE --wallet-dir DIR --expected-wallet-head HEAD`:
  recheck the exact local journal, incidents and draft under the ledger lock, then
  sign and validate using the actual native command rules, then durably record
  the exact command and reserve its inputs before returning any signature.
  The response's `commands` array is for a block producer; signing does not mine.
  Persist the returned new wallet head separately. Exact response-loss retries
  return the retained signature and head without reading a key or signing again.
- `wallet-recover --intent ID --wallet-dir DIR --expected-wallet-head HEAD`:
  recover an exact retained signed command with its current local inclusion state.
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

The current native wallet interface is a verified command layer with persisted
signed-intent reservations; the complete wallet UI, device recovery and external rollback
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

## Pending commands and recovery

Every wallet operation checks the caller's separately retained latest wallet
head. The native CLI takes the ledger lock before the wallet lock. A reviewed
signature is saved with its command, inputs, observation and predecessor head
using private files, fsync and atomic replacement before release. Reopening
recovers a complete interrupted replacement only when it is one exact verified
extension; partial or incompatible bytes remain preserved and fail closed.
An exact lost-response retry or `wallet-recover` uses the retained signature.

`available` excludes inputs of `SIGNED_PENDING_INCLUSION` commands; `ledger.spendable`
is the raw verified ledger amount and is not the wallet's new-payment budget.
Local inclusion changes the record to `INCLUDED_IN_LOCAL_LEDGER`. If another local
command consumes an input, the old command can no longer execute and becomes
`INPUTS_CONSUMED_BY_OTHER_LOCAL_COMMAND`. Only an unincluded command whose next
possible local block is beyond `valid_through` becomes `EXPIRED_BEFORE_INCLUSION`.
The chain head must be at least `valid_through`; wall time, courier deletion,
transport receipts and remote silence never release a reservation.

This expiry applies to an owner command not yet debited into the ledger. An
already included export remains deducted forever under these rules; releasing
its wallet reservation neither refunds the export nor recreates any input.
Native inclusion still rechecks unspent inputs, signatures and height expiry.
All signed records remain retained, including included and expired commands.
At 128 records or 8 MiB the wallet refuses new signatures rather than pruning.

A surviving latest wallet head rejects a restored older wallet directory.
Retained creation/signing observations also reject older/forked node prefixes,
era/finality regression and disappearance of incidents observed at those points.
Read-only queries do not themselves persist new observation anchors. Joint
rollback of the wallet, ledger and every external head, copied-key bypass and
independent monotonic/device recovery remain unqualified. These rules rely on
the candidate's append-only local chain; they do not qualify future fork choice.

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
