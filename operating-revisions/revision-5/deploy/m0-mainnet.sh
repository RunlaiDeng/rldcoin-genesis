#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RLD_M0_DIR="${RLD_M0_DIR:-$SCRIPT_DIR/m0-mainnet-data}"
RLD_M0_PORT_BASE="${RLD_M0_PORT_BASE:-38000}"
RLD_M0_BIND="${RLD_M0_BIND:-127.0.0.1}"
ZONE_NAME="${RLD_M0_ZONE_NAME:-Rldcoin-M0}"
CONTROL_GROUP_ID="${RLD_M0_CONTROL_GROUP_ID:-founder-control-group-1}"
INTERNAL_BIND="127.0.0.1"

BUILD_BIN_DIR="$PROJECT_DIR/target/release"
ARTIFACT_DIR="$RLD_M0_DIR/artifacts"
BIN_DIR="$ARTIFACT_DIR/bin"
ARTIFACT_MANIFEST="$ARTIFACT_DIR/install-manifest.json"
CONFIG_DIR="$RLD_M0_DIR/config"
KEY_DIR="$RLD_M0_DIR/keys"
STATE_DIR="$RLD_M0_DIR/state"
LOG_DIR="$RLD_M0_DIR/logs"
RUN_DIR="$RLD_M0_DIR/run"
MANIFEST="$CONFIG_DIR/genesis-manifest.json"
ADMISSION_BENCHMARK_REPORT="$CONFIG_DIR/admission-benchmark-report.json"
SOURCE_EVIDENCE_TOOL="$PROJECT_DIR/tools/source-evidence/source_snapshot.py"
EXPIRY_SUPERVISOR="$ARTIFACT_DIR/source/tree/deploy/run-with-key-expiry.py"

usage() {
  echo "usage: $0 {install|init|build|start|stop|status|heartbeat|verify|backup|restore} [argument]" >&2
  echo "environment: RLD_M0_DIR RLD_M0_PORT_BASE RLD_M0_BIND RLD_M0_ZONE_NAME RLD_M0_CONTROL_GROUP_ID RLD_M0_EXPECTED_MANIFEST_SHA256" >&2
  echo "start also requires: RLD_M0_KEY_EXPIRES_AT (explicit UTC software-key exception, at most 31 days)" >&2
  echo "init also requires: RLD_M0_ADMISSION_MINIMUM_TARGET RLD_M0_ADMISSION_MAXIMUM_TARGET RLD_M0_ADMISSION_GENESIS_TARGET RLD_M0_ADMISSION_CONFIRMATION_WORK_FLOOR RLD_M0_ADMISSION_LEDGER_HEIGHT_ORIGIN RLD_M0_ADMISSION_CONTRIBUTION_EPOCH_ORIGIN RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH RLD_M0_ADMISSION_BENCHMARK_REPORT" >&2
}

require_runtime_commands() {
  local command
  for command in curl jq shasum awk sed find sort grep tr wc ps python3; do
    command -v "$command" >/dev/null 2>&1 || {
      echo "required command is missing: $command" >&2
      exit 1
    }
  done
}

require_build_commands() {
  require_runtime_commands
  local command
  for command in cargo rustc; do
    command -v "$command" >/dev/null 2>&1 || {
      echo "required build command is missing: $command" >&2
      exit 1
    }
  done
}

build_release() {
  require_build_commands
  cd "$PROJECT_DIR"
  cargo build --locked --release -p rld-node -p rld-signer -p rld-witness -p rld-cli
}

artifact_package() {
  case "$1" in
    rldd) echo rld-node ;;
    rld|rld-genesis) echo rld-cli ;;
    rld-signer) echo rld-signer ;;
    rld-witness) echo rld-witness ;;
    *) return 1 ;;
  esac
}

validate_artifact_tree() {
  local root="$1"
  local manifest="$root/install-manifest.json"
  local sidecar="$root/install-manifest.json.sha256"
  local bin_root="$root/bin"
  [[ -d "$root" && ! -L "$root" && -d "$bin_root" && ! -L "$bin_root" ]] || {
    echo "installed artifact tree is missing or unsafe: $root" >&2
    return 1
  }
  [[ -f "$manifest" && ! -L "$manifest" && -f "$sidecar" && ! -L "$sidecar" ]] || {
    echo "installed artifact manifest or sidecar is missing" >&2
    return 1
  }
  local manifest_sha expected_sidecar
  manifest_sha="$(shasum -a 256 "$manifest" | awk '{print $1}')"
  expected_sidecar="$manifest_sha  install-manifest.json"
  [[ "$(sed -n '1p' "$sidecar")" == "$expected_sidecar" && "$(wc -l <"$sidecar" | tr -d ' ')" == "1" ]] || {
    echo "installed artifact manifest sidecar differs" >&2
    return 1
  }
  jq -e '
    ((.format == "RLD-M0-INSTALLED-ARTIFACTS-V1" and .version == 1) or
     (.format == "RLD-M0-INSTALLED-ARTIFACTS-V2" and .version == 2)) and
    .release_profile == "release" and
    .cargo_locked == true and
    .value_cap == "VALUE_CAP_0" and
    .permanent_genesis_ceremony_executed == false and
    (.source.git_commit == "UNCOMMITTED" or (.source.git_commit | test("^[0-9a-f]{40}$"))) and
    (.source.git_tree == "CLEAN" or .source.git_tree == "DIRTY" or .source.git_tree == "UNCOMMITTED") and
    (.source.cargo_lock_sha256 | test("^[0-9a-f]{64}$")) and
    (.source.rust_toolchain_sha256 | test("^[0-9a-f]{64}$")) and
    (.build.rustc_verbose | type == "string" and length > 0) and
    (.build.cargo_version | type == "string" and length > 0) and
    (.build.target_triple | type == "string" and length > 0) and
    (.artifacts | type == "array" and length == 5)
  ' "$manifest" >/dev/null || {
    echo "installed artifact manifest safety boundary differs" >&2
    return 1
  }
  if find "$root" -type l -print -quit | grep -q .; then
    echo "installed artifact tree contains a symbolic link" >&2
    return 1
  fi
  if [[ "$(jq -r '.version' "$manifest")" == "2" ]]; then
    jq -e '
      .source.snapshot_format == "RLD-SOURCE-SNAPSHOT-V1" and
      .source.snapshot_path == "source" and
      (.source.snapshot_manifest_sha256 | test("^[0-9a-f]{64}$")) and
      (.source.snapshot_tree_sha256 | test("^[0-9a-f]{64}$")) and
      .build.source == "RETAINED_SOURCE_SNAPSHOT" and
      .build.hermetic == false and .build.independently_reproduced == false
    ' "$manifest" >/dev/null || { echo "installed source binding is invalid" >&2; return 1; }
    python3 "$SOURCE_EVIDENCE_TOOL" verify --snapshot "$root/source" \
      --manifest-sha256 "$(jq -er '.source.snapshot_manifest_sha256' "$manifest")" >/dev/null || return 1
    jq -e --slurpfile source "$root/source/manifest.json" '
      .source.snapshot_tree_sha256 == $source[0].tree_sha256 and
      .source.git_commit == $source[0].git_commit and .source.git_tree == $source[0].git_tree and
      .source.cargo_lock_sha256 == ($source[0].files[] | select(.path == "Cargo.lock") | .sha256) and
      .source.rust_toolchain_sha256 == ($source[0].files[] | select(.path == "rust-toolchain.toml") | .sha256)
    ' "$manifest" >/dev/null || { echo "installed source facts differ" >&2; return 1; }
  elif [[ -e "$root/source" ]] || jq -e '.source | has("snapshot_manifest_sha256")' "$manifest" >/dev/null; then
    echo "source-bound installation cannot be downgraded to legacy V1 metadata" >&2
    return 1
  fi
  local name package path expected_hash expected_size actual_hash actual_size
  for name in rldd rld rld-genesis rld-signer rld-witness; do
    package="$(artifact_package "$name")"
    path="$bin_root/$name"
    [[ -f "$path" && ! -L "$path" && -x "$path" ]] || {
      echo "installed executable is missing or unsafe: $path" >&2
      return 1
    }
    [[ "$(jq -r --arg name "$name" '[.artifacts[] | select(.name == $name)] | length' "$manifest")" == "1" ]] || {
      echo "installed artifact manifest does not contain exactly one $name" >&2
      return 1
    }
    [[ "$(jq -r --arg name "$name" '.artifacts[] | select(.name == $name) | .package' "$manifest")" == "$package" ]] || {
      echo "installed artifact package binding differs for $name" >&2
      return 1
    }
    [[ "$(jq -r --arg name "$name" '.artifacts[] | select(.name == $name) | .version' "$manifest")" =~ ^[0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.-]+)?$ ]] || {
      echo "installed artifact package version is invalid for $name" >&2
      return 1
    }
    [[ "$(jq -r --arg name "$name" '.artifacts[] | select(.name == $name) | .relative_path' "$manifest")" == "bin/$name" ]] || {
      echo "installed artifact path binding differs for $name" >&2
      return 1
    }
    expected_hash="$(jq -r --arg name "$name" '.artifacts[] | select(.name == $name) | .sha256' "$manifest")"
    expected_size="$(jq -r --arg name "$name" '.artifacts[] | select(.name == $name) | .size_bytes' "$manifest")"
    actual_hash="$(shasum -a 256 "$path" | awk '{print $1}')"
    actual_size="$(wc -c <"$path" | tr -d ' ')"
    [[ "$expected_hash" =~ ^[0-9a-f]{64}$ && "$expected_hash" == "$actual_hash" && "$expected_size" == "$actual_size" ]] || {
      echo "installed artifact hash or size differs for $name" >&2
      return 1
    }
  done
  [[ "$(find "$bin_root" -maxdepth 1 -type f | wc -l | tr -d ' ')" == "5" ]] || {
    echo "installed bin directory contains unexpected files" >&2
    return 1
  }
}

validate_installed_artifacts() {
  require_runtime_commands
  validate_artifact_tree "$ARTIFACT_DIR"
}

