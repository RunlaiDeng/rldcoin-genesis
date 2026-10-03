# Regional native BFT fault and retained-payment recovery — revision 17

Repeated signed BFT messages can carry a newly certified dependency prefix.
This revision verifies that complete envelope before deduplicating the body,
prepares outgoing custody evidence before opening its TLS connection, and
archives completed transport earlier without deleting evidence. The exact
229-file source passed one fresh twelve-node fault profile and a separate
stopped-state cold verifier. This is a no-value, same-host/controller ground
candidate; it neither upgrades an adopted network nor qualifies interstellar
service, sustained BFT liveness, independent custody or physical links.

A mainnet has not launched. Future mainnet adoption requires a new
signed zero-issuance genesis. Old and test balances never migrate.

## Observed fresh fault profile

The [fresh run](evidence/regional-native-bft-early-archive-fresh-20261001.json)
started from the stopped revision-16 cycle at heights 7/4/4. Earth validator 0
was offline and Earth–Proxima contacts were cut in both directions. Ordinary
native companions continued certified local progress and remote local payments;
the source export stayed deducted while contact was unavailable. Restart
retained the original signer state and separately held caller head.

| Observation | Actual result |
| --- | --- |
| Entire finite run | 863.055 seconds |
| Three online Earth replicas pass height 9 | 107.403 seconds |
| Restarted Earth replica catches up | 34.281 seconds |
| Interregion contact restored | 248.496 seconds from start |
| Original net output 9 imports and matures | import height 11; maturity height 13 |
| Maturity gate after contact restoration | 488.991 seconds, within its 600-second bound |
| Complete-certificate drain after new signing is paused | 26.455 seconds |
| Stopped, agreeing four-replica regional heights | Earth 15; Proxima 13; Andromeda 16 |
| Native conservation | issued 300 = liquid 300 + in transit 0 |
| Archived payloads fully authenticated after shutdown | 4,506 |

Three actual owner requests offered one export of 10 and two local payments
of 1. Queue acceptance did not debit. Controller-generated consensus messages,
payment-proof carriage and checkpoint installation were all zero. The
controller still schedules faults, restarts and observations; this is not
independent operation. The local signing stop height is 24, and all recorded
phase observations completed within their bounds. A signing cap and one finite
profile do not establish general BFT liveness or resource capacity.

The [separate cold verifier](evidence/regional-native-bft-early-archive-fresh-cold-20261001.json)
replayed all twelve native stores, checked each signer against its separate
caller head, checked the four exact original recipient outputs, and fully
authenticated all 4,506 retained archive payloads. It confirms regional state
agreement, source debit, unique mature import and conservation. Every private
fixture file remained unchanged by these reads. The original sealed cycle and
frozen source also remained unchanged; all owned nodes stopped.

## Recovery and failed observations remain separate

The [retained-payment recovery](evidence/regional-native-bft-retained-maturity-20261001.json)
continued an isolated copy of the previous failed fixture with zero new owner
requests. It completed in 589.121 seconds, preserved the original debit/import,
and matured the original net output 9 at height 12. Its 4,256 archived payloads
authenticated; four [additional native recipient reads](evidence/regional-bft-retained-cold-recipient-20261001.json)
confirmed spendability without changing private files. The fresh-profile cold
verifier actually refuses this recovery mode. Recovery never substitutes for
the fresh fault profile above.

| Earlier run | Duration | Terminal outcome |
| --- | --- | --- |
| [Revision-16 continuation](evidence/regional-native-bft-sustained-20261001.json) | 722.430 s | offline-leader observation deadline |
| [Reception/carriage revision](evidence/regional-native-bft-carriage-sustained-20261001.json) | 584.664 s | controller failed on unavailable height |
| [Unavailable-height handling](evidence/regional-native-bft-controller-sustained-20261001.json) | 966.482 s | recipient maturity observation deadline |
| [Preconnection preparation](evidence/regional-native-bft-preconnect-sustained-20261001.json) | 956.535 s | import accepted, maturity observation deadline |

These failures retain their exact source commitments and do not count as passes.
Historical manifests identify those sources; they are not the current runtime.
Diagnostic selected-neighbor carriage and reader cost samples have narrower
scopes than ordinary scheduling and payment maturity.

## Exact source, bounds and checks

