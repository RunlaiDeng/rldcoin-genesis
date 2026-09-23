# Regional PoW v1: activation and verification

Validated on 2026-09-23. User direction: automatic mining plus future interstellar peer-to-peer payments. Regional PoW provides the Earth mining/local-transfer path; asynchronous interregional settlement remains future work.

## Identity and authorization

- Original manifest pin: `874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33`.
- Zone: `zone-77bc978af4837a1e7971`.
- Explicit incompatible adoption: `16d2a4d3ba8dff33613a9127ffc7e540347d377066b367097b765e1472d01e02`.
- Regional chain: `dab6756c593608078a7d1f8cbdc8af7f447ffad6c506f6299262a26511ee586a`.
- Complete predecessor: 25 certified heartbeat commits; final root `057df31874f4713b5fed2c5dd4be784bc455e45f94bfc33199111c5e07d48721`.
- Exact predecessor history bytes SHA-256: `1570c5fe119c097034d49a188062c69c9450d55b4f6ba645f66e60d72d34a7f5`.

All four original validator keys signed the distinct-purpose adoption. All belong to one controller. This is **not** an upgrade authorized by the original limited M0 constitution, and the adoption explicitly says so. Each new node must pin it. Original genesis/release/constitution records remain intact. All original managed roles were stopped and the old operating authorization revoked; the successor holds the old exclusive operator lock. The 73 predecessor state files did not change across retirement.

## Qualified implementation

Source commit `5fed7ef`; source manifest SHA-256 `79f1bcdb2827377a98bed7808396b01ab4b453e91b68b09f16cf35dd2debca48`; source tree SHA-256 `659f0de2670f0a42bf3df1a79a13f28af04ad84e8ecfadaafcd031622379ffad`.

- Linux x86-64 binary: `9238004ea5f8a91b622e0c3f456f198f623714981f2503c8509d65f7c7ec866d`.
- macOS arm64 binary: `61b9876af8038c8627d493a0330d070592519855ca4ba815981b36f9b245454c`.
- Rust 1.98.0; locked dependencies.
- Each platform: 14 unit tests + 5 real-process/network tests pass. macOS Clippy all targets passes with warnings denied.
- Tests cover exact supply, authentic work, wide target arithmetic, reward maturity, signed transfers, fee conservation, double spends, shorter/harder fork selection, orphan reward removal, persistence failure, exclusive storage ownership, corruption detection, crash/restart, multi-page fork synchronization, joining-miner announcements and actual HTTP transfer/mining/replay.

The source snapshot and specification were frozen as candidates before the later operational adoption. Their original wording is retained because exact source/rules bytes are bound. Builds are not hermetic or independently reproduced. No independent operator or external audit is implied.

## Difficulty and mining

After stopping all original admission workers, the exact released binary measured 46,670,000 hashes in 15,001 ms: 3,111,125 hashes/second. Initial target is `000000024d057e308112575a85859078c98bba7adb6631fa6388627d2fed7c55`, using `floor(2^256/(rate*600))-1`, bounded by the protocol maximum. There is no personal difficulty/reward exception.

The new service entered running state on 2026-09-22 at 17:11:42 UTC. `rldcoin-earth.service` is enabled, restarts on failure, uses one mining thread, a one-CPU quota, low scheduling priority and a 1 GiB memory limit. The private key is not needed for mining. The original public receiving key is `9ad964496324ede5cc5710e4697730841841a7e8beac453c9e62737f55194c16`.

Initial subsidy is 250,000 RLD; total supply remains 100 billion RLD. Zero coins are allocated at adoption. Coinbase maturity is creation height +100. No fixed signing authorization expiry is applied to mining; an operator can stop the service. The 100,000-block local capacity remains a real boundary.

## Production evidence

At 2026-09-23 02:51:48 UTC, controlled stop/restart retained height 95, tip `0000000197b3e6a67572ee247d2989307ee6f2d3295788b80cd19f1dacee2b1e`, root `58124f93ab1fcfc5df77392a1065b88cea2d93a31a7e607fcd5e8868d3b40d88`, and 17,500,000 RLD. All were immature. 72 retained data files survived; service remained enabled with zero failure restarts. All nine unrelated services remained active.

The Mac verifier independently recomputed, using the same released implementation, the original genesis, complete certified predecessor, and 71 PoW blocks through height 96. It matched the public node’s tip, accumulated work, state root, 17,750,000 RLD balance and exact supply conservation. Both hosts are owner-controlled. These are historical observations, not a current balance feed.

Private encrypted backups were decrypted and checked on the Mac without writing plaintext there:

| Snapshot | Files verified | Ciphertext SHA-256 |
|---|---:|---|
| `earth-m0-terminal-before-pow-20260922.tar.gz.age` | 115 | `1677cdeeb15ffa407c9bf82733a4138a7284a1f03866a2229a7dfefd4a0c2065` |
| `earth-pow-height95-20260923.tar.gz.age` | 84 | `05c4a2edca419368f7ea31c55539488f2d27613a9672b5bab36eda72b03693ef` |

Wallet secret and backup decryption identity stay on the Mac. Public records contain no live operator/wallet secret or private recovery archive. Preserve both the original base recovery archive and new terminal/PoW snapshots. Never resume the retired M0 ledger as a substitute for recovering issued PoW history.

## Public operation and remaining work

- [Release and platform executables](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-pow-v0.3.0).
- [Public records and node guide](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/pow-v1).
- [Live raw status](https://forum.rldcoin.com/v1/pow/status); [website](https://rldcoin.com/network).

Nginx exposes bounded status/balance reads and sync/block/transaction/template submissions. It exposes no signing or administrative interface. Old M0 routes are retired with HTTP 410; complete certified history is retained in the release. Public telemetry reports actual recent hashing, storage health and capacity, and is not a cryptographic verifier.

Local signed payments work in full process fixtures. A consumer wallet, convenient offline signing, a production mature-value transfer, independent operators/review, long-term block retention, authenticated future upgrades and interregional routes remain incomplete. No speculative cross-region transfer or duplicate regional reserve is activated.
