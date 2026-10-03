# Autonomous joint epoch followed by an offline three-region payment cycle — revision 31

Fresh signed no-value public fixture on one host. Twelve ordinary node processes
use four native replicas per region and literal pinned TLS neighbors. Earth
selects one preconfigured disjoint validator handoff at height 4, with three old
durable fences and three new approvals. Native activation precedes the first
export. One explicitly keyless carrier creates neither a candidate signature
nor a new voting journal. Legacy thresholds and all original bounds remain.

The actual owner payment then follows Earth → Proxima → Andromeda → Earth.
All Earth processes are stopped during remote import, onward transfer and the
new return export. No Earth native CLI call occurs in that remote phase. After
restart, the distinct return export is imported and matures; the initial debit
is never refunded or released. Net original receipts are 96, 91 and 86. Final
heights are 11/4/4 in all four replicas of each region. Sixteen recorded
conservation observations pass: issued 300 = liquid 300 + in transit 0 at the end.
Transport authentication, queued owner commands, native import, maturity and
current spendability remain distinct.

The controller creates zero consensus votes/quorums, zero epoch approvals or
activation, carries zero payment proofs and installs zero checkpoints. Ordinary
nodes perform consensus and all evidence carriage. This is a finite same-host,
same-controller sample with public fixture keys; it does not qualify arbitrary
overlapping membership, sustained Byzantine/network liveness, independent
custody/operators, power-loss durability, long history or physical routes.
**No full fault-profile run was performed for this revision. I1–I12 stay open.**

## Exact source and verification

[270 release source files](source-manifest.json),
[source archive](source.tar.gz), source set `bf7c247ae5023497df005ea54d98d740edfede475aa118b486999ec44a2432ec`.
Native implementation `dee623baa0d39c625a142fa04a6f792342a553cac7d30042997a624c962836e6`.
[Checks](evidence/regional-native-bft-joint-cycle-frozen-checks-20261002.json):
checked release with overflow checks/debug assertions and **72 newly run process
tests** from the retained 269-file [runtime source](runtime-source-manifest.json) /
[exact runtime archive](runtime-source.tar.gz), including 12 joint recovery/cold-retention checks.
The 270-file release adds the unchanged predecessor design and corrects only the
cold verifier's module documentation; its executable AST and every ordinary
node/Native/Core source byte match the tested runtime. The final release was
rebuilt and separately cold-verified. [Release checks](evidence/regional-native-bft-joint-cycle-release-checks-20261002.json)
record this scoped evidence reuse. Native/Core bytes
exactly equal revision 30: its **158 native tests and strict checks are reused,
not rerun or claimed as new**. The prior checked report is retained and pinned.
See [revision 30](../regional-native-bft-autonomous-joint-epochs-v30/README.md)
for its original exact native source, tests and separately preserved failures.

[Complete campaign](evidence/regional-native-bft-joint-cycle-frozen-campaign-20261002.json)
and [separate stopped cold verification](evidence/regional-native-bft-joint-cycle-frozen-cold-20261002.json):
12 native full replays, 12 historical original-output checks, 980 complete
BFT envelopes and 2282 transport archive records authenticated. All private
file bytes/modes/ownership/link counts remain unchanged. Old fences, candidate
approvals and new voter caller heads are separately checked in all Earth stores;
carrier 0 still has no new custody. No cold check performs first signing,
response recovery, ledger adoption or state installation.

The supplemental cold-retention reader accepts joint storage only under the
explicitly signed joint Admission rule and fully authenticates every complete
retained envelope. Live retention/startup code is unchanged. The release includes the predecessor
design in its original source path and as [DESIGN.md](DESIGN.md). The cold
verifier reads existing signer journals through native status checks; it never
initializes or signs them. [Release source review](evidence/regional-native-bft-joint-cycle-release-source-review-20261002.json)
records the exact documentary changes and unchanged executable code. This grants
no additional runtime qualification. [Log inventory](evidence/log-inventory.json) pins original local
and sanitized public digests.

No generated private keys, native/signer/candidate/voter/caller/wallet state,
mesh identities/configs, TLS custody or restoration images are published. No
old or test value migrates. The website and forum are unchanged by this source
publication. Future mainnet still requires independent acceptance and a new
signed zero-issuance genesis.

## Reproduce

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v31
tar -xzf source.tar.gz -C /absolute/source-v31
cd /absolute/source-v31
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v31/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history test_regional_bft_joint_epoch
/absolute/private-venv/bin/python tools/regional_bft_joint_cycle_campaign.py --binary /absolute/source-v31/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cycle.json
/absolute/private-venv/bin/python tools/verify_regional_bft_joint_cycle.py --source /absolute/source-v31 --manifest /absolute/downloaded-package/source-manifest.json --run-report /absolute/cycle.json --binary /absolute/source-v31/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-cycle --report /absolute/cold.json
```

Keep the source unchanged while running. Every reproduced fixture is new and
has no monetary value. Never upload its private root. The native source remains
bounded; the payment cycle is not long-history or whole-project completion.
