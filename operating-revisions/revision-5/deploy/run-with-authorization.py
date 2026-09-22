#!/usr/bin/env python3
"""Supervise one retained role under a signed, revocable operating authorization.

No fixed calendar expiry. This is software custody, not a hardware security
boundary against the machine owner. A revoked or changed permit stops the role.
"""
import argparse
import ctypes
import hashlib
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def parent_death_guard(parent):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0 or os.getppid() != parent:
        os._exit(78)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expires-at', required=True, choices=['UNTIL_REVOKED'])
    parser.add_argument('--binary-sha256', required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--child-pid-file', type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or not Path(command[0]).is_absolute() or Path(command[0]).is_symlink():
        parser.error('absolute non-symlink executable required')
    program = Path(__file__).with_name('permanent-m0.py')
    if program.is_symlink() or not program.is_file():
        parser.error('missing signed operator')
    spec = importlib.util.spec_from_file_location('permanent_operator', program)
    operator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(operator)
    root = Path(os.environ['RLD_M0_DIR']).resolve()
    allowed = operator.authorization_watch(root, os.environ['RLD_M0_EXPECTED_MANIFEST_SHA256'])
    installed = operator.read(root / 'artifacts/install-manifest.json')
    binary = Path(command[0])
    matches = [item for item in installed['artifacts'] if item['name'] == binary.name]
    if (len(matches) != 1 or binary != root / 'artifacts/bin' / binary.name
            or matches[0]['sha256'] != args.binary_sha256):
        parser.error('binary is outside the signed installed artifacts')
    with binary.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != args.binary_sha256:
            parser.error('executable hash mismatch')
    if not allowed():
        return 78
    if args.check_only:
        return 0
    stopped = False
    def stop(*_):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    parent = os.getpid()
    child = subprocess.Popen(command, start_new_session=True,
        preexec_fn=(lambda: parent_death_guard(parent)) if sys.platform == 'linux' else None)
    revoked = False
    try:
        if args.child_pid_file:
            with args.child_pid_file.open('x') as receipt:
                receipt.write(str(child.pid) + '\n'); receipt.flush(); os.fsync(receipt.fileno())
        next_check = 0
        while child.poll() is None and not stopped:
            if time.monotonic() >= next_check:
                if not allowed():
                    revoked = True
                    break
                next_check = time.monotonic() + 1
            time.sleep(0.1)
    finally:
        if child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGKILL if revoked else signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()
    return 78 if revoked else (child.returncode or 0)


if __name__ == '__main__':
    raise SystemExit(main())
