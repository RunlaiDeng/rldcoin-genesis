#!/usr/bin/env python3
"""Contact companion launched by the native fixture node; Rust owns value checks.

Directory contacts are a bounded ground adapter. Discovered self-signed regions
are routing candidates only, never ledger, signer or monetary authority.
"""
import argparse
import base64
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

import interstellar_mesh as mesh
import interstellar_tcp as tcp
import interstellar_transfer as wire

FORMAT = 'RLD-REGIONAL-CONTACT-NODE-V1'
MAX_PER_TICK = 4
MAX_NATIVE_OUTPUT = 8 * 1024 * 1024


class Native:
    def __init__(self, binary, ledger, authority, currency):
        self.binary = Path(binary)
        mesh.require(self.binary.is_absolute() and self.binary.is_file() and not self.binary.is_symlink(), 'native binary must be an absolute regular file')
        self.ledger = Path(ledger)
        self.authority = mesh.hex32(authority)
        self.currency = mesh.hex32(currency)
        mesh.require(self.ledger.is_absolute(), 'ledger directory must be absolute')

    def call(self, *args):
        # Native outputs are bounded by the candidate's journal/frame limits.
        # File-backed capture also bounds memory if a broken executable floods.
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            result = subprocess.run([str(self.binary), '--dir', str(self.ledger),
                '--authority', self.authority, '--currency', self.currency, *map(str, args)],
                stdout=output, stderr=errors, timeout=30, check=False)
            mesh.require(output.tell() <= MAX_NATIVE_OUTPUT and errors.tell() <= 64 * 1024, 'native response outside bound')
            errors.seek(0)
            mesh.require(result.returncode == 0, 'native rejected: ' + errors.read(2048).decode('utf-8', errors='replace').strip())
            output.seek(0)
            return wire.decode_json(output.read(MAX_NATIVE_OUTPUT + 1))

    def apply(self, raw, miner):
        # The mesh retains the complete frame throughout. A temporary native
        # input is disposable; native proof/pending records persist separately.
        with tempfile.NamedTemporaryFile(prefix='rld-regional-contact-', suffix='.json') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
            args = ['contact-apply', '--file', handle.name]
            if miner is not None:
                args.extend(['--miner', miner])
            return self.call(*args)


