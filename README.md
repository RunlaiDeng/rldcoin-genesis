# Rldcoin public protocol and network records

Development uses a public-fixture testnet with no monetary value. Actual implementation and deployment qualification are reported separately in the [status page](research/2026-10-02/regional-native-bft-fair-receive-v33/STATUS.zh-CN.md).

## Current work

- [Fresh Earth testnet](earth/testnet-20260930/README.md): signed fixtures, reproducible source and wallet qualification, worthless test currency and remaining acceptance gates. Current testnet nodes are under one owner.
- [Progressive node discovery and multi-hop relay](research/2026-09-30/mesh/README.md): the Earth–Proxima Centauri–Andromeda connection model, runnable supplemental ground prototype, 34 focused checks and a three-process interruption/restart drill. Native ledger nodes still use explicit peers; physical stellar routes are not deployed.
- [Master plan](MASTER_PLAN.md): mandatory I1-I12 for disconnected local autonomy, arbitrary-region onward/return value, regional finality, native relay and long-term independent qualification. Passing A-G alone is insufficient.
- [Goal-alignment research package](research/2026-09-30/goal-alignment/README.md): detailed plan/status, honest candidate/model limits, sanitized reports and preserved histories.
- [Website node model](https://rldcoin.com/node-network) and [white paper 1.11](https://rldcoin.com/whitepaper).

## Verification material

[Current testnet fixtures](earth/testnet-20260930/README.md) and [reproducible ground research](research/) are available for technical verification. All current networks have no monetary value; a mainnet has not launched. Obsolete mainnet records, releases and archives are excluded and cannot count toward qualification.

Transport discovery or a signed receipt does not authorize payment. Regional ledgers independently validate source authority, finalized history, unique imports and maturity. Independent operation, key custody, outside review, capacity and physical routes require real evidence. No private keys, wallets, sessions or recovery archives are included. Protocol source is Apache-2.0 licensed.

Use each current package’s named checksums. The current cleanup inventory is [SHA256SUMS.current](SHA256SUMS.current); it identifies reviewed public bytes and grants no ledger, signing or mainnet authority.

## Generic regional value candidate

The [separate native fixture candidate](research/2026-09-30/regional-native-v1/README.md) now executes three regional ledger stores, multiple-source imports, onward exports and new cyclic value returns. Its 15 tests and 52 CLI process calls verify bounded ground behavior and conservation; it does not change the adopted testnet, qualify regional BFT or authorize a mainnet. Source archive, exact manifests and sanitized reports are public.

The [incident-retention revision](research/2026-09-30/regional-native-conflict-v2/README.md) adds authenticated conflicts, dependency quarantine, persistent pending guards and exact proof repair. Its 26 tests and 67 CLI calls pass; unaffected local assets continue, while retained affected assets remain quarantined. Independent BFT/epochs and full protocol qualification remain open.

The [durable signer and epoch revision](research/2026-09-30/regional-native-epochs-v3/README.md)
adds persisted-before-release signing locks, caller-retained head checks and
joint unanimous validator handoffs. All 35 tests and a 128-process campaign pass;
post-handoff value still relays offline without changing currency or balances.
Stale signer backups are rejected only while separate latest pins survive.
BFT liveness, full rollback protection, independent custody and protocol
qualification remain open. Earlier packages remain historical and unchanged.

The [default-relay revision](research/2026-09-30/regional-native-relay-v4/README.md)
enables discovery and bounded relay on normal fixture-node startup, with automatic
native evidence validation and explicitly opted-in import mining. All 43 native,
35 transport and eight integration checks pass; the three-ledger value-return
campaign was reproduced from retained named source. Alternate-path delivery and
incremental neighbor addition are tested ground behavior. Real adapters, wallets,
channels, BFT and independent/long-term qualification remain open.

The [native wallet revision](research/2026-09-30/regional-native-wallet-v5/README.md)
adds reviewed owner signing against fresh replayed state and recipient verification
of domains, amount, import/maturity and spent outputs. All 51 native tests and
10 real-process relay/wallet integration tests pass. Wallet UI, pending-input
reservations, device recovery and full protocol qualification remain open.

The [durable wallet reservation revision](research/2026-09-30/regional-native-wallet-reservations-v6/README.md)
persists signatures before release, excludes pending inputs from new-payment
budgets and recovers exact commands after response loss. Separate surviving heads
reject old wallet backups; retained signing observations reject old node prefixes.
All 59 native and 12 relay/wallet process tests pass. Included exports remain
spent; native expiry applies only to unincluded owner commands. Joint rollback,
fork-choice recovery, complete UI and independent qualification remain open.

The [signed IPv4 TCP contact revision](research/2026-09-30/regional-native-tcp-v7/README.md)
adds actual socket contacts to normal fixture startup. The same-host three-ledger
campaign uses no shared transport spools, continues remote native payment/onward
while Earth is disconnected, and preserves permanent debit through a new return.
All 59 native, 12 process and 48 transport tests pass. This signed duplex adapter
is unencrypted; cross-host/physical links and independent qualification remain open.

The [pinned TLS 1.3 contact revision](research/2026-09-30/regional-native-tls-v8/README.md)
defaults to encrypted contacts with independent certificate pins, signed fresh
connection challenges and no downgrade. All 59 native, 12 process and 59 transport
checks pass; a wire proxy observes ciphertext during actual delivery. The three-ledger
TLS campaign retains offline onward payment, new value return and all 31 conservation
checks. Ninety-day ground certificates never expire assets or refund exports.
Cross-host/physical links, long-term cryptographic horizons and independent security
qualification remain open.

The [independent group wallet revision](research/2026-09-30/regional-native-group-wallet-v9/README.md)
adds separately reviewed/persisted owner approvals, only-own-input reservations,
exact no-key recovery and complete native combination. Partial commands cannot
enter blocks. An actual two-owner remote payment leaves 95 spendable at its
recipient after import maturity. All 63 native, 13 process and 59 transport
checks pass in a fresh named-source build; the TLS/offline value-return campaign
retains all 31 conservation checks. This fixture work does not qualify independent
custody, cross-device/reorganization recovery, full wallet UI or physical routes.

The [local wallet interface revision](research/2026-09-30/regional-native-wallet-app-v10/README.md)
adds explicit browser review/signing, persisted response recovery, reservation-aware
budgets, optional local inclusion and separate recipient stages. An actual browser
payment and native conservation were checked; desktop/mobile screenshots were
visually inspected. All 63 native, 20 process/HTTP and 59 transport tests pass in a
fresh 214-file source build. At that revision, encrypted key backup, proposal construction,
cross-device/reorganization recovery and independent wallet qualification remained
mandatory; this is a no-value fixture interface, not a complete wallet product.

The [interactive group proposal revision](research/2026-09-30/regional-native-group-proposal-v11/README.md)
adds public input selection, explicit payment/refund construction and a bound
absolute expiry so later owners review the same exact intent. The browser
constructs/downloads a proposal, separately signs at heights 5 and 6, combines
retained contributions and includes the payment; native conservation is verified.
All 65 native, 22 process/HTTP and 59 transport checks pass from fresh named
source. Encrypted backup, cross-device/reorganization recovery, independent
qualification and physical links remain mandatory.

The [encrypted wallet custody revision](research/2026-09-30/regional-native-encrypted-custody-v12/README.md)
adds native random encrypted owner keys and complete journal/key backup with
fresh-directory restore and a separately retained latest head. The local wallet
saves private backups, and restored keys complete actual native payments while
retaining pending consent/reservations. All 69 native, 24 process/HTTP and 59
transport checks pass from fresh named source; TLS value conservation is
reproduced 31 times. Independent custody/security, cross-device/reorganization,
all-state rollback, hardware/full wallet and physical route qualification remain
mandatory. No mainnet, migration or complete I1-I12 qualification is claimed.

The [explicit regional BFT ground profile](research/2026-09-30/regional-native-bft-v13/README.md) adds three-vote prepare/commit quorums, persistent locks, authenticated view changes and atomic native finality. Three actual CLI voters progress with an offline initial leader; certified cross-region and onward wallet payments conserve value. Workspace/fresh-source checks pass (77 native, 26 process/HTTP, 59 transport). Autonomous validator networking, full BFT reconfiguration and independent consensus/custody qualification remain mandatory. No complete protocol qualification or mainnet is claimed.

The [autonomous regional BFT ground runtime](research/2026-09-30/regional-native-bft-autonomous-v14/README.md) connects explicitly admitted-validator scheduling and authenticated control carriage to ordinary native startup. Actual pinned TLS nodes progress with an offline initial leader, catch up a replica, restart with retained heads and include a reviewed local payment with equal balances. Fresh-source checks pass (80 native, 34 process/HTTP, 61 transport). Multi-region autonomous value, sustained faults, full BFT reconfiguration and independent custody/operations remain mandatory. No full protocol qualification or mainnet is claimed.

The [autonomous three-region ground value relay](research/2026-09-30/regional-native-bft-multiregion-v15/README.md) completes a same-host twelve-node Earth–Proxima–Andromeda–Earth cycle with all Earth processes stopped during remote execution. Native local certificates, recipient maturity, retained source debit and conservation are verified from workspace and exact frozen source (81 native, 36 process/HTTP, 70 transport checks). Full BFT liveness/reconfiguration, independent custody/operations, long-term qualification and physical routes remain required. No mainnet or complete I1–I12 qualification is claimed.

The [bounded contact archive revision](research/2026-10-01/regional-native-archive-v16/README.md) separately reproduces V3/TCP-V4 from exact frozen source: the twelve-node value cycle, 78 transport and 36 process/HTTP checks, 24 native replays and full cold archive reads pass. Three real SIGKILL boundaries preserve exact custody. Sustained faults/load, power loss, cross-host operation, independent custody and full I1–I12 remain unqualified. Old state and value are not migrated; historical packages are unchanged.

The [fault and retained-payment recovery revision](research/2026-10-01/regional-native-bft-fault-recovery-v17/README.md)
verifies repeated BFT envelopes before deduplication, prepares custody before TLS
connection, and archives completed transport earlier without deleting evidence.
Its exact 229-file source passes 84 transport and 34 process/controller checks,
one 863.055-second fresh twelve-node fault profile, and a separate cold verifier
covering twelve native replicas and 4,506 archived payloads. The 589.121-second
retained-payment recovery is separately scoped, and four earlier failed runs
remain public. Same-host finite results do not qualify sustained BFT liveness,
cross-host/independent custody, physical links or a mainnet.

The [verified native-prefix replay candidate](research/2026-10-01/regional-native-prefix-replay-v18/README.md)
binds reusable replay state to the complete verified trust set and avoids
reexecuting exact retained prefixes. Its new native implementation requires a
fresh fixture genesis. The 230-file source passes 86 native, 84 transport and
34 process/controller checks, a new autonomous value cycle and stopped-state
verification of twelve native stores, twelve historical outputs and 1,472
archived payloads. The subsequent 1,059.417-second full fault profile **failed**
recipient maturity; retained BFT state capacity and contention remain open.
Exact successful and failed reports are preserved. No new full-fault, long-history,
independent or mainnet qualification is claimed.

The [shared-evidence revision 19](research/2026-10-01/regional-native-bft-shared-evidence-v19/README.md) retains exact complete proof bytes once, under unchanged capacity and native authentication rules. Its 234-file source rebuilt and passed 47 process/controller/storage checks, a fresh autonomous value cycle and one 653.438-second finite fault profile. Separate cold verification authenticates all twelve native stores, four original recipient outputs, 1,898 retained control envelopes and 4,324 transport archives. Legacy states and failures remain preserved. This is no-value, same-host/controller evidence; sustained BFT liveness, long native history and independent/physical qualification remain open.

The [native paged-history revision 20](research/2026-10-01/regional-native-paged-history-v20/README.md) reconstructs full journals from immutable objects and sixteen-event pages before normal native replay. Its new signed fixture source passes 99 native / 52 process-history checks, a fresh value cycle and a 723.342-second finite fault profile. Separate cold verification authenticates twelve stores, four original outputs, 1,922 control envelopes and 4,359 transport archives. A stopped native audit checks twelve exact retained heads and two event pages per replica without changing private files. Failed sources and tool observations remain retained. Logical 8 MiB / 256-block / 64-snapshot limits remain unchanged; long-history execution, independent latest anchors and fresh-target restore remain open. No old/test balance migrates or mainnet/physical qualification is implied.

The [private native ledger recovery revision 21](research/2026-10-02/regional-native-history-recovery-v21/README.md) passes 109 native / 57 process-history checks, a new cycle and one 583.24-second finite fault profile. Separate audits restore all twelve stopped cycle stores and twelve fault stores into fresh private directories with exact native heads, value/import/incident replay and unchanged original files. Images carry no keys, signers, wallets or caller state and stay private; actual SIGKILL leaves RESTORING targets closed. Logical bounds, independent anchors, power loss, long history and physical qualification remain separate. Historical revision 20 and failures are retained.

The [native disk-prefix revision 22](research/2026-10-02/regional-native-history-prefix-v22/README.md) passes 116 native / 57 process-history checks, a new cycle and one 705.36-second finite fault profile. Its exact 64-checkpoint sample reduces referenced snapshot objects by 88.65% while reconstructing complete signed native history. Separate cold checks and 24 fresh private ledger image restores pass with originals unchanged. The failed first frozen candidate is retained. Full transport/memory histories and original bounds remain; long-history, independent anchors and physical qualification are open.

The [native proof carriage revision 23](research/2026-10-02/regional-native-proof-carriage-v23/README.md) passes 122 native / 57 process / 85 rerun transport checks, a new cycle, one 560.168-second finite fault profile and 24 private fresh-target ledger restores. Exact evidence and BFT envelope samples shrink 90.34% and 26.14% respectively while cold full native replay remains exact. Typed V2 packing rejects legacy payloads; signed bodies and original bounds remain. Earlier failures are retained. Long-history, state/index scaling and independent/physical qualification remain open.

The [native state-record proof revision 24](research/2026-10-02/regional-native-state-proofs-v24/README.md) passes 128 native / 59 process tests, strict checks, a new cycle, a 539.07-second finite fault profile and 24 private ledger restores. Exact caller-selected certified historical records remain distinct from current spendability and native value execution. A 4,096-entry synthetic absence proof is 2,683 bytes. Full evidence/history and original bounds remain; incremental indexes, long-history execution and independent/physical qualification remain open.

The [bounded native archive replay revision 25](research/2026-10-02/regional-native-stream-replay-v25/README.md) checks 1,032 native blocks and 1,024 actual-owner payments with 256 retained observations. Frozen 133 native / 59 process tests, strict checks, a fresh ordinary-node cycle and 12 private ledger-image audits pass; no fresh full fault profile was run here. This read-only PoW-initial stream does not reconcile incidents, adopt a ledger, extend ordinary-node storage or restore signing custody. Long-history finality/indexes and independent/physical gates remain open.

The [segmented checkpoint and paged ordinary-event revision 26](research/2026-10-02/regional-native-segmented-paged-events-v26/README.md) covers 139 distinct native / 60 frozen process tests, 1,029 ordinary-node blocks with 1,025 signed payments, a 361-block real process return and exact private ledger restoration. A separate new bounded BFT cycle, 762.388-second finite fault profile, cold audits and 24 private ledger-image restores pass. The unanimous and BFT profiles retain distinct authority and history limits; complete proof capacity, BFT/long-history and independent/physical gates remain open. Exact sources and failed observations remain retained; generated private state is excluded.

The [incremental native state-index revision 27](research/2026-10-02/regional-native-incremental-index-v27/README.md) preserves exact V1 roots/proofs and reuses only exact typed records and child pairs. Frozen 145 native / 60 process checks, 1,029-block ordinary signed history, a new twelve-node cycle, cold replay and 12 private ledger restores pass. A synthetic 4,096-record point update uses one leaf/twelve branch hashes. No fresh full fault profile is claimed or inherited. Persistent indexing, complete proof/history scaling and independent/physical gates remain open.

The [BFT unanimous epoch activation revision 28](research/2026-10-02/regional-native-bft-unanimous-epochs-v28/README.md) adds a separately signed all-old/all-new ceremony while ordinary BFT stays three-of-four. 149 native / 60 process checks of the retained exact native/process sources and a separately final-source four-replica actual CLI activation with signed payments before/after pass. Old signer journals remain durably fenced; historical keys and late new journals refuse. This is explicit, same-host controller-carried activation, not fault-tolerant dynamic reconfiguration, autonomous epoch scheduling or a new full fault profile.

The [selected-plan joint BFT epoch revision](research/2026-10-02/regional-native-bft-joint-epochs-v29/README.md)
first certifies one old-set plan, then requires three durable old fences and
three fresh new approvals under a separate signed admission. Exact frozen
source passes 155 native / 60 process checks. A four-store same-host ceremony
keeps one old/new signer absent, handles a missing leader by view change,
preserves signed payments and finishes at height 6. It remains controller-carried;
four native stores still receive complete certificates. Autonomous membership,
arbitrary overlap, full fault liveness, independent custody and I1–I12 remain
open. Earlier all-four and legacy profiles retain their thresholds. The root README at the V29 publication commit and its package are covered by the dated
[revision 29 publication inventory](SHA256SUMS.v29-publication).

The [ordinary-lifecycle preconfigured joint epoch revision](research/2026-10-02/regional-native-bft-autonomous-joint-epochs-v30/README.md)
autonomously selects a plan and exchanges three old fences/three new approvals
under the separate signed joint rule. Exact frozen source passes 158 native /
71 process checks. A pinned-TLS same-host sample completes activation, keyless
late catchup, restart and an actual 30-unit owner payment at height 9 without
controller-created consensus or epoch certificates. New custody needs retained
local handoff participation and independent caller heads. This is one explicit
disjoint configuration; arbitrary membership, sustained fault liveness,
independent custody, long history and I1–I12 remain open. The root README at its V30 commit and that package
are in the dated [revision 30 publication inventory](SHA256SUMS.v30-publication).

The [joint-epoch offline three-region cycle, revision 31](research/2026-10-02/regional-native-bft-joint-offline-cycle-v31/README.md)
combines a preconfigured native autonomous handoff with an actual owner-signed
Earth–Proxima–Andromeda–Earth cycle. All Earth processes stop during the remote
stages. Twelve cold native replays and original-output checks verify the final
11/4/4 heights, retained debit and mature distinct return. Seventy-two process
tests were newly run; unchanged native source reuses revision-30 checks. No new
full fault-profile pass, independent custody, long history or physical route is
claimed. I1–I12 remain open. The root README at its V31 commit and that package are in the dated
[revision 31 inventory](SHA256SUMS.v31-publication).

The [native active-epoch proof candidate, revision 32](research/2026-10-02/regional-native-bft-active-epoch-proof-v32/README.md)
distinguishes verified known evidence from actual native activation and avoids
only exact already-active proof reinstallation after full envelope authentication.
A new signed no-value genesis, 158 native/85 process checks, fresh ordinary
three-region cycle with separate cold verification are recorded. The new finite
joint fault profile failed its missing-leader height-13 deadline; stopped native
conservation and 35 current-parent envelope checks are separate diagnostics.
All three failed profiles retain exact sources/reports and remain failed.
This is not sustained Byzantine liveness, independent custody, long history,
physical links or I1–I12 completion. Its package and the root at the V32 commit are in the dated
[revision 32 inventory](SHA256SUMS.v32-publication).

The [fair complete-envelope reception candidate, revision 33](research/2026-10-02/regional-native-bft-fair-receive-v33/README.md) reserves bounded receive slots for novel BFT envelopes and historical/contact traffic while preserving full authentication. Exact native selection observations retain duplicate checkpoint evidence. The final source passes 87 process checks and a separately cold-verified ordinary cycle; its new finite fault profile is **passed with separate cold verification**. Prior failures remain failed. Native/Core checks are reused under exact source bindings. Independent, long-history, physical and I1–I12 qualification remain open. [Exact revision 33 root/package inventory](SHA256SUMS.v33-publication).
