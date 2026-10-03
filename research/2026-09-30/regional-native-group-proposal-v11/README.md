# Native regional candidate: interactive group proposals

The local wallet now constructs exact group payment proposals from verified
public native inputs. Users choose 2-16 participants, select up to 16 actual
inputs, and explicitly allocate every local payment/refund, remote gross amount
and fee. Native validation requires exact conservation. There is no automatic
group change or assumed peer consent. Construction/download never signs,
reserves inputs or mines. **Public fixture keys, no monetary value.**

The versioned proposal pins currency, region, full request, exact intent ID and
one absolute local expiry. Another owner reviewing later local history preserves
that expiry and the same intent instead of starting a new relative lifetime.
Every owner rechecks current native eligibility, ownership, maturity/finality,
quarantine and their own private reservations before explicitly signing. The
server refuses changed recipients/intent/domain, stale selection and expired
or overlong proposals. Expiry never reverses an included export.

Public input queries use one locked native snapshot, bounded to 16 ordered unique
owners. They reveal no peer wallet journal. Own known reservations are displayed;
other wallets' private reservations remain unknown and require independent
review. Each owner retains only their own approval and reserves only their own
inputs. Complete combination and normal native block validation still require
all actual owners. Historical releases and signed source commitments remain
intact; this incompatible fixture root upgrades no adopted network.

## Actual verification

All 65 native tests and strict all-target static checks pass, together with 22
native process/HTTP integrations (8 relay, 5 wallet CLI, 9 wallet app) and 59
transport tests. A fresh 214-file source extraction reproduces both group-payment
reports exactly and the semantic TLS contact-campaign result. All 167 base-source
hashes remain unchanged. The contact campaign retains 31 conservation checks;
the interactive proposal campaign retains 11 additional conservation checks.

The [actual proposal campaign](builder-report.json) constructs a request from
inputs 39 and 60, allocates refund 1, local fee 1 and gross remote payment 97;
destination fee 2 leaves 95 mature net units after unique native import. Owners
review at different local heights but sign the same exact intent. Wrong-domain,
changed-content, expired and stale-selection cases cannot create approvals.

The [actual browser flow](browser-checks.json) chooses those inputs and explicit
refund, downloads the bound unsigned proposal, imports it in separate owner
clients, confirms each review checkbox and signs at heights 5 and 6 with fixed
expiry 13. Each client reserves only 39 or 60. Recovered native contribution files
are uploaded to the UI for complete combination and local inclusion. Both native
journals then observe inclusion and zero reservations. Current source accounting
is 300 issued = 203 liquid + 97 pending export. This browser check does not claim
source export finality or recipient import; the separate native/HTTP campaign
verifies checkpoint, import and recipient maturity. Both are same-host,
same-controller public-fixture checks, not independent custody.

## Reproduce

Verify SHA256SUMS and extract source.tar.gz into a new directory. Use Rust 1.98
or later and Python 3.11 or later with pinned TLS dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
RLD_GROUP_WALLET_REPORT=/absolute/NEW-group-report.json RLD_GROUP_PROPOSAL_REPORT=/absolute/NEW-proposal-report.json python3 -m unittest discover -s tools -p 'test_regional_*.py' -v
python3 -m unittest discover -s tools -p 'test_interstellar_*.py' -v
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-fixture --report /absolute/NEW-contact-report.json --adapter tcp
```

See the [wallet/startup and proposal guide](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).
Private keys, mesh identities/configuration, wallet/session/signer journals and
node state are excluded. Relay service and transport acknowledgments remain
separate from ledger/payment authority.

## Mandatory qualification still open

Encrypted key creation/backup, hardware custody, a complete wallet product,
cross-device cooperation, reorganization recovery and independent anti-rollback
and security qualification remain required. BFT, payment channels, long-term
archives/cryptography, independent operators/review/custody, actual adoption,
cross-host/physical adapters and sustained budgets remain open. No complete
I1-I12 qualification, mainnet authorization or actual stellar route is claimed.

Browser actions and desktop DOM geometry were verified. Screenshot capture did not complete; no new visual layout qualification is claimed.