install_release() {
  require_build_commands
  [[ ! -e "$ARTIFACT_DIR" ]] || {
    echo "refusing to overwrite installed artifacts: $ARTIFACT_DIR" >&2
    exit 1
  }
  [[ ! -L "$RLD_M0_DIR" ]] || { echo "runtime path must not be a symbolic link: $RLD_M0_DIR" >&2; exit 1; }
  mkdir -p "$RLD_M0_DIR"
  local temporary
  temporary="$(mktemp -d "$RLD_M0_DIR/.artifacts-install.XXXXXX")"
  install_temp_cleanup() {
    if [[ -n "$temporary" && -d "$temporary" ]]; then
      case "$temporary" in
        "$RLD_M0_DIR"/.artifacts-install.*) rm -rf -- "$temporary" ;;
        *) echo "refusing to remove unexpected install temporary path: $temporary" >&2 ;;
      esac
    fi
  }
  trap install_temp_cleanup EXIT
  local snapshot_summary snapshot_manifest_sha256 snapshot_tree_sha256
  snapshot_summary="$(python3 "$SOURCE_EVIDENCE_TOOL" create --root "$PROJECT_DIR" --output "$temporary/source")"
  snapshot_manifest_sha256="$(jq -er '.manifest_sha256' <<<"$snapshot_summary")"
  snapshot_tree_sha256="$(jq -er '.tree_sha256' <<<"$snapshot_summary")"
  # Compile the retained tree, never the mutable working directory. The Cargo
  # dependency cache/toolchain/environment are still local, not a hermetic build.
  (
    cd "$temporary/source/tree"
    CARGO_TARGET_DIR="$temporary/build" cargo build --locked --release \
      -p rld-node -p rld-signer -p rld-witness -p rld-cli
  )
  python3 "$SOURCE_EVIDENCE_TOOL" verify --snapshot "$temporary/source" \
    --manifest-sha256 "$snapshot_manifest_sha256" >/dev/null
  mkdir -p "$temporary/bin"
  local metadata name package version source source_hash size artifact_rows
  metadata="$(cd "$temporary/source/tree" && cargo metadata --locked --no-deps --format-version 1)"
  artifact_rows="$temporary/artifacts.ndjson"
  : >"$artifact_rows"
  for name in rldd rld rld-genesis rld-signer rld-witness; do
    source="$temporary/build/release/$name"
    [[ -f "$source" && -x "$source" ]] || { echo "release build did not produce $source" >&2; exit 1; }
    cp -p "$source" "$temporary/bin/$name"
    chmod 0755 "$temporary/bin/$name"
    package="$(artifact_package "$name")"
    version="$(jq -er --arg package "$package" '.packages[] | select(.name == $package) | .version' <<<"$metadata")"
    source_hash="$(shasum -a 256 "$temporary/bin/$name" | awk '{print $1}')"
    size="$(wc -c <"$temporary/bin/$name" | tr -d ' ')"
    jq -nc --arg name "$name" --arg package "$package" --arg version "$version" \
      --arg path "bin/$name" --arg sha256 "$source_hash" --argjson size "$size" \
      '{name:$name,package:$package,version:$version,relative_path:$path,sha256:$sha256,size_bytes:$size}' \
      >>"$artifact_rows"
  done
  rm -rf -- "$temporary/build"
  local git_commit git_tree cargo_lock_hash toolchain_hash rustc_verbose cargo_version target_triple
  git_commit="$(jq -er '.git_commit' "$temporary/source/manifest.json")"
  git_tree="$(jq -er '.git_tree' "$temporary/source/manifest.json")"
  cargo_lock_hash="$(shasum -a 256 "$temporary/source/tree/Cargo.lock" | awk '{print $1}')"
  toolchain_hash="$(shasum -a 256 "$temporary/source/tree/rust-toolchain.toml" | awk '{print $1}')"
  rustc_verbose="$(rustc -Vv)"
  cargo_version="$(cargo -V)"
  target_triple="$(rustc -Vv | awk -F': ' '$1 == "host" {print $2}')"
  jq -n \
    --arg git_commit "$git_commit" --arg git_tree "$git_tree" \
    --arg cargo_lock_sha256 "$cargo_lock_hash" --arg rust_toolchain_sha256 "$toolchain_hash" \
    --arg snapshot_manifest_sha256 "$snapshot_manifest_sha256" --arg snapshot_tree_sha256 "$snapshot_tree_sha256" \
    --arg rustc "$rustc_verbose" --arg cargo "$cargo_version" --arg target_triple "$target_triple" \
    --slurpfile artifacts "$artifact_rows" \
    '{
      format:"RLD-M0-INSTALLED-ARTIFACTS-V2",version:2,release_profile:"release",cargo_locked:true,
      value_cap:"VALUE_CAP_0",permanent_genesis_ceremony_executed:false,
      source:{git_commit:$git_commit,git_tree:$git_tree,cargo_lock_sha256:$cargo_lock_sha256,rust_toolchain_sha256:$rust_toolchain_sha256,
        snapshot_format:"RLD-SOURCE-SNAPSHOT-V1",snapshot_path:"source",snapshot_manifest_sha256:$snapshot_manifest_sha256,snapshot_tree_sha256:$snapshot_tree_sha256},
      build:{rustc_verbose:$rustc,cargo_version:$cargo,target_triple:$target_triple,source:"RETAINED_SOURCE_SNAPSHOT",hermetic:false,independently_reproduced:false},artifacts:$artifacts
    }' >"$temporary/install-manifest.json"
  rm -f "$artifact_rows"
  printf '%s  install-manifest.json\n' "$(shasum -a 256 "$temporary/install-manifest.json" | awk '{print $1}')" \
    >"$temporary/install-manifest.json.sha256"
  validate_artifact_tree "$temporary"
  mv "$temporary" "$ARTIFACT_DIR"
  temporary=""
  trap - EXIT
  validate_installed_artifacts
  echo "M0 release artifacts installed at $ARTIFACT_DIR"
  echo "VALUE_CAP_0; permanent genesis ceremony not executed."
}

public_port() { echo $((RLD_M0_PORT_BASE + $1)); }
peer_port() { echo $((RLD_M0_PORT_BASE + 100 + $1)); }
admin_port() { echo $((RLD_M0_PORT_BASE + 200 + $1)); }
signer_port() { echo $((RLD_M0_PORT_BASE + 400 + $1)); }
witness_port() { echo $((RLD_M0_PORT_BASE + 500 + $1 * 10 + $2)); }

identity_public_key() {
  jq -er '.public_key' "$1"
}

policy_hash() {
  "$BIN_DIR/rld-witness" policy-hash --policy "$1"
}

generate_identity() {
  "$BIN_DIR/rld" keygen --out "$1" >/dev/null
}

require_expected_manifest_pin_for_file() {
  local manifest="$1"
  local expected="${RLD_M0_EXPECTED_MANIFEST_SHA256:-}"
  [[ "$expected" =~ ^[0-9a-f]{64}$ ]] || {
    echo "RLD_M0_EXPECTED_MANIFEST_SHA256 must be an externally supplied lowercase SHA-256" >&2
    return 1
  }
  [[ -f "$manifest" && ! -L "$manifest" ]] || { echo "signed M0 manifest is missing or unsafe: $manifest" >&2; return 1; }
  local embedded
  embedded="$(jq -er '.manifest_sha256' "$manifest")"
  [[ "$embedded" == "$expected" ]] || {
    echo "signed M0 manifest does not match RLD_M0_EXPECTED_MANIFEST_SHA256" >&2
    return 1
  }
  require_bound_admission_benchmark_for_manifest "$manifest"
}

require_bound_admission_benchmark_for_manifest() {
  local manifest="$1"
  local report expected actual
  report="$(dirname "$manifest")/admission-benchmark-report.json"
  [[ -f "$report" && ! -L "$report" ]] || {
    echo "bound admission benchmark report is missing or unsafe: $report" >&2
    return 1
  }
  expected="$(jq -er '.declaration.admission_genesis.benchmark_report_sha256' "$manifest")"
  actual="$(shasum -a 256 "$report" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    echo "admission benchmark report does not match the founder-signed manifest" >&2
    return 1
  }
}

