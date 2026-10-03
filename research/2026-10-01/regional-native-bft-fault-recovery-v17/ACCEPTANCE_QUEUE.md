# Next acceptance work

The master plan's mandatory I1–I12 remain incomplete. Revision 17 is one finite
same-host/controller ground fault profile, not a service qualification.

1. Retain the exact 229-file source, all four failed runs, the separately scoped
   recovery and the completed fresh run/cold verifier. Check public bytes against
   this package's checksums. Reproduction starts with the exact stopped revision-16
   cycle described in the README; an initial revision-17-only cycle is not claimed.
2. Continue bounded local fault/resource work: higher offered load, adversarial
   scheduling, longer disconnections, bounded native/BFT history and refusal at
   capacity. Preserve source debits, imports, signer locks and caller heads.
   A temporary signing cap or one successful run is not a liveness proof.
3. Keep complete BFT epoch handoff refused until safe handoff/reconfiguration and
   its native failure/recovery verification exist. Do not lower legacy thresholds.
4. Implement and verify remaining channels, cross-device wallet/reorganization
   custody and recovery, external monotonic protection, cryptographic era changes
   and long-term archive verification against their explicit native obligations.
5. Cross-host and independent operators remain prerequisites. The user currently
   has neither a second host nor an independent operator; continue local work.
   When available, independently exchange literal endpoints and identity/TLS pins,
   run without a shared filesystem, and obtain actual independent custody/security
   and physical-adapter evidence. Same-host processes cannot substitute.

Do not publish private identities, TLS keys/configs, wallet/signing state, caller
heads, recovery archives or native replica data. Deadlines and transport receipts
never refund value. A future mainnet requires a new signed zero-issuance genesis;
retired and test balances never migrate.
