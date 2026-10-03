# Fair complete-envelope reception — revision 33

A bounded ground candidate under the unchanged revision-32 native implementation
`dd1a55df717c0b31cc736cbe6b3aa94efbf31ee9e8395e4e875727901af217d2`. [273 exact source files](source-manifest.json),
source set `55b923889a476710ef5927482e0dc1efc363c4e0b36ec3cd3fe6f5ad634ab2c9`; [source archive](source.tar.gz).
Native/Core code is unchanged. Each campaign uses fresh private fixture roots;
no retired, adopted or failed balances/custody migrate. Public fixture keys and
test value do not authorize a mainnet.

## Reception and native authority

Restarted nodes retain many already authenticated historical envelopes. A stopped
revision-32 diagnostic found about one hundred such packets per receiver, and
two destination custody receipts for current commit votes not yet processed by
native consensus. Those receipts alone granted no finality or value rights.

The unchanged four-item receive batch reserves two slots for BFT envelopes whose
complete byte identity is absent from the native-checked retained message store,
and two fairly rotated slots for repeated history and ordinary contact traffic.
Unused slots are shared. This is scheduling only. Every selected transit and
receipt still authenticates, and every complete envelope still passes full native
verification and dependency synchronization before body deduplication. Altered
proofs on the same body remain new envelopes. No evidence is pruned, capacity
raised, hash adopted as authority or signing/receipt right granted.

The actual native reception regression uses twelve historical envelopes, a new
signed message and a forged certificate on a retained body. The first batch
authenticates all four envelopes, retains the new message and refuses the forged
proof. History subsequently drains while the bad packet remains; original
message bytes, ledger and caller head stay exact. This is not an adversarial
throughput or arbitrary-arrival starvation guarantee.

## Exact selection observation and preserved failure

An earlier fair-receive cycle reached the real native activation at height 4 and
all four replicas at 7, but its controller demanded exactly one height-4 snapshot.
Two replicas retained two authenticated copies of the same closing statement.
That whole cycle remains **failed**, with its [exact source](failed-selection-source.tar.gz),
manifest, report and log retained. It was not restarted or counted as complete.

The corrected observer reads the actual native active proof, matches the exact
currency, region, current epoch, ordered configured new validators, closing height
and transition number, then asks native replay for the proposal at that exact
closing checkpoint. Its statement must match the active proof. Python neither
computes a checkpoint ID nor uses snapshot multiplicity as authority. All
duplicate evidence remains. A native regression refuses other currency, region,
membership, height and epoch intents. Four separate stopped checks on the failed
stores also pass with 2/2/1/1 snapshots and unchanged private files; they remain
diagnostics, not a repaired complete cycle.

## Actual checks and campaigns

**87 process checks actually ran** from the final frozen source. Native/Core code
and the release binary are exact to the preceding fair build. That build,
158 native tests and strict checks are reused under exact source bindings;
they are not newly rerun for this controller change. The earlier 86-check source
and its failure are separately recorded. Source reviews' pending flags describe
their freeze-time state; terminal reports below supply actual outcomes.

The new ordinary twelve-node Earth–Proxima–Andromeda–Earth cycle completed with
four-replica terminal heights 11/4/4. Earth selected the configured disjoint joint
transition, exported at 8 and stopped entirely during the remote import, maturity
and onward stages. Its return imported at 9 and matured at 11; original source
debits, distinct exports and permanent imports remain. Controllers supplied no
consensus votes/quorums, epoch approvals/activation or payment-proof/checkpoint
progress. Separate cold verification replays twelve native prefixes and twelve
original output observations, checks four custody roles and authenticates all
retained envelopes/archives without private-file changes.

The fresh finite joint fault profile and separate stopped cold verifier passed.
It keeps carrier zero offline, cuts both Earth/Proxima ciphertext contact paths,
passes the derived native height-13 missing-leader successor, includes isolated
local payments, restores fixed contacts, uniquely imports and matures the original
net-9 output, then pauses signing and drains complete certificates. All original
phase bounds remain. Duration: 1282.25 seconds; final heights:
{'earth': 16, 'proxima': 21, 'andromeda': 22}. Cold checks cover twelve native prefixes, four
original outputs and four joint custody roles; native conservation is 300=300+0.
This is one finite same-host fixture profile, not sustained Byzantine or
independent qualification. Exact per-phase and envelope/archive counts are in
the run and cold reports.


All artifacts are in `evidence/`, with [log digests](evidence/log-inventory.json).
Previous revision-32 failures retain their exact dated sources and reports at
[revision 32](../regional-native-bft-active-epoch-proof-v32/README.md).

## Reproduction and limits

Verify `SHA256SUMS`, extract source into a fresh absolute directory, build the
locked candidate binaries, and install pinned mesh dependencies in a private
virtual environment. Set `PYTHONPATH` to extracted `tools` and
`RLD_CONTACT_BINARY` to that newly built candidate binary, then run:

```sh
python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history test_regional_bft_joint_epoch test_regional_bft_joint_fault_profile
python tools/regional_bft_joint_cycle_campaign.py --binary /absolute/candidate-binary --root /absolute/NEW-private-cycle --report /absolute/cycle.json
python tools/verify_regional_bft_joint_cycle.py --source /absolute/source-v33 --manifest /absolute/package-v33/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/candidate-binary --root /absolute/STOPPED-private-cycle --report /absolute/cycle-cold.json
```

Only after that cycle stops and its separate cold verifier passes, run the finite
fault profile in a fresh sole-controller private copy:

```sh
python tools/regional_bft_sustained_campaign.py --joint-cycle --runtime-tools /absolute/source-v33/tools --source-manifest /absolute/package-v33/source-manifest.json --cycle-source-manifest /absolute/package-v33/source-manifest.json --cycle-cold-report /absolute/cycle-cold.json --cycle-report /absolute/cycle.json --binary /absolute/candidate-binary --source-root /absolute/STOPPED-private-cycle --root /absolute/NEW-private-fault --report /absolute/fault.json
```

Only after the fault report records a complete success and all processes stop:

```sh
python tools/verify_regional_bft_joint_sustained.py --source /absolute/source-v33 --manifest /absolute/package-v33/source-manifest.json --run-report /absolute/fault.json --binary /absolute/candidate-binary --root /absolute/STOPPED-private-fault --report /absolute/fault-cold.json
```

This separate verifier is success-only and refuses failed runs.
Never restart a source while its copied signing keys are active elsewhere.
Retain phase-600-second/height-24 and all storage/history/wire bounds.

This is same-host, public-fixture work. Independent operators/custody/security,
cross-device latest-state protection, power loss, arbitrary membership, sustained
Byzantine liveness, long history/cryptographic horizons and qualified physical
links remain separate requirements. **I1–I12 and the full project goal remain
open.** Generated keys, wallets, caller/signer/native/mesh/TLS states and images
are private and excluded. Website and forum are unchanged. A future mainnet needs
independent acceptance and a new signed zero-issuance genesis.
