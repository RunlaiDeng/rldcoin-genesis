#!/usr/bin/env python3
"""Signed authorization and real supervised-process tests; fixture identities only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
import test_permanent_profile as fixtures
module, PROGRAM = fixtures.module, fixtures.PROGRAM
from test_key_expiry import live


class ContinuingAuthorization(unittest.TestCase):
    write = fixtures.PermanentProfile.write
    signed = fixtures.PermanentProfile.signed

    @classmethod
    def setUpClass(cls):
        cls.compile_dir = tempfile.TemporaryDirectory()
        source = Path(cls.compile_dir.name) / 'idle.c'
        source.write_text('#include <unistd.h>\nint main(void) { for (;;) pause(); }\n')
        cls.idle = source.with_suffix('')
        subprocess.run(['cc', str(source), '-o', str(cls.idle)], check=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.compile_dir.cleanup()

    def setUp(self):
        fixtures.PermanentProfile.setUp(self)
        for name in ('artifacts/bin', 'run', 'logs'):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.binary = self.root / 'artifacts/bin/rldd'
        shutil.copy2(self.idle, self.binary)
        self.write('artifacts/install-manifest.json', {'artifacts': [
            {'name': 'rldd', 'sha256': module.digest(self.binary)}]})
        self.statement['installed_artifacts_sha256'] = module.digest(self.root / 'artifacts/install-manifest.json')
        # The original authorization expired years ago: only the signed successor
        # authorizes current process launch, with no fake future expiry.
        self.statement.update(operator_program_sha256='d' * 64,
            designated_at='2020-01-01T00:00:00Z', software_key_expires_at='2020-01-16T00:00:00Z')
        original = self.signed()
        self.write('config/permanent-genesis.json', original)
        previous = None
        for number in range(1, 6):
            s = dict(format='RLD-M0-OPERATIONS-AUTHORIZATION-V1', revision=number,
                manifest_sha256=self.pin, designation_sha256=hashlib.sha256(module.canonical(original)).hexdigest(),
                previous_operator_program_sha256='d' * 64,
                operator_program_sha256=module.digest(PROGRAM) if number == 5 else str(number) * 64,
                heartbeat_interval_seconds=600, value_cap='VALUE_CAP_0', reward_issuance_enabled=False,
                software_key_expires_at=self.statement['software_key_expires_at'], authorized_at='2020-01-02T00:00:00Z')
            if previous:
                s.update(previous_authorization_sha256=hashlib.sha256(module.canonical(previous)).hexdigest(),
                    previous_authorized_program_sha256=previous['statement']['operator_program_sha256'],
                    node_consensus_timeout_ms=30000, node_admission_timeout_ms=30000,
                    node_witness_timeout_ms=10000, node_witness_poll_interval_ms=1000)
            if number >= 3:
                s.update(module.RECOVERY_POLICY)
            if number >= 4:
                s['post_commit_checkpoint_sync'] = 'RETAINED_SEMANTIC_SYNC_V1'
            if number == 5:
                s.update(key_authorization_mode='UNTIL_REVOKED', software_key_expires_at=None,
                    supervisor_program_sha256=module.digest(module.GUARD), revocation_file=module.REVOCATION_FILE)
            previous = self.envelope(s)
            name = 'operations-authorization' + (f'-{number}' if number > 1 else '') + '.json'
            self.write('config/' + name, previous)
        self.permit = s
        self.metadata = self.root / 'run/node-1.pid.json'
        self.env = {**os.environ, 'RLD_M0_DIR': str(self.root), 'RLD_M0_EXPECTED_MANIFEST_SHA256': self.pin,
            'RLD_M0_KEY_EXPIRES_AT': 'UNTIL_REVOKED', 'RLD_M0_AUTHORIZATION_GUARD': str(module.GUARD)}
        self.owned = []

    def envelope(self, s):
        return {'statement': s, 'signature': self.key.sign(module.OPERATIONS_DOMAIN + module.canonical(s)).hex()}

    def tearDown(self):
        for pid in reversed(self.owned):
            if live(pid):
                os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + 7
        while any(live(pid) for pid in self.owned) and time.monotonic() < deadline:
            time.sleep(.1)
        for pid in self.owned:
            if live(pid):
                os.kill(pid, signal.SIGKILL)
        self.temp.cleanup()

    def shell(self, command):
        return subprocess.run(['bash', '-c', 'source "$1"\n' + module.CONTINUING_LIFECYCLE + '\n' + command,
            'test', str(PROGRAM.with_name('m0-mainnet.sh'))], env=self.env, capture_output=True, text=True, timeout=30)

    def start(self):
        r = self.shell('require_software_key_exception\nstart_process node-1 "$BIN_DIR/rldd"')
        if self.metadata.exists():
            m = json.loads(self.metadata.read_text())
            self.owned.extend([m['pid'], m['software_key_exception']['supervisor']['pid']])
        return r

    def assert_ok(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def await_stopped(self):
        deadline = time.monotonic() + 8
        while live(self.owned[0]) and time.monotonic() < deadline:
            time.sleep(.1)
        self.assertFalse(live(self.owned[0]))

    def test_expired_original_runs_under_signed_successor_and_stops_cleanly(self):
        original_hash = module.digest(self.root / 'config/permanent-genesis.json')
        result = module.verify(self.root, self.pin)
        self.assertIsNone(result['software_key_expires_at'])
        self.assertEqual(result['operations_revision'], 5)
        self.assert_ok(self.start())
        time.sleep(1.2)
        self.assertTrue(live(self.owned[0]))
        self.assert_ok(self.shell('validate_pid_metadata "$RUN_DIR/node-1.pid.json"'))
        self.assert_ok(self.shell('stop_m0'))
        self.await_stopped()
        self.assertEqual(module.digest(self.root / 'config/permanent-genesis.json'), original_hash)

    def test_revocation_stops_running_role_and_prevents_restart(self):
        self.assert_ok(self.start())
        (self.root / module.REVOCATION_FILE).touch()
        self.await_stopped()
        self.assertNotEqual(self.start().returncode, 0)
        self.assert_ok(self.shell('stop_m0'))

    def test_changed_authorization_stops_running_role(self):
        self.assert_ok(self.start())
        self.write('config/operations-authorization-5.json', {'changed': True})
        self.await_stopped()
        self.assertNotEqual(self.start().returncode, 0)
        self.assert_ok(self.shell('stop_m0'))

    def test_missing_signature_wrong_pin_and_signed_scope_changes_fail_closed(self):
        path = self.root / 'config/operations-authorization-5.json'
        original = path.read_bytes()
        for field, value in {'software_key_expires_at': '2099-01-01T00:00:00Z',
            'key_authorization_mode': 'UNLIMITED', 'reward_issuance_enabled': True,
            'previous_authorization_sha256': '0' * 64, 'supervisor_program_sha256': '0' * 64,
            'revocation_file': 'elsewhere', 'authorized_at': '2021-01-01T00:00:00Z'}.items():
            with self.subTest(field=field):
                self.write('config/operations-authorization-5.json', self.envelope({**self.permit, field: value}))
                with self.assertRaises(ValueError):
                    module.verify(self.root, self.pin)
        path.write_bytes(original)
        with self.assertRaises(ValueError):
            module.verify(self.root, 'f' * 64)
        record = json.loads(original); record['signature'] = '00' * 64
        self.write('config/operations-authorization-5.json', record)
        self.assertNotEqual(self.start().returncode, 0)
        path.unlink()
        self.assertNotEqual(self.start().returncode, 0)
        self.assertFalse(self.metadata.exists())

    def test_binary_tamper_and_revocation_symlink_refuse_launch(self):
        with self.binary.open('ab') as f:
            f.write(b'changed')
        self.assertNotEqual(self.start().returncode, 0)
        (self.root / module.REVOCATION_FILE).symlink_to(self.root / 'nonexistent')
        with self.assertRaises(ValueError):
            module.verify(self.root, self.pin)
        self.assertFalse(self.metadata.exists())

    def test_supervisor_death_stops_child_and_metadata_substitution_is_rejected(self):
        self.assert_ok(self.start())
        record = json.loads(self.metadata.read_text())
        record['software_key_exception']['supervisor']['pid'] = os.getpid()
        self.metadata.write_text(json.dumps(record))
        self.assertNotEqual(self.shell('validate_pid_metadata "$RUN_DIR/node-1.pid.json"').returncode, 0)
        os.kill(self.owned[1], signal.SIGKILL)
        self.await_stopped()
        self.assert_ok(self.shell('stop_m0'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
