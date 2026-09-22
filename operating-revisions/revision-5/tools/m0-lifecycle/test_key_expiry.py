#!/usr/bin/env python3
"""Exercise real expiry supervision through the M0 lifecycle with harmless binaries.

These tests cover process ownership and deadlines. The separate 24-role E2E
checks the same launcher with actual node, signer and witness executables.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
LIFECYCLE = REPO / 'deploy/m0-mainnet.sh'


def expiry(seconds):
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')


def live(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='],
                            capture_output=True, text=True)
    return result.returncode == 0 and bool(result.stdout.strip()) and 'Z' not in result.stdout


class KeyExpiry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix='rld-expiry-fixture-')
        source = Path(cls.fixture.name) / 'idle.c'
        source.write_text('#include <unistd.h>\nint main(void) { for (;;) pause(); }\n')
        cls.idle = source.with_suffix('')
        subprocess.run(['cc', str(source), '-o', str(cls.idle)], check=True,
                       capture_output=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rld expiry ')
        self.root = Path(self.temp.name)
        self.binary = self.root / 'artifacts/bin/rldd'
        self.binary.parent.mkdir(parents=True)
        shutil.copy(self.idle, self.binary)
        self.digest = hashlib.sha256(self.binary.read_bytes()).hexdigest()
        (self.root / 'artifacts/install-manifest.json').write_text(json.dumps({
            'artifacts': [{'name': 'rldd', 'sha256': self.digest}],
        }))
        self.supervisor = self.root / 'artifacts/source/tree/deploy/run-with-key-expiry.py'
        self.supervisor.parent.mkdir(parents=True)
        shutil.copy2(REPO / 'deploy/run-with-key-expiry.py', self.supervisor)
        for name in ('run', 'logs'):
            (self.root / name).mkdir()
        self.metadata = self.root / 'run/node-1.pid.json'
        self.environment = {**os.environ, 'RLD_M0_DIR': str(self.root),
                            'RLD_M0_KEY_EXPIRES_AT': expiry(120)}
        self.owned = []

    def tearDown(self):
        # Only PIDs retained from our own successful launches, never a tampered
        # metadata file. Do not leave helpers running after an assertion failure.
        for pid in self.owned:
            if live(pid):
                os.kill(pid, signal.SIGTERM)
        for pid in self.owned:
            deadline = time.monotonic() + 7
            while live(pid) and time.monotonic() < deadline:
                time.sleep(.05)
            if live(pid):
                os.kill(pid, signal.SIGKILL)
        self.temp.cleanup()

    def shell(self, script, environment=None):
        return subprocess.run(['bash', '-c', 'source "$1"\n' + script,
                               'test', str(LIFECYCLE)],
                              env=self.environment if environment is None else environment,
                              capture_output=True, text=True, timeout=20)

    def start(self):
        result = self.shell('require_software_key_exception\nstart_process node-1 "$BIN_DIR/rldd" 120')
        if self.metadata.exists():
            data = json.loads(self.metadata.read_text())
            self.owned += [data['pid'], data['software_key_exception']['supervisor']['pid']]
        return result

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_normal_start_tracks_actual_child_and_stop_reaps_it(self):
        self.assert_ok(self.start())
        data = json.loads(self.metadata.read_text())
        self.assertNotEqual(data['pid'], data['software_key_exception']['supervisor']['pid'])
        self.assert_ok(self.shell('validate_pid_metadata "$RUN_DIR/node-1.pid.json"'))
        self.assert_ok(self.shell('stop_m0'))
        self.assertFalse(live(data['pid']))
        self.assertFalse(self.metadata.exists())

    def test_missing_malformed_expired_and_long_exception_never_start(self):
        for value in (None, 'invalid', expiry(-1), expiry(32 * 86400)):
            with self.subTest(value=value):
                environment = dict(self.environment)
                if value is None:
                    environment.pop('RLD_M0_KEY_EXPIRES_AT')
                else:
                    environment['RLD_M0_KEY_EXPIRES_AT'] = value
                result = self.shell('require_software_key_exception\nstart_process node-1 "$BIN_DIR/rldd" 120', environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.metadata.exists())
                self.assertEqual(list((self.root / 'run').iterdir()), [])

    def test_running_child_stops_at_expiry_and_cannot_restart(self):
        self.environment['RLD_M0_KEY_EXPIRES_AT'] = expiry(6)
        self.assert_ok(self.start())
        deadline = time.monotonic() + 9
        while live(self.owned[0]) and time.monotonic() < deadline:
            time.sleep(.05)
        self.assertFalse(live(self.owned[0]))
        self.assertNotEqual(self.start().returncode, 0)
        self.assert_ok(self.shell('stop_m0'))

    def test_executable_tampering_never_starts(self):
        with self.binary.open('ab') as file:
            file.write(b'changed')
        result = self.start()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('executable hash mismatch', result.stderr)
        self.assertFalse(self.metadata.exists())

    def test_supervisor_metadata_substitution_rejected_but_stop_available(self):
        self.assert_ok(self.start())
        data = json.loads(self.metadata.read_text())
        data['software_key_exception']['supervisor']['pid'] = os.getpid()
        self.metadata.write_text(json.dumps(data))
        self.assertNotEqual(self.shell('validate_pid_metadata "$RUN_DIR/node-1.pid.json"').returncode, 0)
        self.assert_ok(self.shell('stop_m0'))
        self.assertFalse(live(self.owned[0]))

    def test_dead_supervisor_is_not_healthy_and_child_can_be_stopped(self):
        self.assert_ok(self.start())
        os.kill(self.owned[1], signal.SIGKILL)
        deadline = time.monotonic() + 2
        while live(self.owned[1]) and time.monotonic() < deadline:
            time.sleep(.05)
        self.assertNotEqual(self.shell('validate_pid_metadata "$RUN_DIR/node-1.pid.json"').returncode, 0)
        if sys.platform == 'linux':
            deadline = time.monotonic() + 3
            while live(self.owned[0]) and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertFalse(live(self.owned[0]), 'Linux parent-death guard left the role alive')
        self.assert_ok(self.shell('stop_m0'))
        self.assertFalse(live(self.owned[0]))

    def test_child_pid_substitution_is_never_signalled(self):
        self.assert_ok(self.start())
        original = self.metadata.read_text()
        data = json.loads(original)
        data['pid'] = os.getpid()
        self.metadata.write_text(json.dumps(data))
        self.assertNotEqual(self.shell('stop_m0').returncode, 0)
        self.assertTrue(live(self.owned[0]))
        self.metadata.write_text(original)
        self.assert_ok(self.shell('stop_m0'))

    def test_supervisor_term_reaps_child(self):
        self.assert_ok(self.start())
        os.kill(self.owned[1], signal.SIGTERM)
        deadline = time.monotonic() + 7
        while live(self.owned[0]) and time.monotonic() < deadline:
            time.sleep(.05)
        self.assertFalse(live(self.owned[0]))
        self.assert_ok(self.shell('stop_m0'))

    def test_expiry_during_binary_verification_never_launches(self):
        spec = importlib.util.spec_from_file_location('expiry_supervisor', self.supervisor)
        supervisor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(supervisor)
        file_digest = hashlib.file_digest

        def slow_digest(*args):
            result = file_digest(*args)
            time.sleep(3)
            return result

        arguments = ['supervisor', '--expires-at', expiry(2), '--binary-sha256',
                     self.digest, '--', str(self.binary)]
        with mock.patch.object(supervisor.sys, 'argv', arguments), \
                mock.patch.object(supervisor.hashlib, 'file_digest', side_effect=slow_digest) as digest, \
                mock.patch.object(supervisor.subprocess, 'Popen') as launch:
            self.assertEqual(supervisor.main(), 78)
            digest.assert_called_once()
            launch.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
