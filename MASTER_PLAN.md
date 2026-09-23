# Rldcoin master plan v6: automatic mining and future interstellar payments

> Current public roadmap, 2026-09-23. This replaces the [historical v5 public plan](archive/MASTER_PLAN_V5_20260923.md) as the description of work after the explicit Earth PoW adoption. This document does not change signed genesis files, deployed consensus rules, balances, or the fixed supply.

## Purpose

Rldcoin's goal is peer-to-peer payments between future human communities across star systems. Earth is the first permanent region. Each future region should process local transactions without waiting for a distant network, while cross-region ownership transfer uses asynchronously delivered, authenticated evidence. Simulated delay between Earth machines is an engineering test; no real interstellar route exists today.

A node may run an automatic SHA-256d miner using only a receiving public key. The founder and later participants follow the same published rules. There was no personal allocation at genesis or PoW adoption, and no participant is guaranteed 5% of supply. An accepted orphan block or a local hash counter is not spendable income.

## Adopted Earth PoW v1

The [signed adoption](pow-v1/adoption.json) explicitly replaces the final legacy heartbeat checkpoint with incompatible regional PoW rules. It binds the complete predecessor history, implementation and precise transition point. It is not an ordinary upgrade authorized by the old limited M0 upgrader. The original genesis and certified history remain intact. The four predecessor keys had one controller; their signatures do not constitute independent review.

| Property | Current rule |
|---|---|
| Currency | RLD; 1 RLD = 10^24 runlai |
| Maximum supply | 100,000,000,000 RLD, shared by all future regions |
| Personal allocation at adoption | 0 |
| Mining | SHA-256d proof of work; greatest valid accumulated work wins |
| Block target | 600 seconds on Earth; actual discovery varies |
| Initial reward | 250,000 RLD plus included fees |
| Reward eras | Each 200,000 blocks distributes half the remaining unissued reserve |
| Reward maturity | A miner reward can be spent in a block at least 100 heights after creation |
| Transactions | Signed UTXO spends with exact integer accounting and probabilistic confirmation |

The exact [rules](pow-v1/REGIONAL-POW-V1.md), [qualification record](pow-v1/qualification.json), [node guide](pow-v1/NODE-GUIDE.md), and [release](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-pow-v0.3.0) define the adopted implementation. Editing this plan cannot activate a new value rule. A future incompatible successor needs frozen rules and implementation, exact activation, operator adoption, replay and rollback tests, and independent scrutiny.

## Delivery stages and present evidence

| Stage | Acceptance target | Current status |
|---|---|---|
| A — permanent operation | Retain original identity and certified history; supervised restart and recoverable operation | Earth genesis and legacy checkpoint retained; original signer roles retired at the PoW transition. |
| B — PoW and accounting | Real work, bounded difficulty, fork choice, reward, maturity, fees, signatures, double-spend and supply checks | Implemented and exercised in the frozen Earth release. |
| C — node and miner | Durable verification, automatic hashing, peer synchronization, bounded public API and recovery | Running on the Earth host. Mining and storage health are observable at `https://api.rldcoin.com/v1/pow/status`. |
| D — explicit adoption | Replay legacy history; stop old roles; adopt one precise successor; retain public artifacts; earn a real valid block | Executed. [Restart](pow-v1/restart-verification.json), [Mac replay](pow-v1/mac-observer-verification.json) and [qualification](pow-v1/qualification.json) records cover their stated versions. |
| E — local payments | Offline signing, mature-value transfer and independent replay; then a noncustodial, enforceable receipt within P95 3 seconds on the same region, plus wallet/reorg/recovery qualification | A [1 RLD mature-value self-transfer](pow-v1/first-mature-payment-20260923.json) was included at Earth height 127. At height 128, the receiver had 1 RLD and the payment had two probabilistic confirmations on owner-controlled nodes. A complete consumer wallet and seconds-scale payment layer are still absent. |
| F — asynchronous regional value | Source lock or permanent debit, authenticated checkpoint and proof delivery, exactly one destination import, delayed receipt, shared-supply and deep-reorg safety | Delay-tolerant transport and isolated value models are candidates only. Mainnet cross-region transfers remain disabled. |
| G — open and lasting operation | Independent operators and miners, security/economic review, sustainable storage and upgrades, resilient custody and eventual real distant deployment | Not qualified; the active Earth deployment and Mac observer still have one owner. |

Old P0 and P1 results apply to the exact earlier candidate and zero-value permanent-genesis scopes. They do not automatically qualify PoW v1, independent participation or the E–G value capabilities.

## Local payment speed

The 600-second figure is a target *block interval*, not a fixed transfer time. `accepted: true, confirmed: false` means a node has a pending transaction. A selected block gives a probabilistic confirmation; a stronger valid branch can remove it. The 100-block maturity rule applies to newly mined rewards, not to ordinary transfer outputs.

The local daily-payment target is a receiver-verifiable, enforceable receipt within P95 three seconds when both parties are online and the noncustodial payment channel has already been funded. It requires consensus-recognized escrow, safe unilateral close and contest, durable wallet state, monitoring, two independently controlled nodes, failure tests and measured latency. Candidate channel code is not an adopted mainnet funding path. The real self-transfer above establishes ordinary on-chain value movement only; it does not meet the seconds target.

## Cross-region and interstellar settlement

Long-distance links can be delayed or disconnected. A courier receipt or copied transaction is not proof that value was safely removed from the source. The intended path is source debit or lock, authenticated proof under an accepted source checkpoint, unique destination import, then an asynchronous return receipt. No timeout may restore source spendability while the destination might still import. A new region must not copy Earth's 100-billion-RLD reserve.

Qualification must cover duplicated and reordered messages, partitions, lost receipts, source and destination reorganizations before and after import, checkpoint trust, recovery and global supply accounting. Two Earth machines can test delivery and delay, but cannot prove a real interstellar link. The current PoW v1 node rejects cross-region value operations.

## Long-term release boundary

The current network has one controlling owner. Public code, a live PID, local tests, owner-controlled Mac replay and this plan do not establish independent operator security. Stage G needs third-party nodes and mining, reproducible releases, external review, storage retention before the 100,000-block index limit, wallet custody recovery, and a governed upgrade path. These are open requirements, not claims about deployed features.

The [public roadmap](pow-v1/ROADMAP.md) and this plan state current capabilities. The immutable genesis and release assets remain historical evidence; future status updates should identify the exact software, chain height, block or transaction, and confirmation depth observed.
