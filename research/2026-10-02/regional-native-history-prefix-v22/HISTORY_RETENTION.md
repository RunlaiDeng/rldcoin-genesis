# Regional native history retention: implementation obligations

The current native candidate is not a long-history ledger. `MAX_BLOCKS=256`,
`MAX_SNAPSHOTS=64`, `MAX_BYTES=8 MiB`, and 4,096 coin/export/import entries are
explicit refusal boundaries. Every snapshot carries the complete regional block
prefix; incoming export evidence carries verified predecessor/dependency closure.
Raising these numbers alone does not satisfy master-plan I2 or I10.

## Current native groundwork

The published revision-18 prefix candidate reuses an exact predecessor's completely
replayed ledger inside one process, bound to the full currency/admission trust
set. It compares the carried block prefix, authenticates incoming certificates
and epochs, and executes every new block through normal native rules. Cold
verification derives the starting ledgers from genesis; no cached ledger is
deserialized as value authority. Block acceptance validates prospective finality
and the complete new ledger before changing either. A failed tail cannot install
an anchor. Preparing epoch authority changes copies only the registry.

This removes duplicate work within the current bounded representation. It does
not provide durable paged history, compact remote value proofs, rollback roots,
history beyond 256 blocks, or a 200,000-block-era acceptance result. A changed
native implementation requires fresh fixture genesis/currency. Retired, adopted
and earlier candidate records retain their exact original source commitments.

## Required storage and proof boundary

The next native representation must separate immutable durable history from its
bounded active replay state. Each history page needs a domain/version, exact
currency and region, ordered height range, predecessor commitment and canonical
record bytes. A manifest must commit to all retained pages, finality/era proofs,
authenticated incidents and permanent import identity commitments. Restoring
from a manifest alone cannot make an unsigned ledger snapshot trustworthy.

Initial verification must replay from the signed zero-allocation genesis or from
a previously fully verified exact prefix protected by a surviving latest-state
anchor. New checkpoint extensions must bind the predecessor's complete state,
history and import commitments. They may execute only their suffix after exact
parent verification; an unverified sender-supplied balance cannot become that
parent. Full owner consent, source issuance/conservation, local maturity, regional
finality, export debit, import uniqueness and transitive incidents remain native
rules. Legacy unanimous regions cannot silently lower their threshold, and a
new storage dialect does not grant BFT reconfiguration or recovery authority.

Remote proof carriage also needs bounded verified dependency access. Splitting
the same unbounded prefix into transport pages without authenticated closure,
resource admission and native reconstruction is insufficient. Missing pages or
unknown delayed cryptographic/era authority must preserve pending value and
refuse acceptance; a receipt or deadline never releases the source export.

## Durable publication and recovery obligations

1. Write and synchronize immutable payloads before making a manifest/head visible.
   Retain interruption residue; do not treat an unverified orphan as an accepted
   page. A response acknowledging custody requires actual retained bytes and
   synchronized file/directory durability.
2. Protect an exact latest native state observation outside the rollback domain.
   Detect missing history, old manifests, disappearance of import tombstones,
   finality/era regression and vanished authenticated incidents. If every archive
   and anchor can roll back together, independent rollback protection is absent.
3. Restore into a fresh private target with an interruption marker, reconstruct
   value and authority, and compare complete roots before opening it. Never
   overwrite an existing caller head, signer reservation or wallet pending review.
4. Quantify bounded active memory, immutable archive bytes/files, source and
   destination proof work, refusal at disk/capacity limits and complete recovery
   costs. Retention may compress exact bytes; it cannot discard unresolved value,
   signer locks, permanent import identities or required historical authority.

## Acceptance still required

Run an actual native history beyond the first declared 200,000-block issuance era
under the applicable issuance rules, with local payments, delayed original
exports/imports, onward/return value and all I=U+T checks. Recover from separately
retained archives; corrupt, omit, reorder and substitute pages, roots, old heads,
finality/era evidence and import commitments. Exercise interrupted writes,
full storage and stale backups. These faults must not create spendable assets or
refund included exports. A fast empty fixture loop alone does not meet this gate.

Same-host testing is local evidence. Independent archive operators, custody,
security review, power-loss storage assumptions and actual physical routes remain
separate prerequisites. No second host or independent operator is currently
available; continue native implementation without claiming those qualifications.

## Supplemental exact shared evidence storage candidate

The companion now stores immutable canonical bytes for distinct complete
evidence snapshots, indexed by their full byte SHA-256. Each original envelope
retains the ordered reference list (including repeated entries), full body,
value/local flag and original canonical digest/size. Reconstruction returns new
objects; the process holds no mutable trusted proof. Before expansion, exact
encoded size must match and remain at most 3 MiB. The combined storage wrapper
still refuses above 32 MiB and at 512 messages; snapshots are not pruned.

`RLD-REGIONAL-BFT-RETENTION-V2` is supplemental storage, not a signed rule or
proof format. Legacy private state refuses unchanged. Every new envelope is
fully authenticated by Rust before retention, and cold startup/verifiers fully
reconstruct and authenticate every retained envelope. Failed disk persistence
keeps exact already-signed responses in the separate caller-head outbox;
restart recovery cannot first-sign. Missing/substituted/orphan bytes, changed
metadata, expansion overflow and forged certificates refuse.

