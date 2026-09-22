#!/usr/bin/env python3
"""Operate an explicitly designated, zero-value M0 identity; never initialize it."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import urllib.request

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

DOMAIN = b"RLD-PERMANENT-GENESIS-DESIGNATION-V1\0"
PROFILE = "P1_REMOTE_ZERO_VALUE_V1"
OPERATIONS_DOMAIN = b"RLD-M0-OPERATIONS-AUTHORIZATION-V1\0"


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("missing, unsafe or oversized public record")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("duplicate JSON member")
            result[k] = v
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(root, expected_pin, record=None):
    if record is None:
        record = read(root / "config/permanent-genesis.json")
    if set(record) != {"statement", "signature"}:
        raise ValueError("invalid designation envelope")
    s = record["statement"]
    manifest_path = root / "config/genesis-manifest.json"
    manifest = read(manifest_path)
    founder = manifest["declaration"]["founder_public_key"]
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(founder)).verify(
        bytes.fromhex(record["signature"]), DOMAIN + canonical(s))
    fixed = {
        "format": "RLD-PERMANENT-GENESIS-DESIGNATION-V1", "profile": PROFILE,
        "manifest_sha256": expected_pin, "founder_public_key": founder,
        "control_group_count": 1, "value_cap": "VALUE_CAP_0",
        "transferable_value_enabled": False, "reward_issuance_enabled": False,
        "independent_review_complete": False, "physical_offline_custody": False,
        "genesis_premine_runlai": "0", "total_supply_runlai": str(10**35),
    }
    for k, v in fixed.items():
        if type(s.get(k)) is not type(v) or s[k] != v:
            raise ValueError("designation scope mismatch: " + k)
    born = datetime.strptime(s["designated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    expires = datetime.strptime(s["software_key_expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if not 0 < (expires - born).total_seconds() <= 31 * 86400:
        raise ValueError("designation needs a bounded software-key exception")
    if (s["manifest_sha256"] != manifest["manifest_sha256"]
            or s["zone_id"] != manifest["declaration"]["descriptor"]["zone_id"]
            or s["genesis_state_root"] != manifest["declaration"]["genesis_state_root"]):
        raise ValueError("designation identity mismatch")
    for field, path in {
        "manifest_file_sha256": manifest_path,
        "installed_artifacts_sha256": root / "artifacts/install-manifest.json",
        "admission_report_sha256": root / "config/admission-benchmark-report.json",
        "source_manifest_sha256": root / "artifacts/source/manifest.json",
    }.items():
        if s[field] != digest(path):
            raise ValueError("designation artifact mismatch: " + field)
    if s["admission_report_sha256"] != manifest["declaration"]["admission_genesis"]["benchmark_report_sha256"]:
        raise ValueError("signed admission report mismatch")
    report = read(root / "config/admission-benchmark-report.json")
    if report.get("qualified_profile") != PROFILE or report.get("remote_genesis_profile_qualified") is not True:
        raise ValueError("unqualified remote genesis inputs")
    if s["operator_program_sha256"] != digest(__file__):
        def check_revision(authorization, program_hash, number, extra=None):
            if set(authorization) != {"statement", "signature"}:
                raise ValueError("invalid operations authorization envelope")
            revision = authorization["statement"]
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(founder)).verify(
                bytes.fromhex(authorization["signature"]), OPERATIONS_DOMAIN + canonical(revision))
            expected = {
                "format": "RLD-M0-OPERATIONS-AUTHORIZATION-V1", "revision": number,
                "manifest_sha256": expected_pin,
                "designation_sha256": hashlib.sha256(canonical(record)).hexdigest(),
                "previous_operator_program_sha256": s["operator_program_sha256"],
                "operator_program_sha256": program_hash,
                "heartbeat_interval_seconds": 600,
                "value_cap": "VALUE_CAP_0", "reward_issuance_enabled": False,
                "software_key_expires_at": s["software_key_expires_at"],
                **(extra or {}),
            }
            if set(revision) != set(expected) | {"authorized_at"}:
                raise ValueError("unexpected operations authorization fields")
            for key, value in expected.items():
                if type(revision[key]) is not type(value) or revision[key] != value:
                    raise ValueError("operations authorization scope mismatch: " + key)
            authorized = datetime.strptime(revision["authorized_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if not born <= authorized < expires:
                raise ValueError("operations authorization outside key exception")
            return authorized
        first = read(root / "config/operations-authorization.json")
        second_path = root / "config/operations-authorization-2.json"
        if second_path.exists() or second_path.is_symlink():
            second = read(second_path)
            previous_hash = first["statement"]["operator_program_sha256"]
            first_time = check_revision(first, previous_hash, 1)
            second_time = check_revision(second, digest(__file__), 2, {
                "previous_authorization_sha256": hashlib.sha256(canonical(first)).hexdigest(),
                "previous_authorized_program_sha256": previous_hash,
                "node_consensus_timeout_ms": 30000, "node_admission_timeout_ms": 30000,
                "node_witness_timeout_ms": 10000, "node_witness_poll_interval_ms": 1000,
            })
            if second_time < first_time:
                raise ValueError("operating revisions out of order")
            return {**s, "heartbeat_interval_seconds": 600, "operations_revision": 2}
        check_revision(first, digest(__file__), 1)
        return {**s, "heartbeat_interval_seconds": 600, "operations_revision": 1}
    return s


# Only launch-time waiting/polling arguments change. The retained lifecycle still
# validates artifacts, pins, process identities, signer gates and checkpoints.
START_WITH_BOUNDED_TIMEOUTS = r"""
source "$1"
eval "$(declare -f start_process | sed '1s/start_process/qualified_start_process/')"
start_process() {
  local -a adjusted=()
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --consensus-timeout-ms|--admission-peer-timeout-ms)
        [[ "$#" -ge 2 ]] || return 1; adjusted+=("$1" 30000); shift 2 ;;
      --witness-timeout-ms)
        [[ "$#" -ge 2 ]] || return 1; adjusted+=("$1" 10000); shift 2 ;;
      --witness-poll-interval-ms)
        [[ "$#" -ge 2 ]] || return 1; adjusted+=("$1" 1000); shift 2 ;;
      *) adjusted+=("$1"); shift ;;
    esac
  done
  qualified_start_process "${adjusted[@]}"
}
start_m0
"""


def main():
    os.umask(0o077)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["seal", "verify", "run"])
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--pin", required=True)
    p.add_argument("--statement", type=Path)
    p.add_argument("--public-status", type=Path)
    p.add_argument("--port-base", type=int, default=48000)
    a = p.parse_args(); root = a.root.resolve()
    if a.command == "seal":
        statement = read(a.statement)
        key = read(root / "keys/founder.json")
        private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key["secret_key"]))
        assert private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex() == key["public_key"]
        record = {"statement": statement, "signature": private.sign(DOMAIN + canonical(statement)).hex()}
        verify(root, a.pin, record)
        target = root / "config/permanent-genesis.json"
        # Exclusive creation; a permanent designation cannot be overwritten.
        with target.open("xb") as f:
            f.write(canonical(record)); f.flush(); os.fsync(f.fileno())
        verify(root, a.pin)
        print("PASS_SIGNED_PERMANENT_DESIGNATION")
        return
    s = verify(root, a.pin)
    if a.command == "verify":
        print(json.dumps({"result": "PASS_PERMANENT_DESIGNATION", "manifest_sha256": a.pin, "profile": PROFILE}))
        return
    if not a.public_status:
        raise ValueError("public status path required")
    env = dict(os.environ, RLD_M0_DIR=str(root), RLD_M0_PORT_BASE=str(a.port_base),
               RLD_M0_BIND="127.0.0.1", RLD_M0_EXPECTED_MANIFEST_SHA256=a.pin,
               RLD_M0_ZONE_NAME=read(root / "config/genesis-manifest.json")["declaration"]["descriptor"]["display_name"],
               RLD_M0_KEY_EXPIRES_AT=s["software_key_expires_at"],
               NO_PROXY="127.0.0.1,localhost,::1", no_proxy="127.0.0.1,localhost,::1")
    script = root / "artifacts/source/tree/deploy/m0-mainnet.sh"
    deadline = datetime.fromisoformat(s["software_key_expires_at"].replace("Z", "+00:00")).timestamp()
    running = True
    def stop_signal(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop_signal); signal.signal(signal.SIGINT, stop_signal)
    def call(op):
        command = ["bash", str(script), op]
        if op == "start" and s.get("operations_revision") == 2:
            command = ["bash", "-c", START_WITH_BOUNDED_TIMEOUTS, "bash", str(script)]
        subprocess.run(command, env=env, check=True, timeout=240)
    last = {}
    last_verified_at = None
    interval = s.get("heartbeat_interval_seconds", 60)
    def publish(state):
        nonlocal last
        if state == "RUNNING":
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
                    f"http://127.0.0.1:{a.port_base+1}/v1/status", timeout=10) as r:
                node = json.load(r)
            if node["value_risk_policy"]["current_cap"] != "VALUE_CAP_0":
                raise ValueError("unexpected value activation")
            last = {"height": node["height"], "state_root": node["persistence"]["state_root"]}
        payload = {**last, "state": state, "observed_at": datetime.now(timezone.utc).isoformat(),
                   "manifest_sha256": a.pin, "zone_id": s["zone_id"], "profile": PROFILE,
                   "value_cap": "VALUE_CAP_0", "reward_issuance_enabled": False,
                   "heartbeat_interval_seconds": interval, "last_full_verification_at": last_verified_at,
                   "operations_revision": s.get("operations_revision", 0),
                   "control_group_count": 1, "software_key_expires_at": s["software_key_expires_at"]}
        temp = a.public_status.with_suffix(".tmp")
        with temp.open("wb") as f:
            f.write(canonical(payload)); f.flush(); os.fsync(f.fileno())
        temp.chmod(0o644); os.replace(temp, a.public_status)
    try:
        call("stop")
        if time.time() >= deadline:
            publish("KEY_EXCEPTION_EXPIRED"); return
        call("start"); call("verify")
        last_verified_at = datetime.now(timezone.utc).isoformat()
        publish("RUNNING")
        next_heartbeat = time.monotonic() + interval
        next_observation = time.monotonic() + 30
        while running and time.time() < deadline:
            if time.monotonic() >= next_heartbeat:
                call("heartbeat"); call("verify")
                last_verified_at = datetime.now(timezone.utc).isoformat()
                publish("RUNNING")
                next_heartbeat = time.monotonic() + interval
            if time.monotonic() >= next_observation:
                publish("RUNNING")
                next_observation = time.monotonic() + 30
            time.sleep(1)
    finally:
        call("stop")
        publish("KEY_EXCEPTION_EXPIRED" if time.time() >= deadline else "STOPPED")


if __name__ == "__main__":
    main()
