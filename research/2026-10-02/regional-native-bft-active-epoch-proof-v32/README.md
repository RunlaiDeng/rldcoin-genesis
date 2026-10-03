# Native active-epoch proof observation — revision 32

A fresh signed no-value ground candidate. The new native implementation identity
requires new fixture genesis/currency; revision-31 and failed fixture stores,
values and signing custody are retained unchanged and never migrated. This is
not an adopted-network upgrade or future mainnet authorization.

Every complete incoming consensus envelope still passes native typed proof,
finality, epoch, owner/value and incident checks before body deduplication.
New certified dependencies still synchronize first. Native `bft-context` now
also exposes `active_epoch_proof`: null until ordered local native journal replay
has actually activated a transition; otherwise its exact retained complete proof
for the current chain epoch. Verified `epochs` evidence can know a future
transition while the local ledger remains in its original epoch.

The companion compares complete canonical proof bytes to that freshly read native
active proof. Only an exact already active proof avoids a redundant proof/pack/
activation path. No Python cache, body/statement/hash match or evidence-membership
claim supplies that decision. Valid different quorum-proof bytes still enter
native activation, preserving original stored bytes. Invalid later envelopes
refuse before deduplication and cannot change ledger/caller heads. New activation
and keyless late catch-up still use native authentication and separate old,
candidate and new custody/head boundaries. No bounds are raised, signed evidence
pruned, first signing/recovery rights granted or state cache adopted.

## Source and actual checks

[273 reviewed files](source-manifest.json), [complete archive](source.tar.gz),
source set `0be0a01f00b6b04c11a7cb4b3012c3b8a2d1857904f1ac921ade72890d49e049`, native implementation
`dd1a55df717c0b31cc736cbe6b3aa94efbf31ee9e8395e4e875727901af217d2`. Native changes are confined to the
read-only main CLI observation and formatting of existing signer-status output;
Core source equals revision 31. The companion and five actual native process
regressions change alongside explicit fault-scope/cold tools.

**158 native tests and 85 process checks actually ran**, with a new locked release
build, format and strict checks. The new cases authenticate repeated complete
activation/carried envelopes, refuse foreign-domain and forged same-body proofs,
retain original head/message bytes, distinguish known from active epochs, retain
native processing for different valid quorum variants, and activate missing
proofs without creating a keyless carrier's voting directory.
[Checks](evidence/regional-native-bft-active-proof-frozen-checks-20261002.json),
[source review](evidence/regional-native-bft-active-proof-source-review-20261002.json).
The source review records pending campaign gates at freeze time; the separate
terminal reports below supply the successful cycle and failed fault outcomes.
This is a bounded work reduction, not a general throughput/liveness benchmark.
[Twelve stopped native observations](evidence/regional-native-bft-active-proof-cold-observation-20261002.json)
also confirm four exact active Earth proofs and eight initial-epoch nulls without
altering any private file or creating keyless voting custody.

## Fresh ordinary cycle and finite fault profile

The [fresh ordinary twelve-node cycle](evidence/regional-native-bft-active-proof-frozen-cycle-20261002.json)
uses preconfigured signed joint admission. Earth selects the plan at height 4,
three old voters retain fences and three new voters retain approvals. Three new
voters continue to height 7; carrier zero never acquires signing custody. The
new-era source export confirms at 8. Earth then stops completely while ordinary
remote nodes perform import, maturity, export and onward carriage. After Earth
returns, the original return output imports at 9 and matures at 11. Regional
terminal replicas agree at 11/4/4; source debits/exports and permanent imports
remain. Controllers generate no consensus votes/quorums, epoch approvals or
activation, and install no checkpoint/payment-proof progress.
[Separate cycle cold checks](evidence/regional-native-bft-active-proof-frozen-cold-20261002.json)
fully replay twelve native prefixes and original output observations, authenticate
every retained envelope/archive and check all four separate joint custody roles.

The [new finite fault profile](evidence/regional-native-bft-active-proof-fault-fresh-20261002.json)
**failed** the original 600-second observation for successor height 13 after the
parent-12 leader went offline. It starts from the stopped, cold-verified new cycle
in a fresh private sole-controller copy; copied-key custody is not independent.
Both Earth/Proxima ciphertext-only relays actually cut their contacts. Three new
voters reached height 12, round 2, but did not finish the next native confirmation
within the bound. This run never restored the contacts or tested recipient
maturity, and is not a passing full fault profile.