The source-set commitment is
`daf6710c8170b994990bbcf96251023fd9d72ffc968de17a51a186c6e4c9843f`.
[source.tar.gz](source.tar.gz) contains exactly the 229 named files in
[source-manifest.json](source-manifest.json). Supplemental copies under `tools/`
match those same source bytes. Frozen documentation and the manifest's
`cold_verifier_positive_completion_path_qualified: false` describe the pre-run
snapshot; the separate terminal cold report records the later observed pass.
The immutable snapshot is intentionally retained.

Mesh V3/TCP-V4 keeps active admission at 256, completion-only archive high-water
32, at most 16 archive transitions per tick, and archive bounds of 4096 files /
256 MiB per node. Pending unreceipted evidence stays active; archived payloads
are retained. Only immutable bounded transit witnesses persist. Cold/external
validation still verifies complete inputs. A three-second socket attempt is
not a three-second total tick or cryptographic CPU guarantee. Authentication,
durable custody, transport receipt, native import and maturity remain separate.

A checked release rebuild with Rust 1.98.0 passed, as did 84 transport and
34 process/controller checks on the frozen source. [checks.json](checks.json)
records modules, report hashes and test-log commitments. Native Rust sources
are unchanged; their earlier 81-test evidence is retained, not rerun for these
Python changes. TLS uses independently configured literal endpoints and pins,
never pins learned from advertisements, with no insecure fallback.

## Reproduce the observed path

Verify this package's [SHA256SUMS](SHA256SUMS), extract its source into a fresh
directory, and verify the named source manifest before building. Use Rust
1.98.0 and a private Python environment with the exact requirements file.

First reproduce the stopped 7/4/4 cycle using the **revision-16 source and guide**
at public commit
[`dd02da67a8945cc7c953810ab39bb6949d8e518a`](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-archive-v16).
Retain its stopped private cycle directory and its newly produced cycle report.
Do not substitute the published report for your own private run. This two-source
path matches the actual experiment; an initial cycle on revision 17 alone has
not been independently rerun. Native implementation identity is unchanged.

From the extracted revision-17 source:

```sh
CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true CARGO_PROFILE_RELEASE_DEBUG_ASSERTIONS=true cargo build --locked --release --manifest-path tools/regional-ledger/Cargo.toml --bins
python3 -m venv /absolute/private-contact-venv
/absolute/private-contact-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
PYTHONPATH=tools /absolute/private-contact-venv/bin/python -m unittest test_interstellar_mesh test_interstellar_tcp test_interstellar_transfer test_interstellar_route_budget
PYTHONPATH=tools RLD_CONTACT_BINARY=/absolute/source-v17/tools/regional-ledger/target/release/rld-regional-ledger-candidate /absolute/private-contact-venv/bin/python -m unittest test_regional_contact_node test_regional_bft_node test_regional_wallet_app test_regional_bft_sustained_campaign
/absolute/private-contact-venv/bin/python tools/regional_bft_sustained_campaign.py \
  --runtime-tools /absolute/source-v17/tools \
  --source-manifest /absolute/package-v17/source-manifest.json \
  --cycle-report /absolute/your-v16-cycle-report.json \
  --binary /absolute/source-v17/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --source-root /absolute/your-stopped-private-v16-cycle \
  --root /absolute/NEW-private-fault-copy \
  --report /absolute/your-sanitized-fault-report.json
/absolute/private-contact-venv/bin/python tools/verify_regional_bft_sustained.py \
  --source /absolute/source-v17 \
  --manifest /absolute/package-v17/source-manifest.json \
  --run-report /absolute/your-sanitized-fault-report.json \
  --binary /absolute/source-v17/tools/regional-ledger/target/release/rld-regional-ledger-candidate \
  --root /absolute/NEW-private-fault-copy \
  --report /absolute/your-sanitized-cold-report.json
```

Use absolute paths appropriate to your host. Run the cold verifier only after
all owned processes stop. Stop and retain failed fixtures; observation deadlines
never refund exports or delete evidence. A separate recovery invocation requires
both `--resume-report` and `--resume-source-manifest`, referring to an actual
stopped failed fixture with matching native history and latest caller heads.
Never run copied signer keys concurrently.

Private mesh/TLS identities, configurations, journals, signer/head/wallet state,
keys and backups are deliberately excluded. Public fixture seed constants in
source are for worthless experiments only. Full BFT reconfiguration remains
refused; long disconnection, channels, cross-device wallet recovery, physical
adapters, long-term crypto/archives and independent operation remain mandatory.
See [current scope](STATUS.zh-CN.md) and [next acceptance work](ACCEPTANCE_QUEUE.md).
