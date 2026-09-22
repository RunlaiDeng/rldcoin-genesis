# Operating revisions

The original permanent designation remains byte-for-byte unchanged. Two subsequent founder-signed records bind narrowly scoped operating changes:

- Revision 1 changes heartbeat production from once per minute to once per ten minutes. Status observations refresh every 30 seconds. The initial software-key exception allows fewer than 2,200 scheduled heartbeats at this cadence, below the retained verifier's 4,096-commit local ceiling. Other byte/event/resource bounds still apply and must never be bypassed by deleting history.
- Revision 2 keeps that cadence and changes node peer waits to 30 seconds, witness waits to 10 seconds and witness polling to once per second. The initial two-second peer configuration failed to collect quorum at height 6, so the operator stopped at height 5. The signed revision retains all vote locks and history. It changes launch arguments through the retained lifecycle without changing any core executable, genesis, quorum or witness gate.

The records are `operations-authorization.json` and `operations-authorization-2.json` in the release root. Both use the domain `RLD-M0-OPERATIONS-AUTHORIZATION-V1` plus a zero byte and the same canonical JSON/Ed25519 scheme as the permanent designation. Revision 2 additionally binds revision 1. Every revision preserves the original expiry, zero-value cap and disabled rewards. This is an operating authorization, not a protocol upgrade or independent review.

To verify the current operator, first reconstruct `proof-root` as described in the root README, then:

```sh
cp operations-authorization.json operations-authorization-2.json proof-root/config/
python3 operating-revisions/deploy/permanent-m0.py verify --root proof-root \
  --pin 874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33
python3 operating-revisions/tools/m0-lifecycle/test_permanent_profile.py
```

Python 3 with `cryptography` is required. No private key is needed. `last_full_verification_at` identifies the most recent all-role check; `observed_at` identifies the more frequent node/status observation.
