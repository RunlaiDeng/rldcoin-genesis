# Join the Rldcoin Earth PoW network

Rldcoin is a peer-to-peer transfer system for humanity's interstellar future. This release runs the Earth region: automatic mining and signed local transfers. Cross-region transfers remain disabled.

## Inspect the adoption

The permanent genesis is retained. PoW is an **explicitly incompatible rule adoption**, not an operation authorized by the original limited M0 upgrade constitution. All four predecessor validator keys signed the new purpose-separated statement; they are controlled by the same owner. Each joining node explicitly pins that adoption. No personal balance is allocated at the transition.

- Original manifest pin: `874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33`
- Zone: `zone-77bc978af4837a1e7971`
- Adoption ID: `16d2a4d3ba8dff33613a9127ffc7e540347d377066b367097b765e1472d01e02`
- Regional chain ID: `dab6756c593608078a7d1f8cbdc8af7f447ffad6c506f6299262a26511ee586a`
- Terminal legacy height: `25`

Obtain the expected pins through a channel you trust. Checksums downloaded beside files detect inconsistency, but alone do not authenticate the publisher.

## Download or build

Download the named assets from [earth-pow-v0.3.0](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-pow-v0.3.0):

- `rldpow-linux-x86_64-v0.3.0.tar.gz` — Linux x86-64 executable.
- `rldpow-macos-arm64-v0.3.0.tar.gz` — macOS Apple Silicon executable.
- `rldcoin-pow-network-v1.tar.gz` — original genesis, complete legacy history, signed adoption, rule specification and public evidence.
- `rldcoin-pow-source-v0.3.0.tar.gz` — exact retained source used for the build.
- `SHA256SUMS` — byte checksums of these assets.

Verify the downloaded assets using `sha256sum -c SHA256SUMS` on Linux or `shasum -a 256 -c SHA256SUMS` on macOS. Missing assets will be reported if you download only one platform; the files you use must all match. The original genesis release remains separately available and has not been overwritten.

To build from source with the pinned Rust 1.98 toolchain:

```sh
tar -xzf rldcoin-pow-source-v0.3.0.tar.gz
python3 source/tree/tools/source-evidence/source_snapshot.py verify \
  --snapshot source \
  --manifest-sha256 79f1bcdb2827377a98bed7808396b01ab4b453e91b68b09f16cf35dd2debca48
cd source/tree
cargo test --locked --release -p rld-pow
cargo build --locked --release -p rld-pow
```

The source archive is frozen at the implementation candidate commit. This guide and the signed adoption establish its later operational activation. Source consistency does not establish an independently reproduced or hermetic build.

## Verify and run

Extract your executable archive and the network archive into the same new working directory. They provide `bin/rldpow` and `network/`.

```sh
./bin/rldpow verify \
  --genesis network/genesis-manifest.json \
  --history network/legacy-history.json \
  --adoption network/adoption.json \
  --manifest-pin 874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33 \
  --accept-adoption 16d2a4d3ba8dff33613a9127ffc7e540347d377066b367097b765e1472d01e02

./bin/rldpow run \
  --genesis network/genesis-manifest.json \
  --history network/legacy-history.json \
  --adoption network/adoption.json \
  --manifest-pin 874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33 \
  --accept-adoption 16d2a4d3ba8dff33613a9127ffc7e540347d377066b367097b765e1472d01e02 \
  --data-dir ./earth-data \
  --listen 127.0.0.1:48200 \
  --peer https://forum.rldcoin.com \
  --mine-to YOUR_64_HEX_RECEIVING_PUBLIC_KEY
```

Replace the last value with your own Ed25519 receiving public key. **Never pass a wallet secret key to the miner or a public server.** Omit `--mine-to` to run a verifier without mining. The node verifies incoming blocks locally and automatically announces its selected blocks to configured peers; a joining miner does not need an inbound public port. Multiple explicitly configured peers improve availability, but a list controlled by one owner does not establish independence.

If you need a new key, the retained source includes `cargo run --locked --release -p rld-cli -- keygen --out wallet.json`. Run it only on your trusted local computer with a restrictive `umask 077`. It prints the public key and leaves the secret in the wallet file. Back up the wallet securely. The legacy CLI's transfer commands and web wallet are not PoW transaction clients.

Query the local node:

```sh
curl http://127.0.0.1:48200/v1/pow/status
curl http://127.0.0.1:48200/v1/pow/balance/YOUR_64_HEX_RECEIVING_PUBLIC_KEY
```

Mining starts automatically with `--mine-to`. A continually increasing hash counter is work in progress; only a valid block on the selected chain earns coins. Leave the process running or configure your operating system's service manager for restart after failure and reboot. Stop it normally before moving its data directory.

## Rewards and local transfers

Total supply is fixed at 100 billion RLD; one RLD is 10^24 runlai. The first subsidy is 250,000 RLD. Each 200,000-block era distributes half the remaining unissued reserve using exact integer accounting. Target interval is ten minutes; discovery is random and difficulty adjusts every 144 blocks. Coinbase can be spent in a block at least 100 heights after its creation. Fees are paid to the miner. Discarded branches lose their rewards.

The launch operator and later miners have identical rules. There is no guaranteed founder share. Early mining before broader participation can concentrate ownership. A single operator's deployment is not decentralized security.

The developer API accepts purpose-bound Ed25519 signed transfers at `POST /v1/pow/transactions`. See `REGIONAL-POW-V1.md` and the real-process transfer test in the source for the exact wire types and signing bytes. A consumer wallet and convenient offline transaction preparation remain in development. Do not use the predecessor's transaction format. Pending transactions are not durable confirmed balances and may need resubmission after restart.

## Operation and limits

- PoW confirmation is probabilistic; a valid greater-work branch can reorganize balances.
- The node stores and replays immutable block files. Preserve the full data directory, original pins, genesis, complete legacy history and adoption. A newer verified backup must not be replaced with a stale snapshot merely to restore an old balance.
- Private receiving keys belong in separate custody and backups. Node data alone cannot spend a reward.
- The initial local index is limited to 100,000 blocks, including tracked forks. At capacity it stops accepting new blocks/mining until a qualified retention upgrade is available.
- Current release bounds: 256 KiB per block, 128 transactions per block, 32 inputs and 8 outputs per transaction, 16 configured peers. Keep the default loopback listener unless you intentionally configure a bounded public reverse proxy.
- Mining has no scheduled authorization expiry. The owner can stop the service. No cryptographic algorithm or machine is promised to remain secure or available forever.
- Future regions must share the same total supply. New regional reserves, export/import proofs, delayed receipts, deep-reorganization handling and disconnected routes are not enabled by this release.
