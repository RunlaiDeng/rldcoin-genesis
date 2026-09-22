# Continuing signing authorization — 2026-09-22

The owner explicitly requested signing operation without a fixed expiry. Founder-signed operating revision 5 supersedes the operational stop date with `UNTIL_REVOKED`. The original designation, its expiry, and revisions 1–4 remain unchanged historical records. This is revocable software-key operation, not an assertion that a key, algorithm or host is permanently secure.

The new operator verifies the full signature chain and binds its supervisor program. Every managed role validates its exact installed executable, retains Linux parent-death protection, and watches the signed authorization files and revocation marker. Missing, changed or revoked authorization stops the role. No unsigned environment setting or fabricated future date can enable this mode.

The authoritative record is `config/operations-authorization-5.json`, SHA-256 `6f944037d486415933f32b138f3383f0219a953a0341f82af517d88d4f725e20`. Public mode is `key_authorization_mode: UNTIL_REVOKED`, `software_key_expires_at: null`. The legacy process-metadata expiry slot explicitly contains `UNTIL_REVOKED`, never a date.

The live restart at height 20 retained all 73 state files unchanged. All 24 roles passed the retained verification at 11:25:40 UTC. Nineteen distinct focused tests cover signature/chain bindings, expired historical authorization with a valid continuing successor, actual role launch/stop, revocation, altered records, invalid scope, binary substitution, supervisor death and exact heartbeat recovery. These are agent checks across the owner's hosts, not independent audit.

The encrypted `earth-height20-state-20260922.tar.gz.age` is retained on the owner's Mac and server. Local decryption and all 114 state/config/key checksum entries passed; backup SHA-256 is `d17010136bde11990f11fa7103682e02d8d0a2bde70d0c6ede0a76335dabcbc5`. Combine it with the unchanged base artifact archive; never restore over later history without reconciliation. Public operating programs and authorization records must also be retained alongside the backup.

To stop the current service, use `sudo systemctl stop rldcoin-earth`. To additionally revoke revision 5, create `/home/galaxy/rldcoin-m0/permanent-earth/config/operations-revoked` and stop the service. The marker is intentionally checked even if it is a dangling symlink. Keep it in place to prevent relaunch; resuming after revocation is a separate owner decision. These commands do not delete ledger history or keys.

The fixed 4,096-commit M0 verifier limit and other byte/resource bounds remain enforced. At a ten-minute cadence that count is roughly 28 days of blocks from genesis, potentially less if another resource limit is reached. No fixed authorization expiry does not mean unbounded storage or guaranteed perpetual progress. A qualified continuation/retention implementation is still required.

Rewards remain disabled and the value cap remains zero. Revision 5 does not authorize the proposed PoW consensus transition, alter supply, or allocate coins. The user has separately chosen automatic regional PoW mining with future asynchronous interregional payments; implementation and transition evidence are tracked in the new master plan.

The normal ten-minute scheduler subsequently reached height 21. Full verification completed at 11:37:38 UTC, with zero automatic service restarts; all nine unrelated services remained active. The prior WAL bytes were retained. [Public verification record](https://forum.rldcoin.com/genesis/operating-revisions/revision-5/verification.json).