validate_admission_init_inputs() {
  local name value source size
  for name in \
    RLD_M0_ADMISSION_MINIMUM_TARGET \
    RLD_M0_ADMISSION_MAXIMUM_TARGET \
    RLD_M0_ADMISSION_GENESIS_TARGET \
    RLD_M0_ADMISSION_CONFIRMATION_WORK_FLOOR; do
    value="${!name:-}"
    [[ "$value" =~ ^[0-9a-f]{64}$ ]] || {
      echo "$name must be an explicit lowercase 32-byte hexadecimal U256" >&2
      return 1
    }
  done
  local max_u128="340282366920938463463374607431768211455"
  for name in \
    RLD_M0_ADMISSION_LEDGER_HEIGHT_ORIGIN \
    RLD_M0_ADMISSION_CONTRIBUTION_EPOCH_ORIGIN \
    RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH; do
    value="${!name:-}"
    [[ "$value" =~ ^(0|[1-9][0-9]*)$ && ${#value} -le 39 ]] || {
      echo "$name must be an explicit canonical decimal U128" >&2
      return 1
    }
    if [[ ${#value} -eq 39 && "$value" > "$max_u128" ]]; then
      echo "$name exceeds U128" >&2
      return 1
    fi
  done
  [[ "$RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH" != "0" && "$RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH" != "1" ]] || {
    echo "RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH must be at least 2" >&2
    return 1
  }
  source="${RLD_M0_ADMISSION_BENCHMARK_REPORT:-}"
  [[ -n "$source" && -f "$source" && ! -L "$source" ]] || {
    echo "RLD_M0_ADMISSION_BENCHMARK_REPORT must name a retained regular report file" >&2
    return 1
  }
  size="$(wc -c <"$source" | tr -d ' ')"
  [[ "$size" =~ ^[0-9]+$ && "$size" -gt 0 && "$size" -le 16777216 ]] || {
    echo "admission benchmark report must contain 1..16777216 bytes" >&2
    return 1
  }
}

require_expected_manifest_pin() {
  require_expected_manifest_pin_for_file "$MANIFEST"
}

init_m0() {
  case "${RLD_M0_GENESIS_CANDIDATE_VERSION:-2}" in
    2|3) ;;
    *) echo "RLD_M0_GENESIS_CANDIDATE_VERSION must be 2 or 3" >&2; return 1 ;;
  esac
  require_runtime_commands
  validate_installed_artifacts
  validate_admission_init_inputs
  local existing
  existing="$(find "$RLD_M0_DIR" -mindepth 1 -maxdepth 1 ! -name artifacts -print -quit)"
  [[ -z "$existing" ]] || { echo "refusing to initialize over existing runtime content: $existing" >&2; exit 1; }
  mkdir -p "$CONFIG_DIR/policies" "$CONFIG_DIR/signers" "$KEY_DIR" "$STATE_DIR" "$LOG_DIR" "$RUN_DIR"
  cp -p "$RLD_M0_ADMISSION_BENCHMARK_REPORT" "$ADMISSION_BENCHMARK_REPORT"
  chmod 0444 "$ADMISSION_BENCHMARK_REPORT"

  generate_identity "$KEY_DIR/founder.json"
  local index
  for index in 1 2 3 4; do
    generate_identity "$KEY_DIR/validator-$index.json"
    generate_identity "$KEY_DIR/notary-$index.json"
  done
  generate_identity "$KEY_DIR/observer.json"

  for index in 1 2 3; do
    "$BIN_DIR/rld-witness" keygen \
      --operator-id "m0-witness-$index" \
      --control-domain "founder-control.invalid/witness-$index" \
      --output "$KEY_DIR/witness-$index.json" >/dev/null
    "$BIN_DIR/rld-witness" publisher-keygen \
      --publisher-id "m0-publisher-$index" \
      --control-domain "founder-control.invalid/publisher-$index" \
      --output "$KEY_DIR/publisher-$index.json" >/dev/null
  done

  local genesis_args=(
    create
    --zone-name "$ZONE_NAME"
    --control-group-id "$CONTROL_GROUP_ID"
    --founder-key "$KEY_DIR/founder.json"
    --admission-minimum-target "$RLD_M0_ADMISSION_MINIMUM_TARGET"
    --admission-maximum-target "$RLD_M0_ADMISSION_MAXIMUM_TARGET"
    --admission-genesis-target "$RLD_M0_ADMISSION_GENESIS_TARGET"
    --admission-confirmation-work-floor "$RLD_M0_ADMISSION_CONFIRMATION_WORK_FLOOR"
    --admission-ledger-height-origin "$RLD_M0_ADMISSION_LEDGER_HEIGHT_ORIGIN"
    --admission-contribution-epoch-origin "$RLD_M0_ADMISSION_CONTRIBUTION_EPOCH_ORIGIN"
    --admission-ledger-blocks-per-contribution-epoch "$RLD_M0_ADMISSION_LEDGER_BLOCKS_PER_CONTRIBUTION_EPOCH"
    --admission-benchmark-sha256 "$(shasum -a 256 "$ADMISSION_BENCHMARK_REPORT" | awk '{print $1}')"
    --out "$MANIFEST"
  )
  if [[ "${RLD_M0_GENESIS_CANDIDATE_VERSION:-2}" == "3" ]]; then
    genesis_args+=(--candidate-v3)
  fi
  for index in 1 2 3 4; do
    genesis_args+=(--validator-key "$KEY_DIR/validator-$index.json")
  done
  for index in 1 2 3 4; do
    genesis_args+=(--notary-key "$KEY_DIR/notary-$index.json")
  done
  "$BIN_DIR/rld-genesis" "${genesis_args[@]}"
  require_bound_admission_benchmark_for_manifest "$MANIFEST"

  jq -s '[.[] | {operator_id,control_domain,public_key}]' \
    "$KEY_DIR/witness-1.json" "$KEY_DIR/witness-2.json" "$KEY_DIR/witness-3.json" \
    >"$CONFIG_DIR/operators.json"
  jq -s '[.[] | {publisher_id,control_domain,public_key}]' \
    "$KEY_DIR/publisher-1.json" "$KEY_DIR/publisher-2.json" "$KEY_DIR/publisher-3.json" \
    >"$CONFIG_DIR/publishers.json"

  local network zone currency subject label subject_key policy policy_id hash
  network="$(jq -er '.declaration.descriptor.network_domain' "$MANIFEST")"
  zone="$(jq -er '.declaration.descriptor.zone_id' "$MANIFEST")"
  currency="$(jq -er '.declaration.descriptor.currency_genesis_root' "$MANIFEST")"
  for index in 1 2 3 4 5; do
    if [[ "$index" -le 4 ]]; then
      label="validator-$index"
      subject_key="$KEY_DIR/validator-$index.json"
    else
      label="observer"
      subject_key="$KEY_DIR/observer.json"
    fi
    subject="$(identity_public_key "$subject_key")"
    policy="$CONFIG_DIR/policies/$label.json"
    policy_id="rld-m0-$label-witness-policy"
    jq -n \
      --arg network "$network" \
      --arg zone "$zone" \
      --arg currency "$currency" \
      --arg subject "$subject" \
      --arg policy_id "$policy_id" \
      --slurpfile operators "$CONFIG_DIR/operators.json" \
      --slurpfile publishers "$CONFIG_DIR/publishers.json" \
      '{
        protocol_version:"RLD-ROLLBACK-WITNESS-V1",
        policy_id:$policy_id,
        network_domain:$network,
        zone_id:$zone,
        currency_genesis_root:$currency,
        storage_format:"RLD-ZONE-STORE-V2",
        subject_id:$subject,
        threshold:"3",
        operators:$operators[0],
        publisher_threshold:"3",
        checkpoint_publishers:$publishers[0]
      }' >"$policy"
    hash="$(policy_hash "$policy")"
    printf '%s\n' "$hash" >"$CONFIG_DIR/policies/$label.sha256"
    if [[ "$index" -le 4 ]]; then
      jq -n \
        --arg network "$network" \
        --arg zone "$zone" \
        --arg currency "$currency" \
        --arg key "$subject" \
        --arg policy_hash "$hash" \
        '{
          protocol_version:"RLD-ISOLATED-SIGNER-V1",
          network_domain:$network,
          zone_id:$zone,
          currency_genesis_root:$currency,
          protocol_era:1,
          crypto_era:1,
          validator_public_key:$key,
          witness_policy_hash:$policy_hash,
          allowed_consensus_profile:"NETWORK_HEARTBEAT_ONLY_V1"
        }' >"$CONFIG_DIR/signers/validator-$index.json"
    fi
  done

  chmod 0600 "$KEY_DIR"/*.json

  jq -n \
    --arg manifest_sha256 "$(jq -er '.manifest_sha256' "$MANIFEST")" \
    --arg admission_genesis_header "$(jq -er '.declaration.admission_genesis.genesis_header' "$MANIFEST")" \
    --arg admission_benchmark_sha256 "$(jq -er '.declaration.admission_genesis.benchmark_report_sha256' "$MANIFEST")" \
    --arg control_group_id "$CONTROL_GROUP_ID" \
    --argjson port_base "$RLD_M0_PORT_BASE" \
    '{
      phase:"M0_NETWORK_BIRTH",
      founder_bootstrapped:true,
      single_control_declared:true,
      control_group_count:1,
      control_group_id:$control_group_id,
      manifest_sha256:$manifest_sha256,
      admission_genesis_header:$admission_genesis_header,
      admission_benchmark_sha256:$admission_benchmark_sha256,
      value_cap:"VALUE_CAP_0",
      transferable_value_enabled:false,
      bft:"3_OF_4_FIXED_VALIDATORS",
      witness_disclosure:"three logical rollback services per subject, all operated by the one declared founder control group; not independent owners",
      port_base:$port_base,
      replaceable_manual_peers:true
    }' >"$CONFIG_DIR/control-disclosure.json"

  "$BIN_DIR/rld-genesis" verify --manifest "$MANIFEST"
  echo "M0 initialized at $RLD_M0_DIR"
  echo "Transferable value is disabled. All processes are one declared control group."
}

canonical_file_path() {
  local path="$1"
  local directory
  directory="$(cd "$(dirname "$path")" && pwd -P)"
  printf '%s/%s\n' "$directory" "$(basename "$path")"
}

process_start_identity() {
  local pid="$1"
  if [[ -r "/proc/$pid/stat" ]]; then
    local boot_id start_ticks
    boot_id="$(sed -n '1p' /proc/sys/kernel/random/boot_id 2>/dev/null || echo unknown-boot)"
    start_ticks="$(awk '{print $22}' "/proc/$pid/stat")"
    printf 'linux:%s:%s\n' "$boot_id" "$start_ticks"
  else
    local started
    started="$(LC_ALL=C ps -ww -p "$pid" -o lstart= 2>/dev/null | sed -E 's/^[[:space:]]+//;s/[[:space:]]+$//')"
    [[ -n "$started" ]] || return 1
    printf 'ps:%s\n' "$started"
  fi
}

process_executable_path() {
  local pid="$1"
  local path=""
  if [[ -L "/proc/$pid/exe" ]]; then path="$(readlink "/proc/$pid/exe")"; fi
  if [[ -z "$path" ]]; then
    path="$(ps -ww -p "$pid" -o comm= 2>/dev/null | sed -E 's/^[[:space:]]+//;s/[[:space:]]+$//')"
  fi
  [[ -n "$path" && -e "$path" ]] || return 1
  canonical_file_path "$path"
}

process_command_sha256() {
  local pid="$1"
  local command_line
  command_line="$(ps -ww -p "$pid" -o command= 2>/dev/null)"
  [[ -n "$command_line" ]] || return 1
  printf '%s' "$command_line" | shasum -a 256 | awk '{print $1}'
}

process_is_live() {
  local pid="$1" state
  kill -0 "$pid" 2>/dev/null || return 1
  state="$(ps -p "$pid" -o stat= 2>/dev/null)" || return 1
  [[ -n "$state" && "$state" != *Z* ]]
}

validate_expiry_supervisor() {
  local file="$1" supervisor_pid parent_pid
  jq -e '
    .format == "RLD-M0-PROCESS-METADATA-V2" and
    (.software_key_exception.expires_at | type == "string") and
    (.software_key_exception.supervisor.pid | type == "number" and . > 0 and floor == .) and
    (.software_key_exception.supervisor.script_sha256 | test("^[0-9a-f]{64}$"))
  ' "$file" >/dev/null 2>&1 || return 1
  supervisor_pid="$(jq -er '.software_key_exception.supervisor.pid' "$file")"
  process_is_live "$supervisor_pid" || return 1
  [[ "$(process_start_identity "$supervisor_pid")" == "$(jq -er '.software_key_exception.supervisor.system_start_identity' "$file")" ]] || return 1
  [[ "$(process_command_sha256 "$supervisor_pid")" == "$(jq -er '.software_key_exception.supervisor.system_command_sha256' "$file")" ]] || return 1
  [[ "$(process_executable_path "$supervisor_pid")" == "$(jq -er '.software_key_exception.supervisor.executable' "$file")" ]] || return 1
  [[ "$(shasum -a 256 "$EXPIRY_SUPERVISOR" | awk '{print $1}')" == "$(jq -er '.software_key_exception.supervisor.script_sha256' "$file")" ]] || return 1
  parent_pid="$(ps -p "$(jq -er '.pid' "$file")" -o ppid= | tr -d ' ')"
  [[ "$parent_pid" == "$supervisor_pid" ]] || return 1
  python3 - "$(jq -er '.software_key_exception.expires_at' "$file")" <<'PY'
import datetime, sys
expires = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
raise SystemExit(0 if datetime.datetime.now(datetime.timezone.utc) < expires else 1)
PY
}

require_software_key_exception() {
  [[ -n "${RLD_M0_KEY_EXPIRES_AT:-}" ]] || {
    echo "start requires explicit RLD_M0_KEY_EXPIRES_AT; no unlimited software-key launch" >&2
    return 1
  }
  [[ -f "$EXPIRY_SUPERVISOR" && ! -L "$EXPIRY_SUPERVISOR" ]] || {
    echo "installed source lacks the software-key expiry supervisor; reinstall from qualified source" >&2
    return 1
  }
  python3 "$EXPIRY_SUPERVISOR" --check-only --expires-at "$RLD_M0_KEY_EXPIRES_AT" \
    --binary-sha256 "$(jq -er '.artifacts[] | select(.name == "rldd") | .sha256' "$ARTIFACT_MANIFEST")" \
    -- "$(canonical_file_path "$BIN_DIR/rldd")"
}

validate_pid_metadata() {
  local file="$1"
  local check_supervisor="${2:-true}"
  [[ -f "$file" && ! -L "$file" ]] || return 1
  jq -e '
    (.format == "RLD-M0-PROCESS-METADATA-V1" or .format == "RLD-M0-PROCESS-METADATA-V2") and
    (.name | type == "string" and length > 0) and
    (.pid | type == "number" and . > 0 and floor == .) and
    (.system_start_identity | type == "string" and length > 0) and
    (.executable | type == "string" and startswith("/")) and
    (.artifact_name | type == "string" and length > 0) and
    (.artifact_sha256 | test("^[0-9a-f]{64}$")) and
    (.arguments_sha256 | test("^[0-9a-f]{64}$")) and
    (.system_command_sha256 | test("^[0-9a-f]{64}$"))
  ' "$file" >/dev/null 2>&1 || { echo "invalid process metadata: $file" >&2; return 2; }
  local pid
  pid="$(jq -er '.pid' "$file")"
  if ! process_is_live "$pid"; then return 1; fi
  local expected_name recorded_start recorded_executable artifact_name recorded_hash recorded_command
  local current_start current_executable current_hash current_command manifest_hash
  expected_name="$(basename "$file" .pid.json)"
  [[ "$(jq -er '.name' "$file")" == "$expected_name" ]] || { echo "process metadata name differs: $file" >&2; return 2; }
  recorded_start="$(jq -er '.system_start_identity' "$file")"
  recorded_executable="$(jq -er '.executable' "$file")"
  artifact_name="$(jq -er '.artifact_name' "$file")"
  recorded_hash="$(jq -er '.artifact_sha256' "$file")"
  recorded_command="$(jq -er '.system_command_sha256' "$file")"
  current_start="$(process_start_identity "$pid")" || { echo "cannot read process start identity for $expected_name" >&2; return 2; }
  current_executable="$(process_executable_path "$pid")" || { echo "cannot read process executable for $expected_name" >&2; return 2; }
  current_command="$(process_command_sha256 "$pid")" || { echo "cannot read process command identity for $expected_name" >&2; return 2; }
  [[ "$artifact_name" =~ ^(rldd|rld-signer|rld-witness)$ ]] || { echo "unexpected process artifact for $expected_name" >&2; return 2; }
  [[ "$recorded_executable" == "$(canonical_file_path "$BIN_DIR/$artifact_name")" && "$current_executable" == "$recorded_executable" ]] || {
    echo "process executable identity differs for $expected_name" >&2; return 2;
  }
  manifest_hash="$(jq -er --arg name "$artifact_name" '.artifacts[] | select(.name == $name) | .sha256' "$ARTIFACT_MANIFEST")"
  current_hash="$(shasum -a 256 "$recorded_executable" | awk '{print $1}')"
  [[ "$recorded_start" == "$current_start" && "$recorded_command" == "$current_command" && \
    "$recorded_hash" == "$manifest_hash" && "$current_hash" == "$recorded_hash" ]] || {
    echo "process start, command or installed hash identity differs for $expected_name" >&2; return 2;
  }
  if [[ "$check_supervisor" == true ]]; then
    validate_expiry_supervisor "$file" || {
      echo "software-key supervisor is missing, changed or expired: $expected_name" >&2; return 2;
    }
  fi
}

start_process() {
  local name="$1"
  shift
  local pid_file="$RUN_DIR/$name.pid.json"
  if [[ -e "$pid_file" ]]; then
    if validate_pid_metadata "$pid_file"; then
      echo "process already running: $name" >&2
      return 1
    else
      local metadata_status=$?
      if [[ "$metadata_status" == "1" ]]; then
        find "$pid_file" -maxdepth 0 -type f -delete
      else
        echo "refusing to replace mismatched live process metadata: $pid_file" >&2
        return 1
      fi
    fi
  fi
  local executable artifact_name artifact_hash arguments_hash
  executable="$(canonical_file_path "$1")"
  artifact_name="$(basename "$executable")"
  artifact_hash="$(jq -er --arg name "$artifact_name" '.artifacts[] | select(.name == $name) | .sha256' "$ARTIFACT_MANIFEST")"
  arguments_hash="$(printf '%s\0' "$@" | shasum -a 256 | awk '{print $1}')"
  [[ -n "${RLD_M0_KEY_EXPIRES_AT:-}" ]] || { echo "software-key expiry is required" >&2; return 1; }
  local receipt_dir receipt supervisor_pid supervisor_start supervisor_command supervisor_executable supervisor_hash count
  receipt_dir="$(mktemp -d "$RUN_DIR/.launch-$name.XXXXXX")"
  receipt="$receipt_dir/child.pid"
  supervisor_hash="$(shasum -a 256 "$EXPIRY_SUPERVISOR" | awk '{print $1}')"
  nohup python3 "$EXPIRY_SUPERVISOR" --expires-at "$RLD_M0_KEY_EXPIRES_AT" \
    --binary-sha256 "$artifact_hash" --child-pid-file "$receipt" -- "$@" \
    >"$LOG_DIR/$name.log" 2>&1 </dev/null &
  supervisor_pid=$!
  local pid=""
  for count in $(seq 1 100); do
    if [[ -s "$receipt" ]]; then pid="$(cat "$receipt")"; break; fi
    process_is_live "$supervisor_pid" || break
    sleep 0.02
  done
  if [[ ! "$pid" =~ ^[1-9][0-9]*$ ]]; then
    kill "$supervisor_pid" 2>/dev/null || true
    wait "$supervisor_pid" 2>/dev/null || true
    rm -f "$receipt"; rmdir "$receipt_dir"
    echo "expiry supervisor did not launch $name; see $LOG_DIR/$name.log" >&2
    return 1
  fi
  rm -f "$receipt"; rmdir "$receipt_dir"
  local start_identity command_hash current_executable
  for count in $(seq 1 50); do
    if process_is_live "$pid" \
      && start_identity="$(process_start_identity "$pid" 2>/dev/null)" \
      && current_executable="$(process_executable_path "$pid" 2>/dev/null)" \
      && [[ "$current_executable" == "$executable" ]] \
      && command_hash="$(process_command_sha256 "$pid" 2>/dev/null)"; then
      break
    fi
    sleep 0.02
  done
  if [[ -z "${start_identity:-}" || -z "${command_hash:-}" ]]; then
    kill "$supervisor_pid" 2>/dev/null || true
    wait "$supervisor_pid" 2>/dev/null || true
    echo "process exited before identity metadata was captured: $name" >&2
    return 1
  fi
  if ! supervisor_start="$(process_start_identity "$supervisor_pid")" \
    || ! supervisor_command="$(process_command_sha256 "$supervisor_pid")" \
    || ! supervisor_executable="$(process_executable_path "$supervisor_pid")"; then
    kill "$supervisor_pid" 2>/dev/null || true
    wait "$supervisor_pid" 2>/dev/null || true
    echo "expiry supervisor exited during launch: $name" >&2
    return 1
  fi
  local metadata_tmp="$pid_file.tmp"
  jq -n --arg name "$name" --argjson pid "$pid" --arg start "$start_identity" \
    --arg executable "$executable" --arg artifact_name "$artifact_name" --arg artifact_sha256 "$artifact_hash" \
    --arg arguments_sha256 "$arguments_hash" --arg system_command_sha256 "$command_hash" \
    --arg expires_at "$RLD_M0_KEY_EXPIRES_AT" --argjson supervisor_pid "$supervisor_pid" \
    --arg supervisor_start "$supervisor_start" --arg supervisor_command "$supervisor_command" \
    --arg supervisor_executable "$supervisor_executable" --arg supervisor_hash "$supervisor_hash" \
    '{format:"RLD-M0-PROCESS-METADATA-V2",name:$name,pid:$pid,system_start_identity:$start,
      executable:$executable,artifact_name:$artifact_name,artifact_sha256:$artifact_sha256,
      arguments_sha256:$arguments_sha256,system_command_sha256:$system_command_sha256,
      software_key_exception:{expires_at:$expires_at,supervisor:{pid:$supervisor_pid,
        system_start_identity:$supervisor_start,system_command_sha256:$supervisor_command,
        executable:$supervisor_executable,script_sha256:$supervisor_hash}}}' >"$metadata_tmp"
  mv "$metadata_tmp" "$pid_file"
  if ! validate_pid_metadata "$pid_file"; then
    kill "$supervisor_pid" 2>/dev/null || true
    wait "$supervisor_pid" 2>/dev/null || true
    return 1
  fi
}

wait_http() {
  local url="$1"
  local attempts="${2:-200}"
  local count
  for count in $(seq 1 "$attempts"); do
    if curl --noproxy '*' -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done
  echo "timed out waiting for $url" >&2
  return 1
}

start_witnesses() {
  local subject_index witness_index label port
  local birth_args=()
  if [[ "$(jq -er '.declaration.format_version' "$MANIFEST")" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
    birth_args=(--m0-genesis-manifest "$MANIFEST" --m0-manifest-sha256 "$RLD_M0_EXPECTED_MANIFEST_SHA256")
  fi
  for subject_index in 1 2 3 4 5; do
    if [[ "$subject_index" -le 4 ]]; then label="validator-$subject_index"; else label="observer"; fi
    for witness_index in 1 2 3; do
      port="$(witness_port "$subject_index" "$witness_index")"
      start_process "witness-$label-$witness_index" \
        "$BIN_DIR/rld-witness" serve \
        --listen "$INTERNAL_BIND:$port" \
        --policy "$CONFIG_DIR/policies/$label.json" \
        --key "$KEY_DIR/witness-$witness_index.json" \
        --store "$STATE_DIR/witness-$label-$witness_index.json" \
        "${birth_args[@]}"
    done
  done
  for subject_index in 1 2 3 4 5; do
    for witness_index in 1 2 3; do
      wait_http "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")/health"
    done
  done
}

start_signers() {
  local index
  local birth_args=()
  if [[ "$(jq -er '.declaration.format_version' "$MANIFEST")" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
    birth_args=(--m0-genesis-manifest "$MANIFEST" --m0-manifest-sha256 "$RLD_M0_EXPECTED_MANIFEST_SHA256")
  fi
  for index in 1 2 3 4; do
    start_process "signer-$index" \
      "$BIN_DIR/rld-signer" \
      --listen "$INTERNAL_BIND:$(signer_port "$index")" \
      --config "$CONFIG_DIR/signers/validator-$index.json" \
      --witness-policy "$CONFIG_DIR/policies/validator-$index.json" \
      --key "$KEY_DIR/validator-$index.json" \
      --state "$STATE_DIR/signer-$index.json" \
      --monotonic-anchor "$STATE_DIR/signer-$index.anchor.json" \
      "${birth_args[@]}"
  done
  for index in 1 2 3 4; do
    wait_http "http://127.0.0.1:$(signer_port "$index")/health"
  done
}

witness_node_args() {
  local subject_index="$1"
  local label="$2"
  local args=(
    --witness-policy "$CONFIG_DIR/policies/$label.json"
    --witness-policy-hash "$(sed -n '1p' "$CONFIG_DIR/policies/$label.sha256")"
    --witness-min-quorum 3
    --witness-timeout-ms 1000
    --witness-poll-interval-ms 100
  )
  local witness_index
  for witness_index in 1 2 3; do
    args+=(--witness-peer "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")")
  done
  printf '%s\n' "${args[@]}"
}

start_nodes() {
  local index peer_index
  for index in 1 2 3 4; do
    local args=(
      --zone-name "$ZONE_NAME"
      --testnet false
      --m0-genesis-manifest "$MANIFEST"
      --m0-genesis-manifest-sha256 "$RLD_M0_EXPECTED_MANIFEST_SHA256"
      --listen "$RLD_M0_BIND:$(public_port "$index")"
      --peer-listen "$RLD_M0_BIND:$(peer_port "$index")"
      --data "$STATE_DIR/node-$index"
      --validator-signer-url "http://127.0.0.1:$(signer_port "$index")"
      --validator-signer-public-key "$(identity_public_key "$KEY_DIR/validator-$index.json")"
      --consensus-timeout-ms 2000
      --admission-peer-timeout-ms 2000
      --admission-sync-interval-ms 1000
    )
    while IFS= read -r argument; do args+=("$argument"); done < <(witness_node_args "$index" "validator-$index")
    for peer_index in 1 2 3 4; do
      if [[ "$peer_index" != "$index" ]]; then
        args+=(--consensus-peer "http://127.0.0.1:$(peer_port "$peer_index")")
        args+=(--admission-peer "http://127.0.0.1:$(peer_port "$peer_index")")
      fi
    done
    start_process "node-$index" "$BIN_DIR/rldd" "${args[@]}"
  done

  local observer_args=(
    --zone-name "$ZONE_NAME"
    --testnet false
    --m0-genesis-manifest "$MANIFEST"
    --m0-genesis-manifest-sha256 "$RLD_M0_EXPECTED_MANIFEST_SHA256"
    --listen "$RLD_M0_BIND:$(public_port 5)"
    --data "$STATE_DIR/observer"
    --witness-subject-id "$(identity_public_key "$KEY_DIR/observer.json")"
    --consensus-timeout-ms 2000
    --admission-peer-timeout-ms 2000
    --admission-sync-interval-ms 1000
  )
  if [[ "$(jq -er '.declaration.format_version' "$MANIFEST")" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
    observer_args+=(--peer-listen "$INTERNAL_BIND:$(peer_port 5)")
  fi
  while IFS= read -r argument; do observer_args+=("$argument"); done < <(witness_node_args 5 observer)
  for peer_index in 1 2 3 4; do
    observer_args+=(--consensus-peer "http://127.0.0.1:$(peer_port "$peer_index")")
    observer_args+=(--admission-peer "http://127.0.0.1:$(peer_port "$peer_index")")
  done
  start_process observer "$BIN_DIR/rldd" "${observer_args[@]}"

  for index in 1 2 3 4 5; do
    wait_http "http://127.0.0.1:$(public_port "$index")/v1/status"
  done
}

snapshot_after_witness_sync() {
  local subject_index="$1" label="$2" status_port="$3" destination="$4"
  local before="$RUN_DIR/$label.node-status-before-sync.json"
  local after="$RUN_DIR/$label.node-status-after-sync.json"
  local sync_status="$RUN_DIR/$label.witness-semantic-sync.json"
  local attempt before_point after_point
  # Catch-up can append a certified block immediately after the sync endpoint
  # releases its ledger read lock. Only publish a checkpoint from a stable pair.
  # This is a bounded startup/heartbeat barrier, not an authorization to retry a
  # partially published checkpoint or to weaken a witness's exact-root check.
  for ((attempt = 1; attempt <= 10; attempt++)); do
    curl --noproxy '*' --max-time 5 -fsS \
      "http://127.0.0.1:$status_port/v1/status" >"$before" || return 1
    curl --noproxy '*' --max-time 30 -fsS -X POST -H 'content-type: application/json' --data '{}' \
      "http://127.0.0.1:$(peer_port "$subject_index")/v1/witness/semantic-sync" \
      >"$sync_status" || return 1
    jq -e '.bound_witness_domains >= 3 and .upgrade_runtime_active == false' \
      "$sync_status" >/dev/null || return 1
    curl --noproxy '*' --max-time 5 -fsS \
      "http://127.0.0.1:$status_port/v1/status" >"$after" || return 1
    before_point="$(jq -ecS '{descriptor,persistence} | if .descriptor != null and
      .persistence != null and .persistence.poisoned == false then .
      else error("missing or poisoned node checkpoint state") end' "$before")" || return 1
    after_point="$(jq -ecS '{descriptor,persistence} | if .descriptor != null and
      .persistence != null and .persistence.poisoned == false then .
      else error("missing or poisoned node checkpoint state") end' "$after")" || return 1
    if [[ "$before_point" == "$after_point" ]]; then
      mv "$after" "$destination"
      return 0
    fi
  done
  echo "node $label did not stabilize across witness history delivery; no checkpoint published" >&2
  return 1
}

seed_subject_witnesses() {
  local subject_index="$1"
  local label="$2"
  local status_port="$3"
  local first_status="$RUN_DIR/$label.witness-status.json"
  local head_code
  head_code="$(curl --noproxy '*' -sS -o "$first_status" -w '%{http_code}' \
    "http://127.0.0.1:$(witness_port "$subject_index" 1)/v1/head")"
  [[ "$head_code" == "200" || "$head_code" == "404" ]] || { echo "unexpected witness head response: $head_code" >&2; return 1; }
  local node_status="$RUN_DIR/$label.node-status.json"
  local checkpoint="$RUN_DIR/$label.checkpoint.json"
  local policy="$CONFIG_DIR/policies/$label.json"
  local subject
  subject="$(jq -er '.subject_id' "$policy")"
  if [[ "$(jq -er '.declaration.format_version' "$MANIFEST")" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
    snapshot_after_witness_sync "$subject_index" "$label" "$status_port" "$node_status" || return 1
  else
    curl --noproxy '*' -fsS "http://127.0.0.1:$status_port/v1/status" >"$node_status"
  fi
  if [[ "$head_code" == "200" ]] && jq -e '.head != null' "$first_status" >/dev/null 2>&1; then
    local witnessed_sequence local_sequence witnessed_height local_height witnessed_root local_root
    witnessed_sequence="$(jq -r '.head.checkpoint.node_binding.durable_sequence // ""' "$first_status")"
    local_sequence="$(jq -r '.persistence.sequence|tostring' "$node_status")"
    witnessed_height="$(jq -r '.head.checkpoint.node_binding.ledger_height // ""' "$first_status")"
    local_height="$(jq -r '.persistence.height|tostring' "$node_status")"
    witnessed_root="$(jq -r '.head.checkpoint.state_root // ""' "$first_status")"
    local_root="sha256:$(jq -r '.persistence.state_root' "$node_status")"
    if [[ "$witnessed_sequence" == "$local_sequence" \
      && "$witnessed_height" == "$local_height" \
      && "$witnessed_root" == "$local_root" ]]; then
      return 0
    fi
  fi

  local previous_receipt="$STATE_DIR/witness-$label.quorum.json"
  local previous_id=""
  if jq -e '.head != null' "$first_status" >/dev/null 2>&1; then
    [[ -f "$previous_receipt" ]] || { echo "missing prior quorum receipt for $label" >&2; return 1; }
    previous_id="$("$BIN_DIR/rld-witness" certified-checkpoint-id --policy "$policy" --receipt "$previous_receipt")"
  fi
  jq \
    --arg policy_id "$(jq -er '.policy_id' "$policy")" \
    --arg subject "$subject" \
    --arg previous "$previous_id" \
    '{
      protocol_version:"RLD-ROLLBACK-WITNESS-V1",
      policy_id:$policy_id,
      network_domain:.descriptor.network_domain,
      zone_id:.descriptor.zone_id,
      currency_genesis_root:.descriptor.currency_genesis_root,
      storage_format:"RLD-ZONE-STORE-V2",
      height:(.persistence.height|tostring),
      state_root:("sha256:" + .persistence.state_root),
      previous_certified_checkpoint_id:(if $previous == "" then null else $previous end),
      epoch:(.descriptor.protocol_era|tostring),
      node_binding:{
        format_version:"RLD-NODE-CHECKPOINT-BINDING-V1",
        subject_id:$subject,
        durable_sequence:(.persistence.sequence|tostring),
        ledger_height:(.persistence.height|tostring),
        last_record_hash:("sha256:" + .persistence.last_record_hash),
        protocol_era:(.descriptor.protocol_era|tostring),
        crypto_era:(.descriptor.crypto_era|tostring)
      }
    }' "$node_status" >"$checkpoint"

  local publisher_index witness_index
  for publisher_index in 1 2 3; do
    "$BIN_DIR/rld-witness" publisher-sign \
      --policy "$policy" \
      --checkpoint "$checkpoint" \
      --key "$KEY_DIR/publisher-$publisher_index.json" \
      --output "$RUN_DIR/$label.publisher-$publisher_index.json"
  done
  "$BIN_DIR/rld-witness" assemble-finality \
    --policy "$policy" \
    --checkpoint "$checkpoint" \
    --publisher-signature "$RUN_DIR/$label.publisher-1.json" \
    --publisher-signature "$RUN_DIR/$label.publisher-2.json" \
    --publisher-signature "$RUN_DIR/$label.publisher-3.json" \
    --output "$RUN_DIR/$label.finality.json"
  for witness_index in 1 2 3; do
    local submit_args=(
      submit
      --url "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")"
      --checkpoint "$checkpoint"
      --finality-certificate "$RUN_DIR/$label.finality.json"
    )
    if [[ -n "$previous_id" ]]; then submit_args+=(--previous-receipt "$previous_receipt"); fi
    "$BIN_DIR/rld-witness" "${submit_args[@]}" >"$RUN_DIR/$label.receipt-$witness_index.json"
  done
  "$BIN_DIR/rld-witness" assemble \
    --policy "$policy" \
    --checkpoint "$checkpoint" \
    --finality-certificate "$RUN_DIR/$label.finality.json" \
    --operator-receipt "$RUN_DIR/$label.receipt-1.json" \
    --operator-receipt "$RUN_DIR/$label.receipt-2.json" \
    --operator-receipt "$RUN_DIR/$label.receipt-3.json" \
    --output "$RUN_DIR/$label.quorum.json"
  cp -p "$RUN_DIR/$label.quorum.json" "$previous_receipt"
}

wait_ready() {
  local index status_url count
  for index in 1 2 3 4 5; do
    status_url="http://127.0.0.1:$(public_port "$index")/v1/status"
    for count in $(seq 1 300); do
      if curl --noproxy '*' -fsS "$status_url" 2>/dev/null \
        | jq -e '.witness_gate.mode == "READY"' >/dev/null 2>&1; then
        break
      fi
      sleep 0.1
    done
    if [[ "$count" == "300" ]]; then
      echo "node $index did not reach witness READY" >&2
      curl --noproxy '*' -sS "$status_url" | jq '.witness_gate' >&2 || true
      return 1
    fi
  done
}

wait_converged() {
  local count index snapshot reference_height reference_root observed_height observed_root converged
  for count in $(seq 1 400); do
    converged=1
    reference_height=""
    reference_root=""
    for index in 1 2 3 4 5; do
      snapshot="$(curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" 2>/dev/null || true)"
      if [[ -z "$snapshot" ]]; then converged=0; break; fi
      observed_height="$(jq -r '.height // -1' <<<"$snapshot")"
      observed_root="$(jq -r '.persistence.state_root // ""' <<<"$snapshot")"
      if [[ -z "$reference_height" ]]; then
        reference_height="$observed_height"
        reference_root="$observed_root"
      elif [[ "$observed_height" != "$reference_height" || "$observed_root" != "$reference_root" ]]; then
        converged=0
        break
      fi
    done
    if [[ "$converged" == "1" ]]; then return 0; fi
    sleep 0.1
  done
  echo "M0 nodes did not converge on one height and state root" >&2
  return 1
}

start_m0() {
  require_runtime_commands
  validate_installed_artifacts
  require_software_key_exception
  [[ -f "$MANIFEST" ]] || { echo "run init first: $MANIFEST is missing" >&2; exit 1; }
  require_expected_manifest_pin
  mkdir -p "$STATE_DIR" "$LOG_DIR" "$RUN_DIR"
  start_witnesses
  start_signers
  start_nodes
  seed_subject_witnesses 1 validator-1 "$(public_port 1)"
  seed_subject_witnesses 2 validator-2 "$(public_port 2)"
  seed_subject_witnesses 3 validator-3 "$(public_port 3)"
  seed_subject_witnesses 4 validator-4 "$(public_port 4)"
  seed_subject_witnesses 5 observer "$(public_port 5)"
  wait_ready
  wait_converged
  seed_subject_witnesses 1 validator-1 "$(public_port 1)"
  seed_subject_witnesses 2 validator-2 "$(public_port 2)"
  seed_subject_witnesses 3 validator-3 "$(public_port 3)"
  seed_subject_witnesses 4 validator-4 "$(public_port 4)"
  seed_subject_witnesses 5 observer "$(public_port 5)"
  wait_ready
  echo "M0 running: observer http://127.0.0.1:$(public_port 5)/v1/status"
  echo "VALUE_CAP_0; one founder control group; no real-value use."
}

stop_m0() {
  [[ -d "$RUN_DIR" ]] || return 0
  local pid_file pid metadata_status
  local -a live_files=() stale_files=()
  for pid_file in "$RUN_DIR"/*.pid.json; do
    [[ -e "$pid_file" ]] || continue
    if validate_pid_metadata "$pid_file" false; then
      live_files+=("$pid_file")
    else
      metadata_status=$?
      if [[ "$metadata_status" == "1" ]]; then
        stale_files+=("$pid_file")
      else
        echo "refusing to stop any process because identity metadata is unsafe: $pid_file" >&2
        return 1
      fi
    fi
  done
  # Bash 3.2 with nounset treats an empty declared array expansion as unbound.
  # Identity preflight is complete here, so temporarily relax nounset only while
  # consuming the possibly empty stop sets.
  set +u
  for pid_file in "${live_files[@]}"; do
    pid="$(jq -er '.pid' "$pid_file")"
    if ! kill "$pid" 2>/dev/null && process_is_live "$pid"; then
      set -u
      return 1
    fi
  done
  for pid_file in "${live_files[@]}"; do
    pid="$(jq -er '.pid' "$pid_file")"
    local attempt
    for attempt in $(seq 1 100); do
      process_is_live "$pid" || break
      sleep 0.1
    done
    if process_is_live "$pid"; then
      echo "process did not stop; retaining identity metadata: $pid_file" >&2
      set -u
      return 1
    fi
  done
  for pid_file in "${live_files[@]}" "${stale_files[@]}"; do
    [[ -e "$pid_file" ]] && find "$pid_file" -maxdepth 0 -type f -delete
  done
  set -u
  echo "M0 stopped"
}

require_no_process_metadata() {
  local operation="$1"
  local pid_file metadata_status
  for pid_file in "$RUN_DIR"/*.pid.json; do
    [[ -e "$pid_file" ]] || continue
    if validate_pid_metadata "$pid_file"; then
      echo "stop M0 before $operation: $(basename "$pid_file") is running" >&2
    else
      metadata_status=$?
      if [[ "$metadata_status" == "1" ]]; then
        echo "run stop before $operation to clear stale process metadata: $pid_file" >&2
      else
        echo "refusing $operation because process identity metadata is unsafe: $pid_file" >&2
      fi
    fi
    return 1
  done
}

status_m0() {
  validate_installed_artifacts
  local index label url
  for index in 1 2 3 4 5; do
    if [[ "$index" -le 4 ]]; then label="validator-$index"; else label="observer"; fi
    url="http://127.0.0.1:$(public_port "$index")/v1/status"
    if curl --noproxy '*' -fsS "$url" 2>/dev/null \
      | jq -c --arg node "$label" '{node:$node,zone_id:.descriptor.zone_id,height,persistence:.persistence,admission_history:.admission.history_store,state_root:.persistence.state_root,value_cap:.value_risk_policy.current_cap,network_birth,witness:.witness_gate.mode,consensus:.consensus}'; then
      :
    else
      jq -nc --arg node "$label" '{node:$node,running:false}'
    fi
  done
}

heartbeat_m0() {
  validate_installed_artifacts
  require_expected_manifest_pin
  local note="${1:-manual-m0-heartbeat}"
  local note_hash index code target_height="" active_validators=0
  local -a active_nodes=()
  note_hash="$(printf '%s' "$note" | shasum -a 256 | awk '{print $1}')"
  for index in 1 2 3 4; do
    if curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" >/dev/null 2>&1; then
      active_nodes+=("$index")
      active_validators=$((active_validators + 1))
    fi
  done
  [[ "$active_validators" -ge 3 ]] || { echo "heartbeat requires at least three reachable validators" >&2; return 1; }
  if curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port 5)/v1/status" >/dev/null 2>&1; then active_nodes+=(5); fi
  for index in 1 2 3 4; do
    if ! curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" >/dev/null 2>&1; then continue; fi
    code="$(curl --noproxy '*' -sS -o "$RUN_DIR/heartbeat-$index.json" -w '%{http_code}' \
      -H 'content-type: application/json' \
      -X POST "http://127.0.0.1:$(public_port "$index")/v1/network/heartbeats" \
      --data "$(jq -nc --arg note_hash "$note_hash" '{note_hash:$note_hash}')" || true)"
    if [[ "$code" == "201" ]]; then
      target_height="$(curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" | jq -er '.height')"
      echo "heartbeat finalized at height $target_height by validator-$index"
      break
    fi
  done
  [[ -n "$target_height" ]] || {
    echo "no round-zero leader finalized the heartbeat" >&2
    for index in 1 2 3 4; do jq -c . "$RUN_DIR/heartbeat-$index.json" >&2 2>/dev/null || true; done
    return 1
  }
  for index in "${active_nodes[@]}"; do
    local count observed
    for count in $(seq 1 300); do
      observed="$(curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" 2>/dev/null | jq -r '.height // -1' || true)"
      if [[ "$observed" == "$target_height" ]]; then break; fi
      sleep 0.1
    done
    [[ "$observed" == "$target_height" ]] || { echo "node $index did not reach height $target_height" >&2; return 1; }
  done
  for index in "${active_nodes[@]}"; do
    if [[ "$index" -le 4 ]]; then
      seed_subject_witnesses "$index" "validator-$index" "$(public_port "$index")"
    else
      seed_subject_witnesses 5 observer "$(public_port 5)"
    fi
  done
}

expected_process_names() {
  local index witness_index label
  for index in 1 2 3 4; do echo "node-$index"; done
  echo observer
  for index in 1 2 3 4; do echo "signer-$index"; done
  for index in 1 2 3 4 5; do
    if [[ "$index" -le 4 ]]; then label="validator-$index"; else label=observer; fi
    for witness_index in 1 2 3; do echo "witness-$label-$witness_index"; done
  done
}

verify_process_inventory() {
  local expected_count=24 actual_count name file
  actual_count="$(find "$RUN_DIR" -maxdepth 1 -name '*.pid.json' -type f | wc -l | tr -d ' ')"
  [[ "$actual_count" == "$expected_count" ]] || {
    echo "M0 process metadata count differs: expected=$expected_count actual=$actual_count" >&2
    return 1
  }
  while IFS= read -r name; do
    file="$RUN_DIR/$name.pid.json"
    [[ -f "$file" && ! -L "$file" ]] || { echo "M0 process metadata is missing: $name" >&2; return 1; }
    validate_pid_metadata "$file" || { echo "M0 process identity is not live and exact: $name" >&2; return 1; }
  done < <(expected_process_names)
}

verify_m0() {
  validate_installed_artifacts
  require_expected_manifest_pin
  "$BIN_DIR/rld-genesis" verify --manifest "$MANIFEST"
  local running=0 index status_file reference_zone="" reference_height="" reference_root=""
  local genesis_state_root admission_genesis_header admission_benchmark_sha256 manifest_version
  manifest_version="$(jq -er '.declaration.format_version' "$MANIFEST")"
  genesis_state_root="$(jq -er '.declaration.genesis_state_root' "$MANIFEST")"
  admission_genesis_header="$(jq -er '.declaration.admission_genesis.genesis_header' "$MANIFEST")"
  admission_benchmark_sha256="$(jq -er '.declaration.admission_genesis.benchmark_report_sha256' "$MANIFEST")"
  for index in 1 2 3 4 5; do
    status_file="$RUN_DIR/verify-status-$index.json"
    if ! curl --noproxy '*' -fsS "http://127.0.0.1:$(public_port "$index")/v1/status" >"$status_file" 2>/dev/null; then
      continue
    fi
    running=$((running + 1))
    jq -e --argjson validator "$([[ "$index" -le 4 ]] && echo true || echo false)" \
      --arg manifest_version "$manifest_version" \
      --arg genesis_state_root "$genesis_state_root" \
      --arg admission_genesis_header "$admission_genesis_header" \
      --arg admission_benchmark_sha256 "$admission_benchmark_sha256" '
      .descriptor.testnet == false and
      .descriptor.network_domain == "rldcoin:mainnet:v1" and
      .value_risk_policy.current_cap == "VALUE_CAP_0" and
      .value_risk_policy.ever_enabled == false and
      .network_birth.phase == "M0_NETWORK_BIRTH" and
      (if $manifest_version == "RLD-M0-GENESIS-MANIFEST-V2" then
        .network_birth.consensus_rooted_binding.format_version == "RLD-M0-NETWORK-BIRTH-STATE-V2" and
        .network_birth.consensus_rooted_binding.allowed_consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1" and
        .network_birth.active_protocol == null
      elif $manifest_version == "RLD-M0-GENESIS-MANIFEST-V3" then
        .network_birth.consensus_rooted_binding.format_version == "RLD-M0-NETWORK-BIRTH-STATE-V3" and
        .network_birth.consensus_rooted_binding.initial_consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1" and
        .network_birth.active_protocol.format_version == "RLD-M0-ACTIVE-PROTOCOL-V1" and
        .network_birth.active_protocol.consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1" and
        .network_birth.active_protocol.upgrade_sequence == "0" and
        .network_birth.active_protocol.founder_special_slot_ceiling == 1000 and
        .network_birth.active_protocol.last_activated_upgrade == null and
        .network_birth.upgrade_runtime_active == false
      else false end) and
      .network_birth.consensus_rooted_binding.admission_genesis.genesis_header == $admission_genesis_header and
      .network_birth.consensus_rooted_binding.admission_genesis.benchmark_report_sha256 == $admission_benchmark_sha256 and
      .network_birth.single_control_declared == true and
      .network_birth.control_group_count == 1 and
      .network_birth.transferable_value_enabled == false and
      .witness_gate.mode == "READY" and
      .consensus.enabled == $validator and
      .persistence.mode == "EXACT_GENESIS_FULL_WAL_REPLAY" and
      .persistence.exact_genesis_anchor.sequence == 0 and
      .persistence.exact_genesis_anchor.ledger_height == 0 and
      .persistence.exact_genesis_anchor.state_root == $genesis_state_root and
      .persistence.exact_genesis_anchor.last_record_hash == ("0" * 64) and
      .admission.history_store_runtime_instantiated == true and
      .admission.history_store_write_route_active == true and
      .admission.history_store_read_routes_active == true and
      .admission.header_ingress.format == "RLD-ADMISSION-HEADER-INGRESS-V1" and
      .admission.header_ingress.content_type == "application/vnd.rld.admission-header-v1" and
      .admission.header_ingress.limit_bytes == 69208076 and
      .admission.header_ingress.maximum_history_durable_bytes >= 69208076 and
      .admission.header_ingress.max_concurrent >= 1 and
      .admission.authenticated_header_anchor_scheme == "WIRE_V1_CONSENSUS_COMMIT_HASH" and
      .admission.history_store.format_version == 2 and
      .admission.history_store.mode == "EXACT_ADMISSION_GENESIS_FULL_TYPED_WAL_REPLAY" and
      .admission.history_store.sequence >= 0 and
      .admission.history_store.durable_bytes <= .admission.header_ingress.maximum_history_durable_bytes and
      .admission.history_store.poisoned == false and
      .admission.history_store.runtime_tag28_active == false and
      .admission.peer_sync.configured == true and
      .admission.peer_sync.format == "RLD-ADMISSION-INVENTORY-V1" and
      .admission.peer_sync.page_limit == 8 and
      .admission.peer_sync.eclipse_resistant == false and
      .admission.peer_sync.runtime_tag28_active == false and
      .admission.sidecar_fetch.max_concurrent >= 1 and
      .fixed_total_supply_runlai == "100000000000000000000000000000000000"
    ' "$status_file" >/dev/null
    if [[ -z "$reference_zone" ]]; then
      reference_zone="$(jq -er '.descriptor.zone_id' "$status_file")"
      reference_height="$(jq -er '.height' "$status_file")"
      reference_root="$(jq -er '.persistence.state_root' "$status_file")"
    else
      [[ "$(jq -er '.descriptor.zone_id' "$status_file")" == "$reference_zone" ]]
      [[ "$(jq -er '.height' "$status_file")" == "$reference_height" ]]
      [[ "$(jq -er '.persistence.state_root' "$status_file")" == "$reference_root" ]]
    fi
  done
  if [[ "$running" -ne 5 ]]; then
    echo "M0 verification requires exactly 5 responding nodes; observed=$running" >&2
    return 1
  fi
  verify_process_inventory

  local peer_status signer_status expected_key expected_policy_hash
  for index in 1 2 3 4; do
    curl --noproxy '*' -fsS "http://127.0.0.1:$(peer_port "$index")/health" \
      | jq -e --arg zone "$reference_zone" \
        '.status == "healthy" and .consensus_enabled == true and .testnet == false and .zone_id == $zone' \
        >/dev/null || {
      echo "validator-$index peer port is not ready" >&2; return 1;
    }
    peer_status="$RUN_DIR/verify-peer-$index.json"
    local peer_code
    peer_code="$(curl --noproxy '*' -sS -o "$peer_status" -w '%{http_code}' \
      "http://127.0.0.1:$(peer_port "$index")/v1/consensus/status")" || {
      echo "validator-$index peer consensus transport failed" >&2; return 1;
    }
    if [[ "$peer_code" != "200" ]]; then
      echo "validator-$index peer consensus status is unavailable: HTTP $peer_code" >&2
      cat "$peer_status" >&2
      return 1
    fi
    jq -e 'type == "object" and has("enabled") and has("zone_id") and has("signed_head")' "$peer_status" >/dev/null || {
      echo "validator-$index peer consensus port is not ready" >&2; return 1;
    }
    if curl --noproxy '*' -fsS "http://127.0.0.1:$(admin_port "$index")/health" >/dev/null 2>&1; then
      echo "validator-$index unexpectedly exposes an M0 admin listener" >&2
      return 1
    fi
    signer_status="$RUN_DIR/verify-signer-$index.json"
    curl --noproxy '*' -fsS "http://127.0.0.1:$(signer_port "$index")/v1/status" >"$signer_status" || {
      echo "signer-$index is unavailable" >&2; return 1;
    }
    expected_key="$(identity_public_key "$KEY_DIR/validator-$index.json")"
    expected_policy_hash="$(sed -n '1p' "$CONFIG_DIR/policies/validator-$index.sha256")"
    jq -e --arg key "$expected_key" --arg policy "$expected_policy_hash" \
      --arg network "$(jq -er '.declaration.descriptor.network_domain' "$MANIFEST")" \
      --arg zone "$reference_zone" --arg currency "$(jq -er '.declaration.descriptor.currency_genesis_root' "$MANIFEST")" '
      .protocol_version == "RLD-ISOLATED-SIGNER-V1" and .validator_public_key == $key and
      .witness_policy_hash == $policy and .network_domain == $network and .zone_id == $zone and
      .currency_genesis_root == $currency and .protocol_era == 1 and .crypto_era == 1 and
      .allowed_consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1"
    ' "$signer_status" >/dev/null || { echo "signer-$index identity or readiness differs" >&2; return 1; }
    if [[ "$manifest_version" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
      curl --noproxy '*' -fsS "http://127.0.0.1:$(signer_port "$index")/v1/m0/semantic-status" \
        >"$RUN_DIR/verify-signer-semantic-$index.json" || return 1
      jq -e --arg pin "$RLD_M0_EXPECTED_MANIFEST_SHA256" --arg height "$reference_height" --arg root "$reference_root" '
        .format_version == "RLD-M0-SIGNER-SEMANTIC-STATUS-V1" and .manifest_sha256 == $pin and
        .finalized_height == $height and .finalized_state_root == $root and
        (.certified_heartbeats | tostring) == $height and
        .allowed_consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1" and .upgrade_runtime_active == false
      ' "$RUN_DIR/verify-signer-semantic-$index.json" >/dev/null || {
        echo "signer-$index has not independently replayed the exact V3 node head" >&2; return 1;
      }
    fi
  done

  local subject_index witness_index label witness_status expected_operator expected_domain expected_subject
  local signer_count=4 witness_count=0
  for subject_index in 1 2 3 4 5; do
    if [[ "$subject_index" -le 4 ]]; then label="validator-$subject_index"; else label=observer; fi
    expected_policy_hash="$(sed -n '1p' "$CONFIG_DIR/policies/$label.sha256")"
    expected_subject="$(jq -er '.subject_id' "$CONFIG_DIR/policies/$label.json")"
    for witness_index in 1 2 3; do
      curl --noproxy '*' -fsS "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")/health" | grep -Fx ok >/dev/null || {
        echo "witness-$label-$witness_index health is unavailable" >&2; return 1;
      }
      witness_status="$RUN_DIR/verify-witness-$label-$witness_index.json"
      curl --noproxy '*' -fsS "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")/v1/head" >"$witness_status" || {
        echo "witness-$label-$witness_index status is unavailable" >&2; return 1;
      }
      expected_operator="m0-witness-$witness_index"
      expected_domain="founder-control.invalid/witness-$witness_index"
      jq -e --arg policy "$expected_policy_hash" --arg operator "$expected_operator" \
        --arg domain "$expected_domain" --arg subject "$expected_subject" --arg zone "$reference_zone" '
        .protocol_version == "RLD-ROLLBACK-WITNESS-V1" and .policy_hash == $policy and
        .operator_id == $operator and .control_domain == $domain and .head != null and
        .head.checkpoint.node_binding.subject_id == $subject and .head.checkpoint.zone_id == $zone
      ' "$witness_status" >/dev/null || { echo "witness-$label-$witness_index identity or readiness differs" >&2; return 1; }
      if [[ "$manifest_version" == "RLD-M0-GENESIS-MANIFEST-V3" ]]; then
        curl --noproxy '*' -fsS "http://127.0.0.1:$(witness_port "$subject_index" "$witness_index")/v1/m0/semantic-status" \
          >"$RUN_DIR/verify-witness-semantic-$label-$witness_index.json" || return 1
        jq -e --arg pin "$RLD_M0_EXPECTED_MANIFEST_SHA256" --arg policy "$expected_policy_hash" \
          --arg operator "$expected_operator" --arg height "$reference_height" --arg root "$reference_root" '
          .format_version == "RLD-M0-WITNESS-SEMANTIC-STATUS-V1" and .manifest_sha256 == $pin and
          .policy_hash == $policy and .operator_id == $operator and
          .finalized_height == $height and .finalized_state_root == $root and
          (.certified_heartbeats|tostring) == $height and
          .allowed_consensus_profile == "NETWORK_HEARTBEAT_ONLY_V1" and .upgrade_runtime_active == false
        ' "$RUN_DIR/verify-witness-semantic-$label-$witness_index.json" >/dev/null || {
          echo "witness-$label-$witness_index did not independently replay the exact V3 head" >&2; return 1;
        }
      fi
      witness_count=$((witness_count + 1))
    done
  done
  [[ "$signer_count" == "4" && "$witness_count" == "15" ]] || return 1
  echo "M0 verification passed; responding_nodes=$running signers=$signer_count witnesses=$witness_count admin_listeners=0 processes=24"
}

backup_m0() {
  local destination="${1:-}"
  [[ -n "$destination" ]] || { echo "backup requires a destination directory" >&2; exit 1; }
  require_no_process_metadata "taking a consistent backup"
  [[ ! -e "$destination" ]] || { echo "refusing to overwrite backup destination: $destination" >&2; exit 1; }
  validate_installed_artifacts
  require_expected_manifest_pin
  mkdir -p "$destination"
  cp -Rp "$ARTIFACT_DIR" "$CONFIG_DIR" "$KEY_DIR" "$STATE_DIR" "$destination/"
  jq -n \
    --arg artifact_manifest_sha256 "$(shasum -a 256 "$ARTIFACT_MANIFEST" | awk '{print $1}')" \
    --arg manifest_sha256 "$RLD_M0_EXPECTED_MANIFEST_SHA256" \
    '{format:"RLD-M0-BACKUP-V2",artifact_manifest_sha256:$artifact_manifest_sha256,manifest_sha256:$manifest_sha256,value_cap:"VALUE_CAP_0",permanent_genesis_ceremony_executed:false}' \
    >"$destination/BACKUP-METADATA.json"
  (
    cd "$destination"
    find artifacts config keys state -type f -print0 | sort -z | xargs -0 shasum -a 256 >SHA256SUMS
    shasum -a 256 BACKUP-METADATA.json >>SHA256SUMS
  )
  chmod 0700 "$destination"
  echo "sensitive M0 backup created: $destination"
}

verify_backup_tree() {
  local source="$1"
  [[ -f "$source/SHA256SUMS" && ! -L "$source/SHA256SUMS" && \
    -f "$source/BACKUP-METADATA.json" && ! -L "$source/BACKUP-METADATA.json" ]] || {
    echo "backup checksum or metadata file is missing or unsafe" >&2
    return 1
  }
  local directory
  for directory in artifacts config keys state; do
    [[ -d "$source/$directory" && ! -L "$source/$directory" ]] || {
      echo "backup directory is missing or unsafe: $directory" >&2
      return 1
    }
  done
  if find "$source/artifacts" "$source/config" "$source/keys" "$source/state" -type l -print -quit | grep -q .; then
    echo "backup contains a symbolic link" >&2
    return 1
  fi
  local actual_paths listed_paths root_entries
  actual_paths="$(cd "$source" && { find artifacts config keys state -type f -print; echo BACKUP-METADATA.json; } | sort)"
  listed_paths="$(sed -E 's/^[0-9a-f]{64}  //' "$source/SHA256SUMS" | sort)"
  [[ "$actual_paths" == "$listed_paths" ]] || {
    echo "backup checksum inventory does not exactly cover restored files" >&2
    return 1
  }
  root_entries="$(cd "$source" && find . -mindepth 1 -maxdepth 1 -print | sed 's#^./##' | sort)"
  [[ "$root_entries" == $'BACKUP-METADATA.json\nSHA256SUMS\nartifacts\nconfig\nkeys\nstate' ]] || {
    echo "backup root contains unexpected entries" >&2
    return 1
  }
  (cd "$source" && shasum -a 256 -c SHA256SUMS)
}

restore_m0() {
  local source="${1:-}"
  [[ -n "$source" && -f "$source/SHA256SUMS" ]] || { echo "restore requires a verified M0 backup directory" >&2; exit 1; }
  require_no_process_metadata "restore"
  verify_backup_tree "$source"
  require_expected_manifest_pin_for_file "$source/config/genesis-manifest.json"
  jq -e '
    .format == "RLD-M0-BACKUP-V2" and .value_cap == "VALUE_CAP_0" and
    .permanent_genesis_ceremony_executed == false and
    (.artifact_manifest_sha256 | type == "string" and test("^[0-9a-f]{64}$")) and
    (.manifest_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
  ' "$source/BACKUP-METADATA.json" >/dev/null || { echo "backup metadata safety boundary differs" >&2; exit 1; }
  validate_artifact_tree "$source/artifacts"
  [[ "$(jq -er '.artifact_manifest_sha256' "$source/BACKUP-METADATA.json")" == \
    "$(shasum -a 256 "$source/artifacts/install-manifest.json" | awk '{print $1}')" ]] || {
    echo "backup artifact manifest binding differs" >&2
    exit 1
  }
  [[ "$(jq -er '.manifest_sha256' "$source/BACKUP-METADATA.json")" == "$RLD_M0_EXPECTED_MANIFEST_SHA256" ]] || {
    echo "backup metadata does not match the externally pinned M0 manifest" >&2
    exit 1
  }
  local preserved=""
  if [[ -d "$RLD_M0_DIR" ]]; then
    preserved="$RLD_M0_DIR.pre-restore.$(date +%Y%m%d-%H%M%S)"
    mv "$RLD_M0_DIR" "$preserved"
  fi
  mkdir -p "$RLD_M0_DIR"
  cp -Rp "$source/artifacts" "$source/config" "$source/keys" "$source/state" "$RLD_M0_DIR/"
  mkdir -p "$LOG_DIR" "$RUN_DIR"
  validate_installed_artifacts
  require_expected_manifest_pin
  echo "M0 restored from $source"
  if [[ -n "$preserved" ]]; then echo "previous runtime preserved at $preserved"; fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  command="${1:-}"
  case "$command" in
  install) install_release ;;
  init) init_m0 ;;
  build) build_release ;;
  start) start_m0 ;;
  stop) stop_m0 ;;
  status) status_m0 ;;
  heartbeat) heartbeat_m0 "${2:-}" ;;
  verify) verify_m0 ;;
  backup) backup_m0 "${2:-}" ;;
  restore) restore_m0 "${2:-}" ;;
  *) usage; exit 2 ;;
  esac
fi
