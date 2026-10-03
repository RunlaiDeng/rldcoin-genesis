# Native encrypted wallet custody: ground candidate revision 12

This revision adds OS-random encrypted owner-key creation, native encrypted
signing, complete owner-journal/key backup, and fresh-directory restore with a
separately retained latest head. The loopback wallet unlocks via its local
terminal and saves backups only to a configured private directory. HTTP never
accepts passwords/keys/paths or returns backup contents. Construction and
transport receipts remain separate from signature, debit and recipient credit.
**No monetary value; no mainnet or asset migration.**

Backup preserves every partial approval, original creation and only-owned
pending-input reservations, plus exact head and backup-time native history,
finality, epoch and incident observation. Restore authenticates and replays
before creating its exclusive fresh target, refuses old backups with surviving
latest heads, and never replaces caller-head/pending consent. A durable
RESTORING marker prevents an interrupted target from opening/signing. Exact
retained recovery needs neither key nor password and cannot first-sign.

The fixed domain/purpose-bound envelope uses Argon2id v19 (64 MiB, t=3, p=4,
16-byte salt, 32-byte derived key) and AES-256-GCM (12-byte random nonce,
16-byte tag). Seeds, plaintext/derived keys, KDF memory and AES schedules enable
zeroization. This is a ground configuration, not independent wallet security,
password entropy, guaranteed runtime/OS memory erasure or stellar crypto life.
See the [native command/custody guide](tools/regional-ledger/README.md) and
[current candidate specification](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md).

## Current evidence

All 69 native tests, 24 process/HTTP tests and 59 transport checks pass, with
strict all-target clippy and a fresh 217-file named-source rebuild. The original
167 adopted-source bytes stay unchanged. The rebuilt custody report matches
exactly; the three-process TLS campaign matches except declared busy-retry
counts and checks conservation 31 times. Generated test secrets and encrypted
backups remain private and are excluded from this package.

The actual browser saved an encrypted backup and displayed the separate latest
head, explicitly signed via the encrypted native key and advanced the retained
head. Native replay independently verified the 60-runlai reservation; the old
backup fails with the newer head. The UI cleared its old backup result after
signing. Functional browser/desktop DOM checks pass; screenshot capture did not
complete, so no new visual layout qualification is claimed.

- [Verification](verification.json)
- [Encrypted custody and two actual local payments](custody-report.json)
- [Three-region TLS value and causal relay campaign](campaign-report.json)
- [Actual browser and native replay checks](browser-checks.json)
- [Exact named source](source-manifest.json), [source archive](source.tar.gz), [checksums](SHA256SUMS)
- [Current mandatory plan status](PLAN_STATUS.zh-CN.md)

## Mandatory qualification still open

Same host/controller tests do not prove independent custody/security, external
monotonic rollback anchors, copied-key concurrent safety, cross-device recovery,
reorganization or hardware/full sustained wallet qualification. Independent BFT,
payment channels, long-term archives/cryptographic eras, operators/review,
sustained resource budgets, exact adoption and actual interstellar physical
routes remain required. No I1–I12 item is fully qualified. Historical revision
packages are unchanged; this incompatible revision uses a fresh fixture root.