A byte-only diagnostic round-tripped all 2,259 envelopes in the twelve stopped
revision-18 failed stores, preserving bodies, complete evidence, values and
local flags. Maximum inline state was 33,529,748 bytes; prospective exact shared
state was at most 1,628,727 bytes. Private files were unchanged and were not
migrated. This accounting does not prove native authentication, repair the
failed run, qualify the full fault profile or meet the long-history gates.
Fresh source freezing, lifecycle value/fault runs and stopped-state native
authentication remain separate required evidence.

The final 234-file source 5ab9e125172125c34ecd81d811c2f00097a59801d7b326afa017559476c52bc0 completed the fresh cycle and one 653.438-second finite fault profile. Separate cold checks authenticated twelve native stores, four original recipient outputs, 1,898 BFT envelopes and 4,324 transport archives without changing private files. Maximum final BFT state was 1,378,543 bytes under the unchanged 32 MiB limit. This is supplemental storage evidence; none of the native long-history or independent gates above is fulfilled. Frozen documentation retains its pre-run status; terminal reports preserve later outcomes.

## Native paged disk candidate

The default native store now prepares typed immutable snapshot, epoch and contact
objects and sixteen-event pages before publishing its compact journal manifest.
Each object binds its full canonical bytes to the storage domain, currency and
local region. Ordered event pages bind exact event offsets, predecessor page
hashes and before/after local heights. The manifest commits the ordered complete
proof set, incident identities and exact reconstructed native journal bytes.
Cold open reconstructs these bytes and performs the existing full native replay;
a self-consistent storage digest cannot validate a forged certificate or balance.

Archive admission counts old tail versions, referenced and unreferenced residue,
and refuses above 4,096 files / 256 MiB. Referenced objects require exact size,
digest, type and scope; unsafe names, symlinks, hardlinks and permissions refuse.
Missing or partial bytes are not repaired automatically. Retained exact objects
are synchronized again before manifest publication. A failed manifest publication
leaves the previous native head and newly written unaccepted objects retained.

The operator can retain `history-head` outside the rollback domain. `history-check`
checks that exact head under the native OS lock and fully replays current native
value/authority; pending incidents require explicit recovery, not reconciliation
inside the pinned check. An old valid manifest can still replay without a surviving
external latest head. This does not qualify independent anti-rollback custody.

This storage phase preserves the logical 8 MiB, 256-block, 64-snapshot and ledger
index bounds. It does not implement long-history execution, compact remote value
proofs, 200,000-block issuance eras or fresh-target archive recovery. Those remain
required above. Old inline private storage is incompatible and remains preserved;
a new implementation requires fresh signed fixture genesis/currency. Passing prior
revision-19 reports cannot certify this changed native source.

Pinned checks also require every authenticated retained incident to appear in the manifest index. An extra unindexed incident refuses before reconciliation; its proof is retained and cannot be hidden by a passing storage head.

The final 237-file source `1756c85e876dbca24275c77e7d035673d2b3fd4a90c5c67b0cbbbf99cd0d445b` passes 99 native and 52 process/history checks, a new signed fixture cycle, one 723.342-second finite fault profile and separate cold native/custody audits. Twelve replicas each cross two event pages; exact reconstructed replay and separately retained head checks pass with private files unchanged. These observations exercise paging under ordinary BFT startup; they do not qualify long-history execution or independent latest anchors. The public [revision-20 evidence](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-paged-history-v20) preserves earlier failed sources and the additional audit tool field error. The latter stopped before its first native call; corrected cycle/fault audits pass without changing the native source.

## Fresh-target private native history image candidate

The new `RLD-NATIVE-HISTORY-ARCHIVE-V1` implementation addresses bounded ledger
image recovery. It seals under the native lock and a separately retained exact
head; restore authenticates the complete image before target creation and again
after synchronized copying. Inventory digests never replace native signature,
finality, owner/value, permanent import or incident replay. Every retained native
object and damaged-incident residue is carried without pruning. Unknown private
source state, keys, signers, BFT replicas, caller heads, wallet journals, pending
reviews, TLS and transport archives are deliberately outside this ledger image.

Images and restored directories use private files/directories. Fresh targets
only; existing targets are never overwritten or merged. `ARCHIVING` prevents use
of an incomplete image. `RESTORING` prevents all ordinary native entry points
and explicit incident recovery from opening an interrupted target; preserve
that target and select a different fresh path. Unresolved source `journal.next`
also refuses sealing without rewriting evidence. Process-local locks and image
equality checks do not qualify hostile all-state rollback or copied-key custody.

This phase retains the 4096-file / 256-MiB native history capacity, bounded
16-file authenticated incidents and 16-file damaged residue, each at most 8 MiB,
and a combined 4130-file / (520 MiB + 32 byte) image ceiling. Native logical
8-MiB, 256-block and 64-snapshot bounds remain unchanged. It neither extends
history to 200,000 blocks nor restores signer/wallet authority. Power-loss,
independent archives/latest heads, cross-device custody and physical-link gates
remain required. A changed native source needs fresh signed fixture genesis;
revision-20 cycle/fault reports cannot certify it.

