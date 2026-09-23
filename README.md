# Rldcoin

**Rldcoin’s long-term goal is peer-to-peer payments between future human communities across star systems.**

Rldcoin starts with a permanent Earth network and automatic proof-of-work mining. The planned design combines local payments within a region with asynchronous settlement between distant regions. Actual interstellar payment routes are not deployed yet.

[Website](https://rldcoin.com) · [Network status](https://rldcoin.com/network) · [Run a node or mine](pow-v1/NODE-GUIDE.md) · [PoW release](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-pow-v0.3.0) · [Community](https://forum.rldcoin.com/)

## Mine and participate

The `rldpow` node can mine automatically using only your receiving public key. It verifies every block, follows the valid branch with greatest accumulated work, and announces its blocks to configured peers. Your wallet secret stays in your custody.

- Fixed supply: **100,000,000,000 RLD**; one RLD is `10^24` runlai.
- Personal allocation at genesis or PoW adoption: **zero**.
- Initial block subsidy: **250,000 RLD**, plus included fees.
- Target interval: **10 minutes**; actual discovery times vary.
- Reward schedule: each **200,000-block era** distributes half the remaining unissued reserve, using exact integer accounting.
- Reward maturity: a coinbase can be spent in a block at least **100 heights after its creation**.

The launch operator and later participants use the same mining rules. There is no guaranteed share. Early mining before broader participation can concentrate ownership. The launch deployment is currently operated by one owner; wider hash-power distribution and independent review remain work ahead.

Follow the [node guide](pow-v1/NODE-GUIDE.md) to verify the release, connect to the public peer, and start a node. Source review, independent operation, documentation, wallet development, and regional-settlement research are welcome contributions.

## Permanent identity and explicit PoW adoption

The original Earth genesis and its certified heartbeat history remain intact. PoW is an **explicitly incompatible consensus-rule adoption**, not a claim that the original limited M0 upgrade constitution already authorized mining rewards. All four predecessor validator keys signed the new statement; those keys belong to the same controller. Joining nodes explicitly choose and pin the new rules.

The unused service reserves become one unissued PoW reserve. The adoption creates no personal balance and no duplicate supply. Old signing roles are retired at height 25. The first PoW block follows that retained checkpoint.

| Record | Commitment |
|---|---|
| Original manifest pin | `874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33` |
| Zone | `zone-77bc978af4837a1e7971` |
| PoW adoption | `16d2a4d3ba8dff33613a9127ffc7e540347d377066b367097b765e1472d01e02` |
| Regional chain | `dab6756c593608078a7d1f8cbdc8af7f447ffad6c506f6299262a26511ee586a` |
| Last legacy state | `057df31874f4713b5fed2c5dd4be784bc455e45f94bfc33199111c5e07d48721` |

Read the [signed adoption](pow-v1/adoption.json), [complete legacy history](pow-v1/legacy-history.json), [rules](pow-v1/REGIONAL-POW-V1.md), and [qualification record](pow-v1/qualification.json). The original [genesis release](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-genesis-20260922), [permanent designation](permanent-genesis.json), external timestamp, and historical operating revisions are preserved without replacing their assets.

## What has been verified

The current release passed 14 unit tests and five real-process/network tests on both Linux and macOS. They cover actual work, exact issuance, reward maturity, signed transfers, double-spend rejection, greater-work reorganizations, competing-branch synchronization, announcements, crash replay and durable storage.

The [production restart check](pow-v1/restart-verification.json) retained height 95 and its 17,500,000 RLD of mined rewards. A [separate Mac verifier](pow-v1/mac-observer-verification.json) replayed the original genesis, all 25 certified legacy commits and 71 PoW blocks through height 96, confirming 17,750,000 RLD and supply conservation. These are timestamped observations; use live status for current values. Rewards in those observations were still immature.

Both hosts belong to the same owner. These checks are not independent operator review, an external security audit, or proof of deployed interstellar payments. A later [1 RLD mature-value self-transfer](pow-v1/first-mature-payment-20260923.json) was included at Earth height 127; at height 128 the separate owner-controlled Mac observer and local wallet agreed on the receiver's 1 RLD balance and two probabilistic confirmations. This does not demonstrate seconds-scale payment or independent operation.

## Current scope and future regions

Earth supports automatic mining and a signed local transaction API. A local candidate wallet was used for the recorded self-transfer, but a consumer wallet remains in development. PoW confirmation is probabilistic; valid greater-work reorganizations can remove earlier rewards and transfers.

The transaction API may quickly accept a valid transfer as **pending** (`confirmed: false`). A first on-chain confirmation depends on the next selected block: ten minutes is the target interval, not a guaranteed payment time. The 100-block maturity rule applies to newly mined rewards, not every transfer. A separate, prefunded noncustodial payment layer is planned for seconds-scale local payments, but is not implemented or available to users today. See the [roadmap](pow-v1/ROADMAP.md) for the target.

Cross-region transfers are disabled. Their qualification must address source locking, authenticated checkpoints, unique imports, delayed receipts, deep source reorganizations, disconnected delivery, and shared supply budgets. A new region cannot duplicate the 100-billion-RLD reserve. Communication delay cannot be eliminated by consensus.

Mining has no scheduled signing-expiry stop. The owner can stop the node, and ordinary machine failures still require recovery. The initial implementation retains a 100,000-block local index limit, including forks; a qualified retention upgrade is required before that limit is reached.

## Downloads and integrity

Use the **named release source archive** for the full Rust protocol tree. GitHub’s automatic archive of this publication repository contains records rather than the full implementation. Download the checksum file from the same release as your assets; independently obtain the expected network/adoption pins through a trusted channel.

Public endpoints at `https://api.rldcoin.com` include `GET /v1/pow/status`, `GET /v1/pow/balance/{public_key}` and bounded `POST /v1/pow/sync`, `/blocks`, `/transactions`, and `/template`. The community forum does not host the API. No signing or administrative interface is public. The former M0 API is retired; its complete certified history is a release artifact. Telemetry is not an independent cryptographic verifier.

No real wallet private key, operator signing secret, decryption identity or private recovery archive is published. The protocol source is Apache-2.0 licensed.
