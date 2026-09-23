# RLD regional proof of work, version 1

Status: implementation candidate; no production activation implied. This specification defines a new, incompatible rule adoption, not an operation of the retained M0 upgrade constitution. The M0 birth, signed records and authenticated heartbeat prefix remain immutable evidence. A node must explicitly pin the new adoption ID as well as the original genesis pin.

## Transition

Only a verified heartbeat-only M0 history is supported. Reconstruct the signed pinned genesis and replay every certified commit through the declared last height. Reject service claims, transfers, reserve releases, membership changes, upgrades or any other command; a richer predecessor requires a separate migration. Bind exact history bytes, final height/root, original network/Zone/currency identity, this specification and the compiled implementation-source commitment. All four current validator keys must sign the sorted, purpose-separated rule-adoption statement. Operating authorizations and a founder-only signature are insufficient.

The statement explicitly declares that the rules are incompatible with the original M0 constitution. An adoption signature is not a historical M0 consensus certificate. Old implementations do not acquire support and must be stopped at the retained checkpoint before new production mining begins. Public observers must choose whether to adopt the new rules. The original network birth is never overwritten or passed off as having contained these rules.

All 10^35 unallocated runlai move from the predecessor's unopened service reserves to the successor's unissued mining reserve. Personal allocation is zero. No existing monetary obligation can be discarded. Identity continuity is established by the authenticated prefix and adoption, not by creating another genesis file with the same display name.

## Blocks and mining

A region advances its own U128 height from the terminal predecessor height. Header bytes have domain `RLD-REGIONAL-POW-HEADER-V1` plus zero, followed by chain ID (32 bytes), parent (32), height (16), timestamp (8), target (32), canonical Ed25519 miner key (32), transaction root (32), resulting UTXO root (32), and nonce (16). Integers use unsigned big-endian bytes. The chain ID commits to typed regional context including the exact adoption, original identity, retained checkpoint, start timestamp and initial target. Block ID is SHA-256(SHA-256(header bytes)); its unsigned big-endian integer must be at most the expected target.

The initial target is bound by the adoption, chosen from a disclosed measured hashing benchmark. Maximum target is `00ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`; minimum target is one. A miner cannot select its difficulty. Target adjustment occurs after each 144-block period using last-minus-first timestamp divided by 143*600 seconds, with elapsed time clamped to one quarter through four times that interval. Multiply in a wide integer before division and clamp to the valid target range. No floating point or saturating amount arithmetic is used.

Block timestamps must exceed the median of up to eleven predecessor times (including the transition time until eleven new blocks are present). Admission rejects timestamps more than two hours ahead of the receiving node's clock; operators need a usable local clock. This is regional timing, not a comparison of clocks on distant planets.

Cumulative work uses the exact integer convention floor((2^256 - 1)/(target + 1)). Select the valid branch with strictly greater cumulative work; retain the current tip on a tie. Recompute the successor state on a branch change; rewards from discarded blocks must disappear. PoW confirmation is probabilistic and must not be labelled irreversible BFT finality.

## Issuance and transactions

Let B=200000 and S=10^35 runlai. After n new PoW blocks, e=floor(n/B), j=n mod B, R=floor(S/2^e), and budget=R-floor(R/2). Cumulative issuance is S-R+floor(budget*j/B); when R=0 it is S. Compute quotient and remainder before multiplication to avoid U128 overflow. The block subsidy is cumulative(n)-cumulative(n-1). The first subsidy is 250000 RLD. No allocation occurs at transition. Unissued reserve plus all UTXOs always equals S.

A coinbase receives the subsidy and all included fees, and matures at its creation height plus 100. Its ID binds chain ID, parent, height, miner and transaction root under the coinbase domain. It has no input and cannot be inserted as a normal transaction. The normal transaction signature binds chain ID, canonical sender key, sorted unique inputs, ordered positive outputs, fee and last valid local height under the transfer domain. Require 1..32 inputs, 1..8 outputs, one owning key per transaction, valid Ed25519 authorization, mature unspent inputs, and exact input=output+fee. Minimum fee is one runlai. Fees are transferred to the miner, never destroyed or newly issued.

Blocks hold at most 128 transactions and 256 KiB of typed JSON. The transaction root hashes their exact typed serialization, including signatures, under the transaction domain. The state root hashes emitted runlai and all sorted unspent objects with owner, amount and maturity. Unknown or duplicate structured fields and noncanonical decimal U128 amounts/heights must be rejected. RPC applies byte and concurrency bounds before expensive decoding or verification.

Validation and durable recording precede publication of a block, new tip or reward. Crash recovery revalidates retained records from the explicit adoption; an incomplete trailing append is not accepted as a block. One process owns the state directory. Peer-provided work totals, state snapshots, balances or boolean success fields are never authoritative.

## Scope and deferred regional transfer

The first implementation is one Earth region. It does not enable interregional transfers or new regional issuance budgets. New regions start without their own duplicate reserve. Export/import, certified source checkpoints, deep-reorganization handling, duplicate-proof rejection, delayed receipts, disconnected delivery and budget transfers require their own qualified protocol. No timeout may simultaneously unlock a source amount already imported elsewhere.

The first in-memory header index has a local 100000-block capacity, and individual frames, transactions and requests have explicit limits. These are disclosed implementation capacity boundaries, not promises of infinite storage. Preserve history and stop at a capacity boundary until a qualified authenticated retention implementation is available.