def startup_config(native, path=None):
    """Restore one persistent relay identity, after native authority validation.

    An empty contact set means waiting for a real contact, never an invented
    reachable peer. Default initialization is serialized across startup races.
    """
    observation = native.call('contact-status')
    mesh.require(observation['currency'] == native.currency, 'startup currency mismatch')
    if path is not None:
        return mesh.load(path, 64 * 1024)
    root = mesh.safe_dir(native.ledger / 'transport')
    descriptor = os.open(root / '.startup.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        path = root / 'config.json'
        if path.exists() or path.is_symlink():
            return mesh.load(path, 64 * 1024)
        identity = root / 'identity.private.json'
        if not identity.exists() and not identity.is_symlink():
            mesh.initialize(root, native.currency, observation['region'], 'regional-node')
        config = {'format': mesh.VERSION, 'state': str(root),
            'network': native.currency, 'contacts': []}
        # Validate recovered identity before exposing configuration, including
        # the crash window after identity creation but before config commit.
        with mesh.Node(config) as node:
            mesh.require(node.state['adverts'][node.id]['body']['region'] == observation['region'],
                'default relay identity differs from native ledger')
        mesh.atomic(path, config)
        return config
    finally:
        os.close(descriptor)


class Service:
    def __init__(self, native, config, miner, listen=('127.0.0.1',0)):
        self.native, self.config, self.miner = native, config, miner
        self.lock = None
        self.tcp = None
        self.root = mesh.safe_dir(config['state'])
        try:
            self.lock = os.open(self.root / '.regional-contact-service.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            observation = native.call('contact-status')
            self.region = observation['region']
            mesh.require(observation['currency'] == native.currency and config['network'] == native.currency,
                'native/transport currency network binding mismatch')
            self.path = self.root / 'regional-contact-progress.json'
            if self.path.exists():
                self.progress = mesh.load(self.path, 8192)
                mesh.require(set(self.progress) == {'format', 'currency', 'region', 'cursor'}
                    and self.progress['format'] == FORMAT and self.progress['currency'] == native.currency
                    and self.progress['region'] == self.region, 'contact progress identity mismatch')
                mesh.integer(self.progress['cursor'], 0, 2**63-1)
            else:
                self.progress = {'format': FORMAT, 'currency': native.currency, 'region': self.region, 'cursor': 0}
            with mesh.Node(config) as node:
                mesh.require(node.state['adverts'][node.id]['body']['region'] == self.region,
                    'local mesh label differs from native ledger identity')
            mesh.atomic(self.path, self.progress)
            self.tcp = tcp.Server(config,listen)
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.tcp is not None:
            self.tcp.close()
            self.tcp = None
        if self.lock is not None:
            os.close(self.lock)
            self.lock = None

    def tick(self):
        # Release the mesh lock before native replay/mining. Enqueue and receipt
        # tools can safely operate between bounded contact iterations.
        socket_observation = self.tcp.tick()
        received, routes, adverts = [], {}, {}
        with mesh.Node(self.config) as node:
            transport = node.tick()
            transport['tcp'] = socket_observation
            eligible = sorted(i for i, t in node.state['messages'].items()
                if t['packet']['body']['destination'] == node.id and i in node.state['receipts'])
            if eligible:
                offset = self.progress['cursor'] % len(eligible)
                rotated = eligible[offset:] + eligible[:offset]
                for ident in rotated[:MAX_PER_TICK]:
                    packet, raw, _ = mesh.transit_check(node.state['messages'][ident], node.network)
                    mesh.receipt_matches(node.state['receipts'][ident], node.state['messages'][ident])
                    received.append((ident, raw))
            adverts = {i: a['body']['region'] for i, a in node.state['adverts'].items()}
            routes = {i: node.route(i) for i in adverts if i != node.id}
        errors = list(socket_observation['errors'])
        native_observation = None
        applied = []
        rejected = []
        try:
            native_observation = self.native.call('contact-status')
            mesh.require(native_observation['currency'] == self.native.currency and native_observation['region'] == self.region,
                'fresh native identity differs from startup binding')
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors.append(str(error))
        if native_observation is not None:
            accepted = {c['message_id'] for c in native_observation['contacts']
                if c['import_accepted'] or (self.miner is None and c['evidence_verified'])}
            for packet_id, raw in received:
                try:
                    frame, _ = wire.inspect_frame(raw)
                    if frame['message_id'] not in accepted:
                        result = self.native.apply(raw, self.miner)
                        applied.append({'packet_id': packet_id, 'native': result})
                except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                    errors.append(str(error))
                    rejected.append({'packet_id': packet_id, 'reason': str(error)})
            # Export authority is obtained from the actual native ledger. A
            # region advertised by a mesh key selects only a candidate carrier.
            try:
                outgoing = self.native.call('contact-outgoing')
                offers = outgoing['offers']
                if offers:
                    offset = self.progress['cursor'] % len(offers)
                    offers = (offers[offset:] + offers[:offset])[:MAX_PER_TICK]
                for offer in offers:
                    candidates = sorted(i for i, region in adverts.items() if region == offer['destination'] and routes.get(i))
                    if not candidates:
                        continue
                    value = self.native.call('contact-export', '--export', offer['export'])
                    raw = wire.canonical(value)
                    frame, _ = wire.inspect_frame(raw)
                    mesh.require(frame['source_chain_id'] == self.region and frame['destination_chain_id'] == offer['destination'], 'outgoing native route changed')
                    with mesh.Node(self.config) as node:
                        # Inspect retained packets to reconcile enqueue-after-
                        # crash, without a fragile external "already sent" flag.
                        retained = set()
                        for transit in node.state['messages'].values():
                            packet, prior, _ = mesh.transit_check(transit, node.network)
                            prior_frame, _ = wire.inspect_frame(prior)
                            if packet['node_id'] == node.id:
                                retained.add((prior_frame['message_id'], packet['destination']))
                        # Rotate among reachable candidates; a dishonest label
                        # can delay delivery but cannot change the ledger target.
                        destination = candidates[self.progress['cursor'] % len(candidates)]
                        if (frame['message_id'], destination) not in retained:
                            node.enqueue(raw, destination)
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                errors.append(str(error))
            try:
                native_observation = self.native.call('contact-status')
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                native_observation = None
                errors.append(str(error))
        self.progress['cursor'] = (self.progress['cursor'] + 1) % (2**63)
        mesh.atomic(self.path, self.progress)
        report = {'format': FORMAT, 'process_id': os.getpid(), 'currency': self.native.currency, 'region': self.region,
            'relay_enabled': True, 'local_import_mining_enabled': self.miner is not None,
            'observed_at_unix': int(time.time()), 'transport': transport,
            'native_observation': native_observation, 'native_observation_available': native_observation is not None,
            'applied': applied, 'rejected': rejected, 'errors': errors[:16], 'fixture_only': True,
            'physical_route_verified': False, 'independent_operators': False,
            'transport_receipt_is_payment_authority': False, 'remote_current_state_known': False}
        mesh.atomic(self.root / 'regional-contact-status.json', report)
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--authority', required=True)
    parser.add_argument('--currency', required=True)
    parser.add_argument('--mesh-config', type=Path)
    parser.add_argument('--listen',default='127.0.0.1:0')
    parser.add_argument('--miner')
    parser.add_argument('--interval', type=float, default=1)
    args = parser.parse_args()
    mesh.require(0.1 <= args.interval <= 3600, 'contact interval outside bound')
    native = Native(args.binary, args.ledger, args.authority, args.currency)
    config = startup_config(native, args.mesh_config)
    parts=args.listen.split(':')
    mesh.require(len(parts)==2 and parts[1].isdigit(), 'TCP listener must be literal IPv4:port')
    listen=mesh.tcp_endpoint(parts[0],int(parts[1]),listening=True)
    service = Service(native, config, args.miner,listen)
    running = True
    def stop(*_):
        nonlocal running
        running = False
        service.tcp.running = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    previous = None
    try:
        while running:
            result = service.tick()
            # Only material changes print; the on-disk observation is refreshed.
            comparable = {k: v for k, v in result.items() if k != 'observed_at_unix'}
            comparable['transport'] = {k: v for k, v in result['transport'].items() if k != 'observed_at_unix'}
            if comparable != previous:
                print(json.dumps(result), flush=True)
                previous = comparable
            deadline = time.monotonic() + args.interval
            while running and time.monotonic() < deadline:
                time.sleep(min(0.1, args.interval))
    finally:
        service.close()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        raise SystemExit('regional contact node rejected: ' + str(error))
