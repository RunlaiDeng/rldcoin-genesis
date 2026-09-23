# Rldcoin Earth Genesis

**A peer-to-peer transfer system for humanity's interstellar future.**

This repository publishes the permanent Earth genesis and its verification materials. The initial network finalizes value-free heartbeats. It has one controlling owner, no personal genesis allocation, no active service rewards, and no enabled value transfers. It is the permanent mainnet identity, not a disposable development network.

- Manifest pin: `874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33`
- Zone: `zone-77bc978af4837a1e7971`
- Profile: `P1_REMOTE_ZERO_VALUE_V1`
- Fixed supply: **100,000,000,000 RLD** (`10^35 runlai`; `1 RLD = 10^24 runlai`).
- Initial reserves: startup services 1%, continuity services 9%, demand matching 90%; spendable balance **0**.
- Current signing authorization: **no fixed expiry, until revoked** under signed operating revision 5. The original dated exception remains in the historical designation.
- [Live identity and status](https://forum.rldcoin.com/genesis/) · [Release downloads](https://github.com/RunlaiDeng/rldcoin-genesis/releases/tag/earth-genesis-20260922)

## Participation and rewards

Rldcoin is being built for community participation. Contributors can inspect the source and genesis records, report issues, improve documentation, and help develop and verify the protocol. Join the [community forum](https://forum.rldcoin.com/) to discuss the work and its next milestones.

The protocol design pays for verified services from fixed reserves under shared rules, with no personal genesis allocation or reserved founder share. Admission work regulates access; service verification determines rewards, and verified contribution determines validation eligibility. These are separate mechanisms. Service rewards are not yet enabled on the permanent Earth network; activation requires the contribution and security milestones described in the published plan.

## Verify the record

Download the release assets. The repository and HTTPS site retain the small records, while the release also provides the complete runtime source and Linux executables.

Use the checksum file shipped with the same release when verifying its downloaded archives. The repository's current `SHA256SUMS` also covers updated documentation and operating revisions; the original release checksum list is retained as `SHA256SUMS.genesis-release-20260922`. Published genesis release assets have not been replaced.

1. Check the assets against `SHA256SUMS` (use `sha256sum -c SHA256SUMS`, or `shasum -a 256 -c SHA256SUMS` on macOS). The checksums establish file integrity; obtain the expected genesis pin through an independently trusted channel.
2. Extract the Linux archive on Linux. Verify the founder-signed genesis using `bin/rld-genesis verify --manifest genesis-manifest.json`. Confirm the exact manifest pin above. The raw file SHA-256, `33e0669d4b411baae9e25a72167a20e8a9124aac96e26168449735c3364d659e`, differs from this canonical manifest pin.
3. Verify the external RFC 3161 timestamp:

   ```sh
   openssl ts -verify -data genesis-manifest.json -in timestamp/genesis.tsr \
     -CAfile timestamp/cacert.pem -untrusted timestamp/tsa.crt
   ```

   The response records **2026-09-22 06:38:53 UTC**, serial `0x084E40B0`. Verify the certificate fingerprints against [FreeTSA's published certificates](https://freetsa.org/index_en.php); a downloaded trust certificate is not automatically a trusted third party.
4. `permanent-genesis.json` is a separate founder-signed designation. Its domain is the UTF-8 bytes `RLD-PERMANENT-GENESIS-DESIGNATION-V1` followed by a zero byte. It signs the `statement` as sorted, compact, ASCII JSON followed by a newline using Ed25519. The founder public key comes from the verified genesis. The designation binds the runtime/source manifests, admission report, operator program and actual recovery/observer receipts.
5. The runtime source archive contains the retained `source` directory. Verify it with its `tools/source-evidence/source_snapshot.py verify --snapshot source --manifest-sha256 49fdd963a483ce725dd480f3be616b620dadbc7cb63111e89cad6be041e5657b`. Installation metadata deliberately retains its historical candidate flag; the later permanent designation does not rewrite that record.

The operating authorization verifier requires Python 3 and the `cryptography` library. Linux deployment used Python's system cryptography 41.0.7. Source/build manifests disclose toolchain and reproducibility limits. The SPDX inventory covers Cargo dependencies, not a whole-host vulnerability audit.

## Observation and scope

Bounded HTTPS GET endpoints at `https://forum.rldcoin.com` expose `/v1/status`, `/v1/consensus/status`, `/v1/consensus/commits`, and admission history data. Public write, signing and administrative endpoints are blocked. The permanent operator updates `/genesis/status.json`; an observation older than three minutes should be treated as stale.

The receipts demonstrate same-identity recovery on the running host, encrypted recovery on the owner's Mac in a network-denied process, and a Mac observer's genesis-to-head synchronization, peer replacement and restart. Both machines and all roles belong to one controller. These are agent technical checks, not independent review, physical offline custody, independent operators, or completed interstellar transfer qualification.

The master plan and remote operations archive describe the authorized P1 scope. Value activation, open rewards, external operators and interstellar route qualification remain later work. No private keys, recovery identity or encrypted private backup is included in this public release.

To verify the designation with the shipped operator program without using private keys:

```sh
# From a directory containing the downloaded release assets:
tar -xzf rldcoin-runtime-source-445e27b.tar.gz
tar -xzf rldcoin-remote-operations.tar.gz
mkdir -p proof-root/config proof-root/artifacts
cp genesis-manifest.json admission-benchmark-report.json permanent-genesis.json proof-root/config/
cp install-manifest.json proof-root/artifacts/
cp -R source proof-root/artifacts/
python3 deploy/permanent-m0.py verify --root proof-root \
  --pin 874066fe96d12bfa42cc316f5387cc8f4df649f794b43e2ee724b8029b0abf33
```

This verification checks the signed scope and artifact bindings. It does not start a node or grant operating authority. A historical signature remains verifiable after software-key expiry; that does not authorize continued signing.

## Current operating revision

The original declaration is unchanged. [Signed operating revision 5](operating-revisions/README.md) supersedes the original calendar stop date with a continuing, owner-revocable software-key authorization. It retains revision 4's exact vote-lock recovery, checkpoint synchronization, ten-minute heartbeats and 30-second public observations. All 24 roles remain supervised; changed authorization or a revocation marker stops signing. Current status explicitly reports `UNTIL_REVOKED` and a null expiry. There is no reward activation, supply change or claim of perpetual cryptographic security.

The existing verifier still has local history and resource ceilings. Continuing authorization does not remove those bounds or promise indefinite uptime. See [revision 5 evidence and limits](operating-revisions/revision-5/README.md).
