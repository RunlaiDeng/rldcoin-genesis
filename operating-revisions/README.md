# Operating revisions

The original permanent designation remains byte-for-byte unchanged. Subsequent founder-signed records bind narrowly scoped operating changes:

- Revision 1 changes heartbeat production from once per minute to once per ten minutes. Status observations refresh every 30 seconds. The initial software-key exception allows fewer than 2,200 scheduled heartbeats at this cadence, below the retained verifier's 4,096-commit local ceiling. Other byte/event/resource bounds still apply and must never be bypassed by deleting history.
- Revision 2 keeps that cadence and changes node peer waits to 30 seconds, witness waits to 10 seconds and witness polling to once per second. The initial two-second peer configuration failed to collect quorum at height 6, so the operator stopped at height 5. The signed revision retains all vote locks and history. It changes launch arguments through the retained lifecycle without changing any core executable, genesis, quorum or witness gate.
- Revision 3 fixes the outer node request deadline (previously 10 seconds, shorter than the 30-second peer wait), admits authenticated pending votes at startup, and retries only the same deterministic heartbeat target. Its first recovery finalized height 17 but revealed that post-commit checkpoint synchronization was also required. Its signed record and operator source are retained as an intermediate revision.
- Revision 4 adds that retained semantic checkpoint synchronization before declaring recovery complete. It preserves exact vote locks, parent state, finalized history and the existing full node/signer/witness checks. A lost response does not authorize another block. The service retries failures after 60 seconds without permanently exhausting the previous two-start limit; signature, identity, quorum and fixed-expiry checks remain in force.

The records are `operations-authorization.json` through `operations-authorization-4.json` in the repository root. They use the domain `RLD-M0-OPERATIONS-AUTHORIZATION-V1` plus a zero byte and the same canonical JSON/Ed25519 scheme as the permanent designation. Each successor binds the preceding authorization and operator program. Every revision preserves the original expiry, zero-value cap and disabled rewards. These are operating authorizations, not protocol upgrades or independent reviews. Historical release assets are unchanged.

To verify the current operator, first reconstruct `proof-root` as described in the root README, then:

```sh
cp operations-authorization*.json proof-root/config/
python3 operating-revisions/revision-4/deploy/permanent-m0.py verify --root proof-root \
  --pin 874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33
python3 operating-revisions/revision-4/tools/m0-lifecycle/test_permanent_profile.py
```

Python 3 with `cryptography` is required. No private key is needed. `last_full_verification_at` identifies the most recent all-role check; `observed_at` identifies the more frequent node/status observation.
