# Fresh Earth testnet — September 30, 2026

This running network contains **worthless test currency and public fixture keys**.
It starts at height zero with an empty inherited history and zero inherited
issuance. Test balances never migrate into a future mainnet.
A mainnet has not launched.

| Identity | Exact value |
| --- | --- |
| Protocol source commitment | `d4fdaf6dbb05d00e1820f585dc7ddeb5f0d10f927b003d4551c0429a92d66b54` |
| Source chain | `e8a8dd66eac5a8fe70816901c6b06035fc92b2193213d8fa0f00d2f10a32438e` |
| Destination chain | `6f952ed6eff0aa16d27bd18ab6c760357a21770a954952fffeb4852537c5363a` |
| Qualification profile | Signed 600-second regional rules; low-difficulty fixture and 10-second mining polling |
| Operation | Linux source/destination; macOS observer and independently replaying wallet, one owner |
| Mainnet/value authorization | None |

[Public source status](https://api.rldcoin.com/v1/testnet/earth/status) ·
[Public destination status](https://api.rldcoin.com/v1/testnet/earth-destination/status) ·
[Acceptance and remaining gaps](ACCEPTANCE.zh-CN.md) ·
[Testnet-to-mainnet path](TEST-TO-MAINNET.zh-CN.md)

## Verified evidence

The exact protocol passed 104 checks on each of macOS and Linux (zero failures,
two ignored). These include research migration regressions; the published fresh
network has no migration record. Signed regional-rule adoption, native PoW,
source/destination execution and process recovery are included.

At source height 964, Linux source and macOS observer had identical chain identity,
tip, work and state root. Each process restarted and retained the same values.
The test wallet passed its release tests, including 1000 durable channel payments,
challenge/settlement, cross-region import/maturity/payment and return verification.
The browser wallet downloaded and restored an encrypted full backup, received
1 test RLD, sent 0.25 plus a 0.000001 test fee, and independently replayed the
selected transfer with a remaining balance of 0.749999.

`evidence/` holds non-sensitive reports. Tests and two hosts under one owner do
not prove independent operation, hardware signing, cross-device rollback
resistance, physical distant routes, compensation funding or mainnet acceptance.
Continuous channel/cross-region operation on this persistent fresh network,
new-parameter capacity/fault qualification and the exact non-test release remain
open. The test wallet is a product candidate.

## Reproduce the exact code

Verify `SHA256SUMS` before extraction. Use a new absolute source directory:

```sh
sha256sum --check SHA256SUMS
mkdir /absolute/new-test-source
tar -xzf source.tar.gz -C /absolute/new-test-source
python3 tools/prepare-source.py --root /absolute/new-test-source --manifest source-manifest.json
cd /absolute/new-test-source
cargo test --release --locked -p rld-pow -p rld-value-successor --lib --test runtime --test migrated_runtime -- --test-threads=2
cargo test --release --locked --manifest-path tools/earth-wallet/Cargo.toml -- --test-threads=2
cargo build --release --locked -p rld-value-successor --bin rld-earth-node --bin rld-earth-destination-node
cargo build --release --locked --manifest-path tools/earth-wallet/Cargo.toml
cargo build --release --locked --manifest-path tools/earth-testnet/Cargo.toml
```

On macOS, use `shasum -a 256 -c SHA256SUMS`. The independent source verifier
checks 184 named inputs and 8,672,435 bytes. Wallet and deployment tools are
supplemental and outside the consensus commitment. Binary hashes depend on the
platform/toolchain; a source hash alone does not attest a binary.

## Join this testnet as a local observer

Create a private directory with `bin/`, `records/` and `data/`. Copy the published
`records/` exactly, copy the two freshly built native binaries into `bin/`, and
write `binary-hashes.json` mapping their filenames to locally verified SHA-256
hashes. `tools/run.py` checks metadata, zero inherited issuance and binary bytes
before native signed-record verification.

Run `tools/peer-bridge.py --region earth --port 48530` on loopback, then:

```sh
python3 tools/run.py --root /absolute/private-testnet --mode observer --peer http://127.0.0.1:48530
```

The public bridge requires the exact testnet chain/source commitment and the
public no-value flags. It strips the gateway annotations from strict native RPC
schemas. Only its **private** status/continuity responses normalize native
`live_rld` to signed adopted mode; its `X-Rld-Network: testnet` header and the
published fixture identity remain explicit. Public API responses always have
`live_rld=false`, `test_only=true`, `has_monetary_value=false` and
`mainnet_authorized=false`. This adapter cannot authorize a mainnet.

For the pinned test wallet, also run the destination bridge on port 48531, place
`rld-earth-wallet` in `bin/`, add its verified binary hash, and use
`tools/wallet-run.py --root /absolute/private-testnet`. The full session link is
printed only locally; never publish it or any wallet backup. Use new test-only
wallet keys and passwords.

`tools/src/main.rs` generates a separate fixture network in a new directory using
known public seeds. Generating another fixture changes its signed chain identity;
use the published records to join this network. The wallet deliberately pins the
published identity and rejects a different or incompatible network.

## Operator deployment

`deploy/` contains the resource-limited source/destination/gateway systemd units,
testnet-only nginx site and its read limits. Adjust only host paths and
install the rate-limit definitions once in nginx's HTTP context. Test nodes use
separate directories and ports. Private recovery archives and keys are excluded
from this directory.

Formal launch follows the acceptance list. Public fixture keys, low-difficulty
history and test balances are never copied into mainnet. A mainnet needs its own
empty genesis, accepted parameters, non-test signing identities and exact release
verification after the applicable acceptance conditions pass.

## Progressive node discovery and multi-hop qualification

The [separate ground mesh prototype](../../research/2026-09-30/mesh/README.md) and [N1–N10 requirements](../../research/2026-09-30/mesh/docs/research/INTERSTELLAR_NODE_MESH_REQUIREMENTS.md) add the Earth–Proxima Centauri–Andromeda connection target. Its 34 checks and three-process ground recovery drill do not change this testnet consensus commitment, enable native default discovery, establish a physical route or authorize a mainnet.
