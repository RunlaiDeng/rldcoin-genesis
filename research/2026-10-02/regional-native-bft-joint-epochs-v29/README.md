# BFT selected-plan joint epochs — revision 29

Fresh no-value native candidate, separately signed
`RLD-REGIONAL-BFT-JOINT-EPOCH-FIXTURE-V1`. Ordinary old BFT first certifies one
exact `Reconfigure` plan in a block with three prepare and commit votes. Only
that selected plan can collect durable old-journal fences and new candidate
approvals. Activation requires three ordered distinct old and three ordered
distinct fresh new keys. The existing all-four epoch profile, legacy unanimous,
legacy BFT and segmented profiles never silently lower thresholds or adopt this
rule. No old/adopted/test balances or private state migrate.

After selection, every old-era successor signature, including timeouts,
refuses. Activation binds the complete certified selected block, the exact
native-replayed closing checkpoint and new set under the separate
`RLD-BFT-JOINT-EPOCH-V1` / `joint-epoch-handoff-v1` domain. Prior native prepare
locks and highest-QC view changes prevent replacing a prepared plan before
selection. Original old BFT journals persist fences before releasing approvals.
Missing signatures never unseal an old key or refund value. Current new sets
are disjoint and historically unused; arbitrary overlap/reactivation refuses.

Complete owner/value, era, finality and incident authentication remain mandatory.
Activation changes no balances. Local history requires an explicit installed
epoch event. Remote cold replay stages exact verified authority, validates the
whole new suffix, then publishes state; invalid tails publish neither authority
nor ledger progress. All native/evidence/history/archive bounds remain unchanged.

## Exact local results

[263 reviewed files](source-manifest.json), [complete source](source.tar.gz):
`5ce8aa65cc3dd41ca27dab46c83a35b3454c7c5019f7b65c6cd978be257247cc`. Native implementation:
`a62625a12ee8039c600513fe3cf7ca40d5930552febc7abc99462937cd01d155`.

[Frozen checks](evidence/regional-native-bft-joint-frozen-checks-20261002.json):
checked release build, strict all-target checks, **155 native / 60 process
tests**, all from this exact unchanged source. Six added native regressions
cover absent participants, highest-QC competing-plan refusal, preselection
refusal, changed selection/domain, duplicate/under-quorum approvals, unfenced
old timeout refusal, legacy profile refusal, invalid new tail atomicity,
missing local epoch event, real owner value, cold replay and stale backup
refusal under a surviving latest caller head.

[CLI ceremony](evidence/regional-native-bft-joint-cli-campaign-20261002.json):
four separate native stores, **three old durable fences / three new durable
approvals**, actual owner-signed payments before and after activation, all four
tips at height 6 and minted 300. One old and one new signer never first-sign;
the missing old round-zero leader is bypassed through an authenticated
three-vote view change. Exact old fences recover without keys; caller heads
are retained separately. Each CLI operation performs native disk cold replay.
Absence here is **signer-only**: all four native stores still receive
controller-carried complete certificates. Same host/controller, short local
history, no independent or power-loss qualification.

The [native sample](evidence/regional-native-bft-joint-native-sample-20261002.json)
also includes a payment to another actual owner in the selected closing block
and a new-set continuation. Signed value is conserved through activation and
full genesis replay. Ordinary local replay refuses deletion of the epoch event;
an invalid fully signed new tail cannot install staged activation.

No fresh twelve-node value cycle or full fault profile is inherited from
earlier revisions. Individual epoch approvals remain outside ordinary BFT mesh
carriage; config/key switch and ceremony are explicit controller operations.
No autonomous reconfiguration, arbitrary membership, formal Byzantine/network
fault-liveness proof, independent custody, long history or physical route is
qualified. I1–I12 remain mandatory.

The historical directory retains the initial test-compilation source (direct
comparison of a type without equality/debug support) and the next focused
source with three passes and one test-helper failure (non-BFT admissions were
incorrectly opened through a BFT-only helper). Production semantics did not
change in those repairs. Failed private test roots remain retained; no state or
value was migrated. Public archives contain only reviewed source, tools and
sanitized reports/logs. Keys, wallets, native/signer/caller journals, transport,
TLS state and generated restoration images are excluded.

[Design and primary references](DESIGN.md) state the changed rules and scope.
Existing protocol proofs or reference implementations do not qualify this
candidate's membership path. Future mainnet requires independent acceptance
and a newly signed zero-issuance genesis.

## Reproduce

```sh
shasum -a 256 -c SHA256SUMS
mkdir /absolute/source-v29
tar -xzf source.tar.gz -C /absolute/source-v29
cd /absolute/source-v29
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
RLD_STREAM_TEST_BINARY=/absolute/source-v29/tools/regional-ledger/target/release/rld-regional-ledger-candidate cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml --lib -- --nocapture
python3 -m venv /absolute/private-venv
/absolute/private-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v29/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign test_regional_bft_retention test_regional_history test_regional_history_archive test_regional_state_proof test_regional_segmented_history
/absolute/private-venv/bin/python tools/regional_bft_joint_epoch_campaign.py --binary /absolute/source-v29/tools/regional-ledger/target/release/rld-regional-ledger-candidate --root /absolute/NEW-private-ceremony --report /absolute/ceremony.json
```

Keep incomplete activation, original old locks and separately retained heads.
Ground process/response recovery does not prove all-state rollback protection,
copied-key concurrency, power-loss durability or restored signing custody.
