# Native regional candidate: signed IPv4 TCP contacts

Normal fixture-node startup now includes a bounded IPv4 TCP listener and signed
contact exchanges alongside the directory adapter. Only explicitly configured
literal IPv4 endpoints and independently pinned neighbor identities are used;
remote advertisements cannot supply URLs or executable endpoints. Requests and
replies bind the exact recipient, network, fresh nonce and exchange hash.
Complete verified state is durably saved before custody acknowledgment. Failed,
lost or refused replies retain source evidence. Retried packets stay idempotent.
Socket waits hold no mesh lock; persisted batch rotation prevents later packets
being starved by failed earlier deliveries. Native Rust alone validates credits.

The [three-native-process campaign](campaign-report.json) uses actual loopback
sockets and no shared transport spools. Earth disconnects only after neighboring
custody; remote imports, local payments and onward export then proceed without
Earth. A new cyclic return waits for restored contact. All 31 conservation checks
pass, the original debit remains permanent, and transport-valid foreign-currency
bytes obtain storage receipts without native credit. Relay-only carriers preserve
verified evidence without implicitly mining. Test amounts/keys have no value.

All 59 native tests and strict all-target static checks pass. All 12 relay/wallet
process integrations and 48 transport tests pass, including 13 actual-socket
checks for two-hop delivery, an added alternate route, relay loss, sender/destination
restart, lost acknowledgment, concurrent duplex contacts, input/capacity/write
refusal, bounded workers, malformed input and more than one packet batch.
A fresh same-host build from 209 named files reproduced the tests and every
semantic campaign field. Only busy-retry/helper counters vary with scheduling.
All 167 earlier base-source hashes and commitment remain unchanged. This new
incompatible fixture root neither upgrades an adopted network nor authorizes mainnet.

## Reproduce and configure

Verify `SHA256SUMS`, extract `source.tar.gz` into a new directory, use Rust 1.98
or later and install the pinned Python dependencies:

```sh
cargo test --locked --manifest-path tools/regional-ledger/Cargo.toml
cargo clippy --locked --manifest-path tools/regional-ledger/Cargo.toml --all-targets -- -D warnings
cargo build --locked --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m pip install -r tools/interstellar-mesh-requirements.txt
python3 -m unittest discover -s tools -p 'test_interstellar_*.py' -v
python3 -m unittest discover -s tools -p 'test_regional_*.py' -v
python3 tools/regional_contact_campaign.py --binary "$PWD/tools/regional-ledger/target/debug/rld-regional-ledger-candidate" --root /absolute/NEW-tcp-fixture --report /absolute/NEW-report.json --adapter tcp
```

Ordinary node startup needs the fixed authority and currency root and no
subcommand. It defaults to a loopback listener on an automatically assigned port.
Supply `--mesh-listen 127.0.0.1:PORT` for a stable local endpoint. An operator may
explicitly bind an IPv4 interface, but no firewall/public exposure/NAT setup is
performed. Adjacent contacts in the private canonical configuration have shape
`{"peer":"PINNED_NODE_HEX","host":"127.0.0.1","port":39001}`. Configure and pin
both sides. See the [complete startup, contact and wallet guide](tools/regional-ledger/README.md),
[ledger rules](docs/research/REGIONAL_LEDGER_CANDIDATE_V1.md),
[verification](verification.json) and [current status](PLAN_STATUS.zh-CN.md).
Source/runtime files must remain in the exact build checkout. No private mesh
identity, contact configuration, node state, signing/wallet journal or key is published.

## Bounds and remaining mandatory work

At most two inbound workers and four outbound neighbors per tick are admitted.
The outer frame is at most 20 MiB plus 4,096 bytes; the inner exchange stays within
20 MiB. A three-second local attempt controls ground connection waits. It never
expires stored evidence, deletes remote nodes or refunds an included export,
and is not a stellar RTT qualification. Contact observations are process-local
history, distinct from candidate routes, stored bytes, import and spendability.
Default mesh/native/wallet capacity rules remain in force; full stores preserve
accepted evidence and refuse new work. Wallet reservations still persist exact
signatures before release and support separately retained-head response recovery.

The tested adapter is same-host IPv4, duplex, signed and **unencrypted**.
Cross-host operation, confidentiality, one-way/radio/BPv7 adapters, physical
contact schedules and adversarial availability remain unqualified. Full wallet
UI and multi-owner/reorganization recovery, payment channels, BFT, external
monotonic anchors, long-term archives/crypto, independent custody/review and
exact signed-release adoption remain mandatory. No I1–I12 completion is claimed.
Earlier published packages remain unchanged.
