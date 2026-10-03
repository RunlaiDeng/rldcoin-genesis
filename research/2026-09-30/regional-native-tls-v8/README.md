# Native regional candidate: pinned TLS 1.3 contacts

Normal fixture-node startup now defaults to TLS 1.3 IPv4 contacts. Adjacent
endpoints, mesh identities and exact DER certificate SHA-256 hashes must be
independently configured and pinned. There is no public CA/hostname trust,
endpoint discovery from advertisements, TLS 1.2 or plaintext fallback.
The client checks the certificate hash, exact mesh identity/network, self-signature
and ground validity. A fresh signed server challenge binds the mesh request to
its connection. The signed response binds both nonces and the exact exchange.
A captured request cannot be reused on another connection to obtain return data.
Client mesh identity is authenticated inside TLS by this challenge/signature;
this is not TLS client-certificate authentication. No custom encryption is used.

TLS has a separate private key, committed with its certificate in one owner-only,
fsynced private PEM. It never uses wallet/finality keys. Restart preserves the
pair; corrupt, symlinked, overly permissive or mismatched material is refused
and retained. New certificates last 90 days under the ground operator's UTC
clock. Expiry blocks new contact, retaining all messages and value. Renewal,
changed pins, cross-device recovery and delayed revocation need separately
verified operator policy; no automatic trust update is performed. This ground
certificate policy does not qualify stellar cryptographic horizons.

All 59 native tests and strict all-target static checks pass, as do 12 actual
relay/wallet process integrations and 59 transport checks. The latter include
24 actual-socket checks for multi-hop/failover, restart, durable custody, response
loss, capacity/hostile input, fair batches, certificate pins, TLS downgrade and
plaintext refusal, cross-connection replay, validity and private-material failures.
A transparent proxy captured ciphertext while the same packet/receipt was
actually delivered. This is an execution check, not independent cryptographic review.

The [three-native-process TLS campaign](campaign-report.json) uses no shared
transport spools. Earth disconnects only after actual neighboring custody;
remote native imports, local payment and onward export proceed without an
available Earth service or Earth ledger CLI calls. A new cyclic return waits
for restored contact. All 31 conservation checks pass; original debit stays
permanent and transport-valid foreign currency earns storage receipts without
native credit. Public fixture keys and integer runlai have no monetary value.

## Reproduce and configure

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory, use Rust 1.98
or later and Python 3.11 or later with TLS 1.3/OpenSSL and pinned dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
python3 -m unittest discover -s tools -p 'test_interstellar_*.py' -v
python3 -m unittest discover -s tools -p 'test_regional_*.py' -v
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-tls-fixture --report /absolute/NEW-report.json --adapter tcp
```

Ordinary startup needs the fixed authority/currency and no subcommand. It opens
a loopback TLS listener on an automatically assigned port and reports its public
certificate hash/deadline. `--mesh-listen 127.0.0.1:PORT` fixes a local endpoint;
explicit IPv4 interface binding does not configure firewall/public exposure/NAT.
A private canonical adjacent contact has shape
`{"peer":"PINNED_NODE_HEX","host":"127.0.0.1","port":39001,"tls_cert_sha256":"PINNED_CERT_SHA256"}`.
Independently pin both sides; failure sends no application exchange and keeps
source evidence. See the [full startup and wallet guide](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).
Explicit `--mesh-insecure-tcp` permits an unpinned plaintext ground experiment
with signed connection challenges; it rejects pinned peer configurations and
is never a fallback. Directory contacts remain available.

The archive contains 209 named files. A fresh same-host build passed 59 native,
12 process and 59 transport tests and reproduced every semantic campaign field;
only busy-retry/helper counters vary with scheduling. All 167 base-source hashes
and commitment remain unchanged. Source/runtime files stay in the exact build
checkout. This incompatible fixture root does not upgrade an adopted network.
No private TLS/mesh key, identity, contact configuration, wallet/session/signer
journal or node state is published. Earlier source packages remain unchanged.

## Bounds and remaining mandatory work

Two inbound workers, four outbound neighbors per tick, a 20 MiB inner exchange
and outer 20 MiB plus 4,096 bytes bound ground contact admission. A three-second
local connection attempt and 90-day certificate are not stellar RTT or long-term
qualification. Failure/expiry never deletes evidence, removes remote nodes or
refunds an included export. Socket waits hold no mesh lock; persistent batch
rotation and original-evidence retention remain in force. Only durable verified
custody is acknowledged; native Rust independently decides ledger credit.
TLS encrypts each configured hop; relays still read carried evidence. Metadata
and traffic-analysis anonymity are not claimed.

Cross-host operation, independent security/cryptographic review, one-way/radio/
BPv7 adapters, physical contact schedules and adversarial availability remain
unqualified. Full wallet UI/multi-owner/reorganization recovery, payment channels,
BFT, external monotonic anchors, long-term archives/crypto, independent custody/
review and exact signed-release adoption remain mandatory. No I1–I12 completion
or mainnet/physical route authorization is claimed.