The initial ten-test run had nine successes and one incorrect assertion about
the error text for a short forged signature. Preserve that failed log/source.
The corrected test uses a full-length invalid signature, so it exercises native
cryptographic rejection; all ten focused tests and strict all-target checks pass.
Frozen full-source lifecycle and fault-profile results remain separate evidence.

The final 241-file source `4af70053f541a67f967bbcfca3d647c46af663343c34e76d7c2e5d63cee6d258` rebuilds and passes 109 native / 57 process checks and strict clippy. Its fresh cycle passes all fifteen conservation checks and 96/91/86 recipients. Separate stopped checks authenticate twelve native stores/original outputs, 607 BFT envelopes and 1392 transport archives without private writes. All twelve native stores also restore into fresh private directories with exact native heads, value/import/incident state and retained bytes; originals and frozen source remain unchanged. The new full finite fault profile is running and has no terminal pass yet. Revision 21 is not published; revision-20 fault results do not qualify this source.

The 4130-file / (520 MiB + 32 byte) ceiling counts retained native payload
(manifest, guard, history, incidents and damaged residue). The separate canonical
archive index is bounded at 8 MiB; locks and filesystem directory metadata are
not included in the reported retained-native byte count. This clarification
does not change native limits or the frozen source used by the running campaign.

The same frozen source now passes one 583.24-second fresh finite fault profile with actual output 9 imported at height 11 and matured at 13; terminal exit is zero and all owned nodes are stopped. Separate fault cold checks authenticate twelve native stores, four original outputs, 1688 BFT envelopes and 3844 transport archives without private writes. Another twelve stopped native stores restore to fresh private directories with exact native heads/value/imports/incidents and retained bytes, originals unchanged. Together the cycle and fault audits complete 24 same-host private native image restores. No generated archive, signer/wallet/caller state or keys are published/restored; all independent, power-loss, cross-device and long-history qualifications remain open.

Revision 21 source/reports are publicly committed at `dbb9930eb74819b8b2403010baa530eb3b4d6e20`, with 50 exact remote files verified. The independent English production site is at commit `56f5ccd4614a69e36d3b883bb18c651290a50134`, verified READY deployment `dpl_7zErQPk49YHuA3cGwV4V9xUsxUuX`; desktop/mobile visuals and navigation, five public routes and six exact remote source files pass. Images/keys/custody state stay private. This publication does not change any long-history, independent, power-loss, custody or physical qualification boundary above.

## Exact predecessor sharing in native history storage V2

`RLD-NATIVE-HISTORY-MANIFEST-V2` and `RLD-NATIVE-HISTORY-OBJECT-V2`
retain the same complete logical native journal. A first checkpoint is a full
object. A later checkpoint with an exact listed predecessor carries that
predecessor's object digest and byte length, the complete prefix length, the
new blocks and the original complete certificate/era metadata. The signed
statement, consensus serialization, complete snapshot transport and native
value rules are unchanged. The implementation commitment changes, requiring
a fresh signed no-value fixture currency; V1 directories refuse unchanged.

Reconstruction uses only objects already directly listed and reconstructed
earlier in the manifest. It cannot recursively follow references, adopt
orphans, reorder checkpoints or use a future object. Exact object scope,
reference length, predecessor statement, region/currency, prefix height and
new block range are checked. Expanded snapshot bytes must fit the declared
logical journal budget, and the final complete journal commitment must match.
Native signature, BFT/unanimous finality, era, owner, conservation, permanent
import and incident replay still decide validity; self-consistent storage
hashes do not authenticate a forged certificate.

All retained old objects, partial-tail pages and failure residue count against
the original 4096-file/256-MiB archive limit. Logical 8-MiB, 256-block,
64-snapshot and permanent-index bounds remain unchanged. Full expanded memory
state and remote proofs are still bounded and duplicate complete prefixes.
This phase reduces repeated on-disk checkpoint blocks; it does not qualify
200,000-block histories, compact transport proofs, independent archives,
latest-state anti-rollback or stellar cryptographic horizons.

The first frozen disk-prefix candidate exposed an unintended duplicate-checkpoint refusal in complete regression. Exact repeats and independently authenticated equivalent BFT quorum encodings remain valid native evidence. Storage now retains every listed proof and selects the earliest exact predecessor object for deterministic prefix sharing; it does not normalize away native authorization checks. The first full frozen source and failed logs are retained; a seventh focused regression covers exact repeats and forged duplicate rejection. Final frozen qualification is pending.

The final 242-file source passes 116 native / 57 process checks, a fresh 96/91/86 cycle, one 705.36-second finite fault profile, separate cold authentication and 24 private fresh-target ledger restores with exact native state and retained bytes. The 64-checkpoint sample reduces referenced snapshot object bytes by 88.65%; full logical journal bytes match. Initial 87-pass/28-fail duplicate-refusal source/logs remain retained. Disk sharing does not extend full transport, memory, logical/index limits, independent anchors or long-term history qualification.
