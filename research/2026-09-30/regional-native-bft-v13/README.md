# Explicit regional BFT ground profile: revision 13

Signed fixture admissions can explicitly authorize four equal validators and
three distinct ordered prepare votes plus three matching commit votes. This
profile binds each vote to native parent history, value, phase and round, retains
prepared-QC locks before releasing commits, and carries highest prepared values
through authenticated next-round proposals. Blocks and finality install in one
native journal commit. Legacy unanimous admissions cannot lower their quorum.
**No monetary value, adopted-network upgrade, mainnet or asset migration.**

The ground campaign runs separate native CLI processes over four stores/signers
per region. With its initial leader offline, three validators certify a view
change and commit; the offline replica catches up through sequential certified
blocks. Actual reviewed wallet payment delivers net 95 to Proxima, then net 93
to Andromeda, with zero Earth calls during remote execution. Contact evidence is
verified/stored before credit; import, local finality and maturity remain distinct.
Duplicate carriage/imports never credit twice. Conservation counts one canonical
history per region, not four copies of each balance. All 12 conservation checks
pass; the legacy three-process TLS value campaign retains its 31 checks.

The eight added native tests include all eight honest initial-prepare partitions
under a deliberately equivocating fixture leader, then recovery with that leader
offline; persistent locks, sealed rounds, exact keyless response recovery, old
backup/latest-head rejection, uncertified block rejection, phase/domain/quorum
checks, write/interruption recovery and certified-conflict quarantine. This is
partial ground evidence, not a complete safety/liveness proof.

All 77 native tests, 26 process/HTTP tests, 59 transport tests and strict all-target
clippy pass in the workspace and a fresh 221-file named-source build. Original
167 adopted source bytes remain unchanged. Rebuilt BFT reports match exactly;
legacy TLS reports match except declared busy-retry counters. Private signer,
replica, caller-head, key, wallet and transport state is excluded.

- [Verification](verification.json)
- [Actual-process BFT value campaign](campaign-report.json)
- [Legacy three-process TLS regression](legacy-tls-report.json)
- [Exact source manifest](source-manifest.json), [source archive](source.tar.gz), [checksums](../regional-native-encrypted-custody-v12/SHA256SUMS)
- [Current mandatory plan status](PLAN_STATUS.zh-CN.md)
- [Native commands](tools/regional-ledger/README.md)
- [Regional finality specification](docs/research/REGIONAL_SIGNER_EPOCHS_V1.md)

## Remaining mandatory implementation and qualification

The message bus is a same-host controller carrying files. Normal relay startup
does not yet run an autonomous BFT pacemaker or validator gossip; relay evidence
and receipts cannot authorize local imports. BFT era handoff currently refuses;
legacy joint handoff is not BFT reconfiguration. Independent operators/custody,
external rollback anchors, sustained fault/partition recovery, full membership
handoff and independent consensus review remain open. Payment channels, full
hardware/cross-device wallet, long-term archive/algorithm eras and physical
interstellar routes are also required. No I1–I12 item is fully qualified.
Historical packages and exact signed source commitments remain unchanged.
