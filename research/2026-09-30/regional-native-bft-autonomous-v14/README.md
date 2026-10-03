# Autonomous regional BFT ground runtime: revision 14

Ordinary fixture startup can run its relay and an explicitly admitted validator
scheduler in the same lifecycle. Native Rust authenticates typed proposals,
votes, timeouts, exact certified parents and value; signer locks and caller heads
persist before response release. Carriage does not grant validator authority.
**No monetary value, adopted-network upgrade, mainnet or asset migration.**

Four actual native-started processes use pinned TLS 1.3 along 0--1--2--3.
With initial leader 0 offline, three voters certify a view change and commit
three blocks. The offline replica catches up through actual network evidence.
A reviewed signed payment propagates without debit; all four nodes restart
with separately retained native heads, certify through height 5 and agree on
recipient amount 30 and zero pending reservation. No controller creates votes,
quorums or view certificates, or installs checkpoints. Two-hop carriage is
checked against retained transit signatures. Phase durations and ground bounds
are reported rather than treated as stellar timing promises.

All 80 native, 34 process/HTTP and 61 transport checks, plus strict all-target
clippy, pass in both the workspace and fresh 225-file build. Eight companion
checks include keyless exact-response recovery, unsigned pending recovery,
old-backup/new-head refusal, write-before-sign failure, exact carriage domains,
native queued payment/no debit/tamper refusal, and delayed complete certificate
installation after timeout without a key or new signature, and immediate new-vote queuing despite already enqueued history. Verified next-hop
suppression is ephemeral, periodically reprobes, and preserves all evidence;
lost/invalid replies or failed local custody never suppress retries.

The fresh native three-region controller-carried value regression retains 12
conservation checks (Earth to Proxima net 95, onward to Andromeda net 93 without
Earth calls during remote execution). The separate legacy three-process TLS
campaign retains 31 checks. These are separate from the autonomous one-region
campaign; multi-region autonomous end-to-end qualification remains open.

- [Verification and failure findings](verification.json)
- [Actual autonomous TLS campaign](campaign-report.json)
- [Native three-region BFT value regression](native-bft-value-report.json)
- [Legacy TLS regression](legacy-tls-report.json)
- [Exact source manifest](source-manifest.json), [source archive](source.tar.gz), [checksums](../regional-native-bft-v13/SHA256SUMS)
- [Current mandatory plan status](PLAN_STATUS.zh-CN.md)
- [Configuration and commands](tools/regional-ledger/README.md)
- [Regional finality specification](docs/research/REGIONAL_SIGNER_EPOCHS_V1.md)

The prototype is bounded and controlled on one host. Private signer, replica,
head, key, wallet and transport state is excluded. Original 167 adopted source
files and historical packages remain unchanged. Full BFT epoch handoff refuses;
sustained faults/liveness, multi-region autonomous flow, independent custody and
operators, external monotonic recovery, channels/full wallet, long-term archives
and crypto, exact adoption and real physical routes remain mandatory. No I1--I12
item is fully qualified and no complete protocol/service qualification is claimed.