Total run, failure observations and cleanup took **763.285 seconds**. Stopped
native replay heights are **{'earth': [11, 12, 12, 12], 'proxima': [18, 18, 18, 18], 'andromeda': [16, 16, 15, 15]}**; the highest compatible certified prefixes
retain 300 = 290 + 10, four exports, three imports and one unresolved export.
The original source debit remains; no timeout refund or import is fabricated.
These heights do not establish all-replica agreement. Owned cleanup and original
stopped-cycle byte preservation passed. Exact source is the same 273-file archive
above. No success-only full-profile cold verifier was run on this failed report.

[Separate stopped diagnostic](evidence/regional-native-bft-active-proof-fault-diagnostic-20261002.json)
fully authenticates 35 current-parent envelopes on the three online Earth stores.
Each has three prepare votes, but only one or two retained commit votes. Private
files and separately retained heads remain exact; no node restart, first signing,
recovery or head adoption occurs. Read timings are sequential same-host cold
observations, not concurrent runtime throughput or proof of a unique root cause.
Carriage scheduling, lock contention and repeated native processing need further
investigation. **This profile remains failed.**

## Preserved failed profiles

Both prior complete-profile attempts remain failed. The first reached recipient
maturity but failed a controller custody read on a native OS lock. Its exact
[source](failed-lock-source.tar.gz), [manifest](failed-lock-source-manifest.json)
and [report](evidence/regional-native-bft-joint-fault-reviewed-fresh-20261002.json)
remain. Read-only retries are limited to explicit read commands and exact native
store-lock refusal, at most eight invocations using each original timeout. All
other failures and exhaustion still refuse; no cached success or signing retry.
[Actual lock regression](evidence/regional-native-bft-joint-read-lock-regression-20261002.json)
retains failed bytes without restarting that fixture.

The second fresh profile timed out recipient maturity. Its exact
[source](failed-maturity-source.tar.gz), [manifest](failed-maturity-source-manifest.json)
and [report](evidence/regional-native-bft-joint-fault-retry-reviewed-fresh-20261002.json)
remain. Four [stopped native checks](evidence/regional-native-bft-joint-fault-retry-recipient-diagnostic-20261002.json)
show the retained output imported at 18, requiring 20, but stopped at 19. It is
accepted and immature, not refunded, lost or spendable. Those old-source failures
are not retroactively passed by the new implementation or a recovery stage.

## Scope and reproduction

Only same-host public fixtures under one controller are demonstrated. One finite
cycle or failed profile does not qualify sustained Byzantine load/faults, arbitrary or
overlapping membership, independent operators/custody, cross-device freshness,
power loss, long history/cryptographic horizons or physical interstellar links.
**I1–I12 and the whole-project goal remain open.** Generated private keys, native,
signer, caller, wallet, mesh/TLS state and images are not published. Website and
forum are unchanged; future mainnet requires independent acceptance and a new
signed zero-issuance genesis. [Log digests](evidence/log-inventory.json).

Verify `SHA256SUMS`, extract `source.tar.gz` into a fresh absolute directory,
build the locked binaries and install pinned mesh dependencies in a private
Python virtual environment. Run the native/strict checks and the same 11 process
test modules used for the recorded 85 checks:

```sh
python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history test_regional_bft_joint_epoch test_regional_bft_joint_fault_profile
```

Set `PYTHONPATH` to the extracted `tools` directory and `RLD_CONTACT_BINARY` to
the newly built candidate binary. Reproduce the ordinary joint cycle using this source
and source manifest following revision-31's process instructions, then cold-check
it with `verify_regional_bft_joint_cycle.py`. Use those exact stopped-cycle reports
and this manifest for the explicit fresh fault profile:

The second command is success-only: run it only after a fresh profile completes
and all its owned processes stop. It must refuse this revision's failed report;
failure diagnostics do not replace that complete qualification.

```sh
python tools/regional_bft_sustained_campaign.py --joint-cycle --runtime-tools /absolute/source-v32/tools --source-manifest /absolute/package-v32/source-manifest.json --cycle-source-manifest /absolute/package-v32/source-manifest.json --cycle-cold-report /absolute/cycle-cold.json --cycle-report /absolute/cycle.json --binary /absolute/source-v32/tools/regional-ledger/target/release/rld-regional-ledger-candidate --source-root /absolute/STOPPED-private-cycle --root /absolute/NEW-private-fault --report /absolute/fault.json
python tools/verify_regional_bft_joint_sustained.py --source /absolute/source-v32 --manifest /absolute/package-v32/source-manifest.json --run-report /absolute/fault.json --binary /absolute/source-v32/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-fault --report /absolute/fault-cold.json
```

Never substitute an old implementation's genesis/currency, source manifest,
private stores or failed report. Keep roots private, stop the original before
copying fixture signing keys, and retain phase-600-second/height-24, message,
payload/archive/history bounds unchanged.
