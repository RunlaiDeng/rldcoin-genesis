# Ordinary-lifecycle preconfigured joint epochs — revision 30

Fresh signed no-value ground candidate. Under the explicitly signed
`RLD-REGIONAL-BFT-JOINT-EPOCH-FIXTURE-V1` rule, ordinary old three-of-four
consensus selects an exact plan, three original old journals persist fences,
and three fresh new candidate journals approve it. Complete activation then
permits new three-of-four prepare/commit voting. One exact disjoint new set and
its existing pinned carriers are configured in advance. Legacy and all-four
epoch thresholds stay unchanged. No old/adopted value or custody migrates.

Typed era-scoped messages carry complete native authorization before the first
new-era checkpoint. Every received envelope is fully authenticated, including
valid alternate three-signature certificate subsets; retained original proof
bytes survive. Native cold sync installs explicit verified epoch events before
new-era suffixes. Invalid signatures/tails cannot grant ledger or signing rights.

Old voting, new approval and new voting custody have separate caller heads.
Restart first recovers exact retained responses and then compares current heads;
recover-only cannot first-sign. New voting creation needs an exact handoff
already authenticated in its local candidate journal under the retained head,
the installed native closing boundary and a separately persisted creation
observation. Existing unmarked journals refuse; late nonparticipants remain
read-only even when historical boundary evidence arrives first.

## Frozen observations

[268 exact source files](source-manifest.json),
[source archive](source.tar.gz), source set `d14db018bcd42cba1aad629f076c2db9397de0953b7d4689e69f15425cc28e43`.
Native implementation `dee623baa0d39c625a142fa04a6f792342a553cac7d30042997a624c962836e6`.
[Checks](evidence/regional-native-bft-autonomous-epoch-wallet-frozen-checks-20261002.json):
checked release with overflow checks/debug assertions, strict all-target checks,
**158 native / 71 process tests**, including eleven actual native caller recovery
checks. All use the same unchanged reviewed source. Logs retain exact local and
sanitized public digests in the [log inventory](evidence/log-inventory.json).

[Ordinary startup campaign](evidence/regional-native-bft-autonomous-epoch-wallet-frozen-campaign-20261002.json):
four separate native stores on one host; carriers 1–3 alone select the plan at
height 4, exchange three old fences/three new approvals over the ordinary pinned
TLS mesh, install activation and continue to height 7. Missing leaders require
native authenticated view changes. Carrier 0 stays offline through activation;
its old/new private keys are explicitly absent from the configured signing
inputs. It later cold-replays the eras without a key, creating no new voting
journal and making no old or candidate signature. Wallet signing-height review
replays the original ordered block, finality and explicit epoch events through
the same native execution kernel as ordinary storage replay.

A real owner signs a 30-unit payment after activation. Submission gossips while
voting is paused and does not itself debit. All four processes restart with
retained caller heads; three new voters include the payment and all four native
stores cold-replay to height 9, minted 300, recipient 30, no pending owner
reservation. The controller supplies configuration, start/stop and the owner
request; it creates **zero consensus votes/quorums, zero epoch approvals or
activation, and zero checkpoint installation**. Old fences remain in their
original native signing journals.

This short same-host sample is not arbitrary overlapping membership,
sustained Byzantine/network fault liveness, independent operations/custody,
power-loss durability, long history or a physical route. No twelve-node full
fault-profile pass is inherited from another revision. I1–I12 remain open.
Mainnet still needs independently accepted evidence and a new signed
zero-issuance genesis.

Historical source and sanitized failure logs remain separate: a Rust closure
parse error, a controller path-type failure before startup, a telemetry-field
failure after height seven, the late empty-journal behavior, and block-only wallet signing-height replay repaired here.
The failed campaign private roots remain local with pinned inventories;
none is relabeled a pass or migrated. Initial failed unit-test temporary roots
were cleaned by their harness; their logs/source remain, and they provide no
private-state preservation or recovery qualification. Public files exclude all
generated private keys, native/signer/caller/wallet state, transport/TLS state
and restoration images. See [design](DESIGN.md) and [failure observations](evidence/regional-native-bft-autonomous-epoch-failed-observations-20261002.json).

## Reproduce

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v30
tar -xzf source.tar.gz -C /absolute/source-v30
cd /absolute/source-v30
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
RLD_STREAM_TEST_BINARY=/absolute/source-v30/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --lib -- --nocapture
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v30/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history test_regional_bft_joint_epoch
/absolute/private-venv/bin/python tools/regional_bft_autonomous_epoch_campaign.py --binary /absolute/source-v30/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-campaign --report /absolute/campaign.json
```

The retained historical revision-29 checksum inventory stays dated. This package
and root README have a new complete publication inventory. The independent
website and forum are not updated by this source publication.
