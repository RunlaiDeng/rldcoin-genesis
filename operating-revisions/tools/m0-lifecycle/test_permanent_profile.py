#!/usr/bin/env python3
"""Actual Ed25519 designation and scope checks; no live identity or deployment."""
import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

PROGRAM = Path(__file__).resolve().parents[2] / "deploy/permanent-m0.py"
spec = importlib.util.spec_from_file_location("permanent", PROGRAM)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PermanentProfile(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ["config", "artifacts/source"]:
            (self.root / name).mkdir(parents=True)
        self.key = Ed25519PrivateKey.generate()
        pub = self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
        self.pin = "a" * 64
        report = {"qualified_profile": module.PROFILE, "remote_genesis_profile_qualified": True}
        self.write("config/admission-benchmark-report.json", report)
        report_hash = module.digest(self.root / "config/admission-benchmark-report.json")
        self.write("config/genesis-manifest.json", {
            "manifest_sha256": self.pin,
            "declaration": {"founder_public_key": pub, "descriptor": {"zone_id": "fixture"},
                            "genesis_state_root": "b" * 64,
                            "admission_genesis": {"benchmark_report_sha256": report_hash}}})
        self.write("artifacts/install-manifest.json", {"fixture": True})
        self.write("artifacts/source/manifest.json", {"fixture": True})
        self.statement = {
            "format": "RLD-PERMANENT-GENESIS-DESIGNATION-V1", "profile": module.PROFILE,
            "manifest_sha256": self.pin, "founder_public_key": pub,
            "control_group_count": 1, "value_cap": "VALUE_CAP_0",
            "transferable_value_enabled": False, "reward_issuance_enabled": False,
            "independent_review_complete": False, "physical_offline_custody": False,
            "genesis_premine_runlai": "0", "total_supply_runlai": str(10**35),
            "zone_id": "fixture", "genesis_state_root": "b" * 64,
            "admission_report_sha256": report_hash, "operator_program_sha256": module.digest(PROGRAM),
            "designated_at": "2026-09-22T00:00:00Z", "software_key_expires_at": "2026-10-07T16:00:00Z",
        }
        for field, path in [("manifest_file_sha256", "config/genesis-manifest.json"),
                            ("installed_artifacts_sha256", "artifacts/install-manifest.json"),
                            ("source_manifest_sha256", "artifacts/source/manifest.json")]:
            self.statement[field] = module.digest(self.root / path)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, value):
        (self.root / name).write_bytes(module.canonical(value))

    def signed(self, statement=None):
        statement = self.statement if statement is None else statement
        return {"statement": copy.deepcopy(statement),
                "signature": self.key.sign(module.DOMAIN + module.canonical(statement)).hex()}

    def test_valid_and_wrong_external_pin(self):
        record = self.signed()
        self.assertEqual(module.verify(self.root, self.pin, record), self.statement)
        with self.assertRaises(ValueError):
            module.verify(self.root, "c" * 64, record)

    def test_payload_tamper_and_wrong_signature(self):
        record = self.signed(); record["statement"]["zone_id"] = "changed"
        with self.assertRaises(Exception):
            module.verify(self.root, self.pin, record)
        record = self.signed(); record["signature"] = "00" * 64
        with self.assertRaises(Exception):
            module.verify(self.root, self.pin, record)

    def test_even_founder_cannot_sign_out_of_profile_claims(self):
        mutations = {"value_cap": "VALUE_CAP_1", "transferable_value_enabled": True,
                     "reward_issuance_enabled": True, "genesis_premine_runlai": "1",
                     "control_group_count": 2, "independent_review_complete": True,
                     "physical_offline_custody": True, "total_supply_runlai": "1",
                     "software_key_expires_at": "2027-01-01T00:00:00Z",
                     "operator_program_sha256": "0" * 64}
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = {**self.statement, field: value}
                with self.assertRaises(ValueError):
                    module.verify(self.root, self.pin, self.signed(changed))

    def test_scoped_operating_revision_preserves_designation(self):
        self.statement["operator_program_sha256"] = "d" * 64
        record = self.signed()
        revision = {
            "format": "RLD-M0-OPERATIONS-AUTHORIZATION-V1", "revision": 1,
            "manifest_sha256": self.pin,
            "designation_sha256": hashlib.sha256(module.canonical(record)).hexdigest(),
            "previous_operator_program_sha256": "d" * 64,
            "operator_program_sha256": module.digest(PROGRAM),
            "heartbeat_interval_seconds": 600, "value_cap": "VALUE_CAP_0",
            "reward_issuance_enabled": False,
            "software_key_expires_at": self.statement["software_key_expires_at"],
            "authorized_at": "2026-09-22T01:00:00Z",
        }
        def authorize(value):
            self.write("config/operations-authorization.json", {
                "statement": value, "signature": self.key.sign(
                    module.OPERATIONS_DOMAIN + module.canonical(value)).hex()})
        authorize(revision)
        result = module.verify(self.root, self.pin, record)
        self.assertEqual(result["heartbeat_interval_seconds"], 600)
        self.assertEqual(record, self.signed())
        for field, value in {"heartbeat_interval_seconds": 60,
                             "designation_sha256": "e" * 64,
                             "software_key_expires_at": "2026-10-08T16:00:00Z",
                             "operator_program_sha256": "f" * 64,
                             "reward_issuance_enabled": True,
                             "authorized_at": "2026-09-21T00:00:00Z"}.items():
            with self.subTest(field=field):
                authorize({**revision, field: value})
                with self.assertRaises(ValueError):
                    module.verify(self.root, self.pin, record)
        authorize(revision)
        corrupted = module.read(self.root / "config/operations-authorization.json")
        corrupted["statement"]["heartbeat_interval_seconds"] = 60
        self.write("config/operations-authorization.json", corrupted)
        with self.assertRaises(Exception):
            module.verify(self.root, self.pin, record)

    def test_timeout_revision_chain_and_preserved_launch_arguments(self):
        self.statement["operator_program_sha256"] = "d" * 64
        record = self.signed()
        first = {
            "format": "RLD-M0-OPERATIONS-AUTHORIZATION-V1", "revision": 1,
            "manifest_sha256": self.pin,
            "designation_sha256": hashlib.sha256(module.canonical(record)).hexdigest(),
            "previous_operator_program_sha256": "d" * 64,
            "operator_program_sha256": "c" * 64,
            "heartbeat_interval_seconds": 600, "value_cap": "VALUE_CAP_0",
            "reward_issuance_enabled": False,
            "software_key_expires_at": self.statement["software_key_expires_at"],
            "authorized_at": "2026-09-22T01:00:00Z",
        }
        def envelope(value):
            return {"statement": value, "signature": self.key.sign(
                module.OPERATIONS_DOMAIN + module.canonical(value)).hex()}
        first_record = envelope(first)
        self.write("config/operations-authorization.json", first_record)
        second = {**first, "revision": 2, "operator_program_sha256": module.digest(PROGRAM),
                  "previous_authorization_sha256": hashlib.sha256(module.canonical(first_record)).hexdigest(),
                  "previous_authorized_program_sha256": "c" * 64,
                  "node_consensus_timeout_ms": 30000, "node_admission_timeout_ms": 30000,
                  "node_witness_timeout_ms": 10000, "node_witness_poll_interval_ms": 1000}
        self.write("config/operations-authorization-2.json", envelope(second))
        self.assertEqual(module.verify(self.root, self.pin, record)["operations_revision"], 2)
        for field, value in {"node_consensus_timeout_ms": 1,
                             "previous_authorization_sha256": "e" * 64,
                             "reward_issuance_enabled": True}.items():
            self.write("config/operations-authorization-2.json", envelope({**second, field: value}))
            with self.assertRaises(ValueError):
                module.verify(self.root, self.pin, record)
        self.write("config/operations-authorization-2.json", envelope(second))
        first_record["signature"] = "00" * 64
        self.write("config/operations-authorization.json", first_record)
        with self.assertRaises(Exception):
            module.verify(self.root, self.pin, record)
        library = self.root / "library.sh"
        library.write_text("start_process() { printf '%s\\n' \"$@\"; }\n"
                           "start_m0() { start_process node-1 /retained/bin/rldd "
                           "--m0-genesis-manifest-sha256 pinned --consensus-timeout-ms 2000 "
                           "--admission-peer-timeout-ms 2000 --witness-timeout-ms 1000 "
                           "--witness-poll-interval-ms 100 --testnet false; }\n")
        actual = subprocess.check_output(["bash", "-c", module.START_WITH_BOUNDED_TIMEOUTS,
                                          "bash", str(library)], text=True).splitlines()
        self.assertEqual(actual, ["node-1", "/retained/bin/rldd", "--m0-genesis-manifest-sha256",
                                  "pinned", "--consensus-timeout-ms", "30000",
                                  "--admission-peer-timeout-ms", "30000", "--witness-timeout-ms",
                                  "10000", "--witness-poll-interval-ms", "1000", "--testnet", "false"])

    def test_changed_artifact_and_duplicate_json_rejected(self):
        record = self.signed()
        self.write("artifacts/install-manifest.json", {"different": True})
        with self.assertRaises(ValueError):
            module.verify(self.root, self.pin, record)
        path = self.root / "duplicate.json"; path.write_text('{"x":1,"x":2}')
        with self.assertRaises(ValueError):
            module.read(path)


if __name__ == "__main__":
    unittest.main()
