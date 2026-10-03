#!/usr/bin/env python3
"""Signed, durable contact-spool discovery and multi-hop evidence prototype.

This is a supplemental ground reference, not BPv7, a physical radio, ledger
consensus, payment acceptance or an authenticated claim to govern a region.
Contact adapters move complete *.json files between configured spool directories.
"""
import argparse
import base64
from collections import OrderedDict
import copy
import fcntl
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import signal
import threading
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
import interstellar_transfer as evidence

VERSION = 'RLD-CONTACT-MESH-V2'
MAX_NODES = 64
MAX_CONTACTS = 16
MAX_MESSAGES = 256
MAX_STATE = 64 * 1024 * 1024
MAX_BATCH = 20 * 1024 * 1024
MAX_SPOOL_FILES = 256
MAX_SPOOL_BYTES = 64 * 1024 * 1024
MAX_PACKET_BATCH = 4
MAX_HOPS = 16
HEX = re.compile(r'[0-9a-f]{64}\Z')
STATE_KEYS = {'format', 'network', 'node_id', 'adverts', 'messages', 'receipts', 'peer_inventory', 'cursor'}
MAX_VERIFIED_TRANSITS = 512
_verified_transits = OrderedDict()
_verified_transits_lock = threading.Lock()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(evidence.canonical(value)).hexdigest()


def hex32(value):
    require(isinstance(value, str) and HEX.fullmatch(value), 'invalid 32-byte identifier')
    return value


def node_id(public):
    hex32(public)
    return hashlib.sha256((VERSION + '\0node\0').encode() + bytes.fromhex(public)).hexdigest()


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, 'integer outside bound')


def safe_dir(path):
    path = Path(path)
    require(path.is_absolute(), 'directory must be absolute')
    require(not any(p.is_symlink() for p in [path, *path.parents]), 'symlink directory refused')
    evidence.ensure_dir(path)
    return path


def load(path, limit):
    raw = evidence.read_file(Path(path), limit)
    value = evidence.decode_json(raw)
    require(raw == evidence.canonical(value), 'noncanonical JSON')
    return value


def spool_files(root):
    files, total = [], 0
    for path in root.iterdir():
        require(len(files) < MAX_SPOOL_FILES, 'contact file capacity reached; preserve spool')
        require(re.fullmatch(r'[0-9a-f]{64}\.json', path.name) and path.is_file() and not path.is_symlink(), 'unsafe contact spool file')
        total += path.stat().st_size
        require(total <= MAX_SPOOL_BYTES, 'contact byte capacity reached; preserve spool')
        files.append(path)
    return sorted(files), total


def atomic(path, value):
    raw = evidence.canonical(value)
    require(len(raw) <= MAX_STATE, 'durable state capacity reached; retain previous state')
    temporary = path.parent / ('.write-' + os.urandom(16).hex())
    try:
        evidence.write_new(temporary, raw)
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)


def sync_retained(path):
    """Reaffirm unchanged custody without rewriting the complete archive."""
    descriptor=os.open(path,os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    descriptor=os.open(path.parent,os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def sign(key, kind, body):
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    return {'body': body, 'public_key': public,
            'signature': key.sign((VERSION + '\0' + kind + '\0').encode() + evidence.canonical(body)).hex()}


def verify(value, kind, network):
    require(isinstance(value, dict) and set(value) == {'body', 'public_key', 'signature'}, 'invalid signed object')
    body = value['body']
    require(isinstance(body, dict) and body.get('network') == network and body.get('format') == VERSION, 'wrong network or version')
    public = hex32(value['public_key'])
    require(isinstance(value['signature'], str) and re.fullmatch(r'[0-9a-f]{128}', value['signature']), 'invalid signature encoding')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public)).verify(
            bytes.fromhex(value['signature']), (VERSION + '\0' + kind + '\0').encode() + evidence.canonical(body))
    except InvalidSignature as error:
        raise ValueError('invalid signature') from error
    require(body.get('node_id') == node_id(public), 'node identity mismatch')
    return body


def advert_check(value, network):
    body = verify(value, 'advert', network)
    require(set(body) == {'format', 'network', 'node_id', 'region', 'label', 'sequence', 'neighbors'}, 'invalid advertisement fields')
    hex32(body['region'])
    require(isinstance(body['label'], str) and 1 <= len(body['label']) <= 80 and body['label'].isascii()
            and all(ord(c) >= 32 for c in body['label']), 'invalid display label')
    integer(body['sequence'], 1, 2**63 - 1)
    neighbors = body['neighbors']
    require(isinstance(neighbors, list) and len(neighbors) <= MAX_CONTACTS
            and all(isinstance(peer, str) for peer in neighbors), 'invalid neighbor list')
    require(neighbors == sorted(set(neighbors)), 'invalid neighbor order or duplicate')
    for peer in neighbors:
        hex32(peer)
        require(peer != body['node_id'], 'self contact')
    return body


def packet_check(value, network):
    body = verify(value, 'packet', network)
    require(set(body) == {'format', 'network', 'node_id', 'destination', 'nonce', 'hop_limit', 'frame'}, 'invalid packet fields')
    hex32(body['destination'])
    hex32(body['nonce'])
    integer(body['hop_limit'], 1, MAX_HOPS)
    require(isinstance(body['frame'], str) and len(body['frame']) <= evidence.MAX_FRAME * 2, 'frame outside bound')
    try:
        raw = base64.b64decode(body['frame'], validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('invalid frame encoding') from error
    require(base64.b64encode(raw).decode() == body['frame'], 'noncanonical frame encoding')
    frame, payload = evidence.inspect_frame(raw)
    if frame['kind'] == 'regional-bft':
        require(evidence.decode_json(payload)['currency'] == network,
            'consensus carriage differs from mesh currency')
    return body, raw


def transit_check(transit, network, recipient=None, sender=None):
    """Reuse only a bounded witness for exact previously authenticated bytes.

    No frame, key, mutable result or unchecked state is cached. Ownership and
    archive limits are still checked by the caller; Native Rust verifies value.
    """
    require(isinstance(transit,dict) and set(transit)=={'packet','routing','hops'}
            and isinstance(transit['packet'],dict) and isinstance(transit['routing'],dict)
            and isinstance(transit['hops'],list),'invalid transit fields')
    namespace=(VERSION,hex32(network),recipient,sender,MAX_HOPS,evidence.FORMAT,evidence.DOMAIN,
               evidence.MAX_FRAME,evidence.MAX_PAYLOAD,tuple(sorted(evidence.KINDS | evidence.CONTROL_KINDS)))
    key=(namespace,digest(transit))
    with _verified_transits_lock:
        while len(_verified_transits)>MAX_VERIFIED_TRANSITS:
            _verified_transits.popitem(last=False)
        visited=_verified_transits.get(key)
        if visited is not None:_verified_transits.move_to_end(key)
    if visited is not None:
        packet=transit['packet']['body']
        return packet,base64.b64decode(packet['frame'],validate=True),list(visited)
    packet,raw,visited=_transit_check(transit,network,recipient,sender)
    with _verified_transits_lock:
        if MAX_VERIFIED_TRANSITS>0:
            _verified_transits[key]=tuple(visited)
            _verified_transits.move_to_end(key)
            while len(_verified_transits)>MAX_VERIFIED_TRANSITS:
                _verified_transits.popitem(last=False)
    return packet,raw,visited


def _transit_check(transit, network, recipient=None, sender=None):
    require(isinstance(transit, dict) and set(transit) == {'packet', 'routing', 'hops'}, 'invalid transit fields')
    packet, raw = packet_check(transit['packet'], network)
    routing = receipt_route_check(transit['routing'], network)
    frame, _ = evidence.inspect_frame(raw)
    require(routing['node_id'] == packet['node_id'] and routing['packet_id'] == digest(transit['packet'])
            and routing['destination'] == packet['destination'] and routing['frame_id'] == frame['message_id'],
            'receipt routing certificate differs from signed packet')
    hops = transit['hops']
    require(isinstance(hops, list) and len(hops) <= packet['hop_limit'], 'hop limit exceeded')
    previous, current = digest(transit['packet']), packet['node_id']
    visited = [current]
    for hop in hops:
        body = verify(hop, 'hop', network)
        require(set(body) == {'format', 'network', 'node_id', 'packet_id', 'previous', 'to'}, 'invalid hop fields')
        hex32(body['to'])
        require(body['node_id'] == current and body['previous'] == previous
                and body['packet_id'] == digest(transit['packet']), 'broken signed hop chain')
        require(body['to'] not in visited, 'routing loop')
        current, previous = body['to'], digest(hop)
        visited.append(current)
    if recipient is not None:
        require(bool(hops) and current == recipient and hops[-1]['body']['node_id'] == sender,
                'hop does not authorize this contact')
    return packet, raw, visited


def receipt_route_check(route, network):
    body = verify(route, 'receipt-route', network)
    require(set(body) == {'format', 'network', 'node_id', 'packet_id', 'destination', 'frame_id'},
            'invalid source-signed receipt routing certificate')
    for field in ('packet_id', 'destination', 'frame_id'):hex32(body[field])
    return body


def inventory_check(inventory, network):
    body = verify(inventory, 'inventory', network)
    require(set(body) == {'format', 'network', 'node_id', 'packet_ids'} and isinstance(body['packet_ids'],list)
            and len(body['packet_ids']) <= MAX_MESSAGES, 'invalid peer inventory capacity/schema')
    for ident in body['packet_ids']:hex32(ident)
    require(body['packet_ids'] == sorted(set(body['packet_ids'])), 'peer inventory duplicate/order invalid')
    return body


def receipt_check(receipt, network):
    body = verify(receipt, 'receipt', network)
    require(set(body) == {'format', 'network', 'node_id', 'packet_id', 'frame_id', 'routing', 'outcome'}, 'invalid receipt fields')
    hex32(body['packet_id'])
    hex32(body['frame_id'])
    require(body['outcome'] == 'EVIDENCE_STORED_NOT_LEDGER_ACCEPTED', 'wrong receipt outcome')
    routing = receipt_route_check(body['routing'], network)
    require(body['node_id'] == routing['destination'] and body['packet_id'] == routing['packet_id']
            and body['frame_id'] == routing['frame_id'], 'wrong destination receipt')
    return body['packet_id']


def receipt_matches(receipt, transit):
    packet = transit['packet']['body']
    frame, _ = evidence.inspect_frame(base64.b64decode(packet['frame'], validate=True))
    require(receipt['body']['node_id'] == packet['destination']
            and receipt['body']['frame_id'] == frame['message_id']
            and receipt['body']['routing']['body'] == transit['routing']['body'], 'wrong destination receipt')


def initialize(root, network, region, label):
    root = safe_dir(root)
    hex32(network)
    hex32(region)
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    identity = {'format': VERSION, 'network': network, 'region': region, 'label': label,
                'public_key': public, 'private_key': key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex()}
    # Validate public fields before creating the sole private identity file.
    advert_check(sign(key, 'advert', {'format': VERSION, 'network': network, 'region': region,
                 'label': label, 'node_id': node_id(public), 'sequence': 1, 'neighbors': []}), network)
    evidence.write_new(root / 'identity.private.json', evidence.canonical(identity))
    return {'node_id': node_id(public), 'public_key': public, 'network': network, 'region': region}


def tcp_endpoint(host, port, listening=False):
    require(isinstance(host, str) and len(host) <= 15, 'TCP host must be a literal IPv4 address')
    address = ipaddress.IPv4Address(host)
    integer(port, 0 if listening else 1, 65535)
    require(not address.is_multicast and host != '255.255.255.255'
            and (listening or not address.is_unspecified), 'invalid TCP endpoint')
    return str(address), port


class Node:
    def __init__(self, config, nonblocking=False):
        require(isinstance(config, dict) and set(config) == {'format', 'state', 'network', 'contacts'}, 'invalid config fields')
        require(config['format'] == VERSION, 'unsupported config')
        self.root = safe_dir(config['state'])
        self.network = hex32(config['network'])
        self.lock = os.open(self.root / '.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
            identity = load(self.root / 'identity.private.json', 8192)
            require(set(identity) == {'format', 'network', 'region', 'label', 'public_key', 'private_key'}
                    and identity['format'] == VERSION and identity['network'] == self.network, 'identity network mismatch')
            require((self.root / 'identity.private.json').stat().st_mode & 0o077 == 0, 'private identity permissions too broad')
            self.key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(hex32(identity['private_key'])))
            public = self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
            require(public == identity['public_key'], 'private identity mismatch')
            self.id = node_id(public)
            contacts = config['contacts']
            require(isinstance(contacts, list) and len(contacts) <= MAX_CONTACTS, 'contact capacity reached')
            self.contacts = {}
            for contact in contacts:
                require(isinstance(contact, dict) and set(contact) in
                        ({'peer', 'inbox', 'outbox'}, {'peer', 'host', 'port'},
                         {'peer', 'host', 'port', 'tls_cert_sha256'}), 'invalid contact')
                peer = hex32(contact['peer'])
                require(peer != self.id and peer not in self.contacts, 'duplicate or self contact')
                if 'host' in contact:
                    host, port = tcp_endpoint(contact['host'], contact['port'])
                    self.contacts[peer] = {'host': host, 'port': port}
                    if 'tls_cert_sha256' in contact:
                        self.contacts[peer]['tls_cert_sha256'] = hex32(contact['tls_cert_sha256'])
                else:
                    self.contacts[peer] = {k: safe_dir(contact[k]) for k in ('inbox', 'outbox')}
                    require(self.contacts[peer]['inbox'] != self.contacts[peer]['outbox'], 'contact directions must differ')
            dirs = [p for contact in self.contacts.values() if 'inbox' in contact for p in contact.values()]
            require(len(set(dirs)) == len(dirs), 'contact spools must be distinct')
            self.path = self.root / 'mesh-state.json'
            require(not self.path.is_symlink(), 'symlink state refused')
            existed=self.path.exists()
            if existed:
                self.state = load(self.path, MAX_STATE)
                self.validate_state()
            else:
                self.state = {'format': VERSION, 'network': self.network, 'node_id': self.id,
                              'adverts': {}, 'messages': {}, 'receipts': {}, 'peer_inventory': {}, 'cursor': 0}
            # Inventories are only bounded delivery-demand caches. Removing a
            # configured contact may forget its cache, never messages/receipts.
            inventory_changed=any(i not in self.contacts for i in self.state['peer_inventory'])
            self.state['peer_inventory'] = {i:v for i,v in self.state['peer_inventory'].items() if i in self.contacts}
            old = self.state['adverts'].get(self.id)
            body = {'format': VERSION, 'network': self.network, 'node_id': self.id,
                    'region': identity['region'], 'label': identity['label'], 'sequence': 1,
                    'neighbors': sorted(self.contacts)}
            if old:
                body['sequence'] = old['body']['sequence']
                if body != old['body']:
                    body['sequence'] += 1
            self.state['adverts'][self.id] = sign(self.key, 'advert', body)
            advert_check(self.state['adverts'][self.id], self.network)
            # Opening a verified archive is a read operation unless configured
            # inventory/advertisement actually changes. Rewriting megabytes on
            # every lock acquisition can prevent bounded contacts completing.
            if not existed or inventory_changed or old!=self.state['adverts'][self.id]:
                self.save()
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.lock is not None:
            os.close(self.lock)
            self.lock = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def validate_state(self):
        s = self.state
        require(isinstance(s, dict) and set(s) == STATE_KEYS and s['format'] == VERSION
                and s['network'] == self.network and s['node_id'] == self.id, 'corrupt state identity')
        integer(s['cursor'], 0, 2**63 - 1)
        for name, bound in [('adverts', MAX_NODES), ('messages', MAX_MESSAGES), ('receipts', MAX_MESSAGES)]:
            require(isinstance(s[name], dict) and len(s[name]) <= bound, 'state capacity or schema invalid')
        for ident, advert in s['adverts'].items():
            require(advert_check(advert, self.network)['node_id'] == ident, 'corrupt advert key')
        for ident, transit in s['messages'].items():
            packet, _, visited = transit_check(transit, self.network)
            require(digest(transit['packet']) == ident and visited[-1] == self.id, 'corrupt message ownership')
        for ident, receipt in s['receipts'].items():
            require(receipt_check(receipt, self.network) == ident, 'corrupt receipt key')
            if ident in s['messages']:
                receipt_matches(receipt, s['messages'][ident])
        require(isinstance(s['peer_inventory'],dict) and len(s['peer_inventory'])<=MAX_CONTACTS,
                'peer inventory cache capacity/schema invalid')
        for peer, inventory in s['peer_inventory'].items():
            require(inventory_check(inventory,self.network)['node_id']==peer,'peer inventory identity changed')

    def save(self):
        atomic(self.path, self.state)

    def route(self, destination, excluded=(), first_hop=None):
        if destination == self.id:
            return [self.id]
        frontier, seen = [[self.id]], set(excluded) | {self.id}
        while frontier:
            path = frontier.pop(0)
            advert = self.state['adverts'].get(path[-1])
            if not advert:
                continue
            for peer in advert['body']['neighbors']:
                if peer in seen or (len(path) == 1 and
                        (peer not in self.contacts or (first_hop is not None and peer != first_hop))):
                    continue
                if peer == destination:
                    return path + [peer]
                seen.add(peer)
                frontier.append(path + [peer])
        return None

    def enqueue(self, frame, destination, hop_limit=MAX_HOPS):
        hex32(destination)
        evidence.inspect_frame(frame)
        integer(hop_limit, 1, MAX_HOPS)
        require(len(self.state['messages']) < MAX_MESSAGES, 'message capacity reached; retain existing evidence')
        packet = sign(self.key, 'packet', {'format': VERSION, 'network': self.network, 'node_id': self.id,
                      'destination': destination, 'nonce': os.urandom(32).hex(), 'hop_limit': hop_limit,
                      'frame': base64.b64encode(frame).decode()})
        ident = digest(packet)
        header, _ = evidence.inspect_frame(frame)
        routing = sign(self.key,'receipt-route',{'format':VERSION,'network':self.network,'node_id':self.id,
            'packet_id':ident,'destination':destination,'frame_id':header['message_id']})
        self.state['messages'][ident] = {'packet': packet, 'routing': routing, 'hops': []}
        self.deliver_local(self.state)
        self.save()
        return ident

    def deliver_local(self, state):
        for ident, transit in state['messages'].items():
            if ident in state['receipts']:
                receipt_matches(state['receipts'][ident], transit)
            if transit['packet']['body']['destination'] == self.id and ident not in state['receipts']:
                require(len(state['receipts']) < MAX_MESSAGES, 'receipt capacity reached')
                _, raw = packet_check(transit['packet'], self.network)
                frame, _ = evidence.inspect_frame(raw)
                state['receipts'][ident] = sign(self.key, 'receipt', {'format': VERSION, 'network': self.network,
                    'node_id': self.id, 'packet_id': ident, 'frame_id': frame['message_id'],
                    'routing': transit['routing'],
                    'outcome': 'EVIDENCE_STORED_NOT_LEDGER_ACCEPTED'})

    def receive(self, bundle, peer):
        body = verify(bundle, 'exchange', self.network)
        require(set(body) == {'format', 'network', 'node_id', 'to', 'adverts', 'transits', 'receipts', 'inventory'}
                and body['node_id'] == peer and body['to'] == self.id, 'wrong contact peer')
        require(peer in self.contacts,'unconfigured inventory peer')
        require(inventory_check(body['inventory'],self.network)['node_id']==peer,'exchange inventory differs from sender')
        for name, bound in [('adverts', MAX_NODES), ('transits', MAX_PACKET_BATCH), ('receipts', MAX_MESSAGES)]:
            require(isinstance(body[name], list) and len(body[name]) <= bound, 'exchange item limit')
        updated = copy.deepcopy(self.state)
        updated['peer_inventory'][peer] = body['inventory']
        for advert in body['adverts']:
            a = advert_check(advert, self.network)
            old = updated['adverts'].get(a['node_id'])
            if old and a['sequence'] == old['body']['sequence']:
                require(advert == old, 'conflicting signed advertisement; preserve incoming file')
            elif not old or a['sequence'] > old['body']['sequence']:
                require(a['node_id'] != self.id, 'remote cannot revise local advertisement')
                require(old is not None or len(updated['adverts']) < MAX_NODES, 'discovery capacity reached')
                updated['adverts'][a['node_id']] = advert
        for transit in body['transits']:
            packet, _, _ = transit_check(transit, self.network, self.id, peer)
            ident = digest(transit['packet'])
            old = updated['messages'].get(ident)
            if old:
                require(old['packet'] == transit['packet'], 'packet ID collision')
                # A shorter valid custody path can enable a later alternate route.
                if len(transit['hops']) < len(old['hops']):
                    updated['messages'][ident] = transit
            else:
                require(len(updated['messages']) < MAX_MESSAGES, 'message capacity reached; retain incoming file')
                updated['messages'][ident] = transit
        for receipt in body['receipts']:
            ident = receipt_check(receipt, self.network)
            if ident in updated['messages']:
                receipt_matches(receipt, updated['messages'][ident])
            require(ident in updated['receipts'] or len(updated['receipts']) < MAX_MESSAGES, 'receipt capacity reached')
            updated['receipts'][ident] = receipt
        self.deliver_local(updated)
        # The entire exchange is checked and durably committed before inbox removal.
        if updated!=self.state:
            atomic(self.path, updated)
        else:
            # Even an exact repeated exchange must reaffirm durable custody
            # before its socket acknowledgment or inbox consumption. A sync
            # failure refuses custody; it never deletes or refunds evidence.
            sync_retained(self.path)
        self.state = updated

    def exchange(self, peer, accepted_transits=None):
        pending = sorted(self.state['messages'])
        cursor = self.state['cursor'] % max(1, len(pending))
        pending = pending[cursor:] + pending[:cursor]
        transits = []
        requested=set(self.state['peer_inventory'].get(peer,{}).get('body',{}).get('packet_ids',[]))
        receipts=[]
        for ident in sorted(self.state['receipts']):
            receipt=self.state['receipts'][ident]
            source=receipt['body']['routing']['body']['node_id']
            route=self.route(source,first_hop=peer) if source!=self.id else None
            if ident in requested or route and 1<len(route)<=MAX_HOPS+1:
                receipts.append(receipt)
        body = {'format': VERSION, 'network': self.network, 'node_id': self.id,
                'to': peer, 'adverts': [self.state['adverts'][i] for i in sorted(self.state['adverts'])],
                'transits': transits, 'receipts': receipts,
                'inventory':sign(self.key,'inventory',{'format':VERSION,'network':self.network,
                    'node_id':self.id,'packet_ids':sorted(self.state['messages'])})}
        for ident in pending:
            if ident in self.state['receipts']:
                continue
            transit = self.state['messages'][ident]
            packet, _, visited = transit_check(transit, self.network)
            # Bounded redundancy over each eligible adjacent contact avoids
            # pinning all delivery to one advertised shortest route. Each copy
            # retains the same signed packet ID and visited-hop loop checks.
            route = self.route(packet['destination'], visited[:-1], first_hop=peer)
            if not route or len(route) < 2 or route[1] != peer or len(transit['hops']) + len(route) - 1 > packet['hop_limit']:
                continue
            hop = sign(self.key, 'hop', {'format': VERSION, 'network': self.network, 'node_id': self.id,
                       'packet_id': ident, 'previous': digest(transit['hops'][-1]) if transit['hops'] else ident, 'to': peer})
            candidate = {'packet': transit['packet'], 'routing': transit['routing'], 'hops': transit['hops'] + [hop]}
            if accepted_transits is not None and digest(candidate) in accepted_transits:
                continue
            # Count the second base64 layer and signature/advertisement overhead.
            if len(evidence.canonical({**body, 'transits': transits + [candidate]})) + 512 > MAX_BATCH:
                break
            transits.append(candidate)
            if len(transits) == MAX_PACKET_BATCH:
                break
        return sign(self.key, 'exchange', body)

    def tick(self):
        errors = []
        for peer, contact in sorted(self.contacts.items()):
            if 'host' in contact:
                continue  # Socket I/O runs outside the mesh lock via the contact service.
            try:
                incoming, _ = spool_files(contact['inbox'])
            except (OSError, ValueError) as error:
                errors.append(str(error))
                incoming = []
            for path in incoming:
                try:
                    require(re.fullmatch(r'[0-9a-f]{64}\.json', path.name), 'unexpected inbox file')
                    bundle = load(path, MAX_BATCH)
                    require(path.stem == digest(bundle), 'exchange filename mismatch')
                    self.receive(bundle, peer)
                    path.unlink()
                    fd = os.open(path.parent, os.O_RDONLY)
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)
                except (OSError, ValueError) as error:
                    errors.append(str(error))
            try:
                bundle = self.exchange(peer)
                data = evidence.canonical(bundle)
                require(len(data) <= MAX_BATCH, 'exchange bytes exceed bound')
                target = contact['outbox'] / (digest(bundle) + '.json')
                files, total = spool_files(contact['outbox'])
                if not target.exists():
                    require(len(files) < MAX_SPOOL_FILES and total + len(data) <= MAX_SPOOL_BYTES,
                            'contact capacity reached; retain queued evidence')
                    evidence.write_new(target, data)
                else:
                    require(evidence.read_file(target, MAX_BATCH) == data, 'exchange file collision')
            except (OSError, ValueError) as error:
                errors.append(str(error))
        self.state['cursor'] = (self.state['cursor'] + 1) % (2**63 - 1)
        self.save()
        report = self.status()
        report['errors'] = errors[:16]
        atomic(self.root / 'status.json', report)
        return report

    def status(self):
        return {'format': VERSION, 'network': self.network, 'node_id': self.id,
                'research_only': True, 'physical_route_verified': False, 'payment_authorized': False,
                'observed_at_unix': int(time.time()), 'nodes': len(self.state['adverts']),
                'regions': sorted({a['body']['region'] for a in self.state['adverts'].values()}),
                'routes_are_advertised_candidates': True,
                'routes': {i: self.route(i) for i in sorted(self.state['adverts']) if i != self.id},
                'messages': {i: ('EVIDENCE_STORED_NOT_LEDGER_ACCEPTED' if i in self.state['receipts'] else
                    'QUEUED_WAITING_CONTACT_OR_ROUTE') for i in sorted(self.state['messages'])}}

    def export_received(self, ident, output):
        hex32(ident)
        transit = self.state['messages'][ident]
        packet, raw, _ = transit_check(transit, self.network)
        require(packet['destination'] == self.id and ident in self.state['receipts'], 'not a locally received frame')
        evidence.write_new(Path(output), raw)
        return evidence.inspect_frame(raw)[0]['message_id']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init')
    init.add_argument('--state', type=Path, required=True)
    init.add_argument('--network', required=True)
    init.add_argument('--region', required=True)
    init.add_argument('--label', required=True)
    for name in ['run', 'tick', 'status', 'enqueue', 'export-received']:
        command = sub.add_parser(name)
        command.add_argument('--config', type=Path, required=True)
        if name == 'run':
            command.add_argument('--interval', type=float, default=1)
        if name == 'enqueue':
            command.add_argument('--destination-node', required=True)
            command.add_argument('--frame', type=Path, required=True)
            command.add_argument('--hop-limit', type=int, default=MAX_HOPS)
        if name == 'export-received':
            command.add_argument('--packet-id', required=True)
            command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'init':
        print(json.dumps(initialize(args.state.absolute(), args.network, args.region, args.label)))
        return
    config = load(args.config, 64 * 1024)
    if args.action == 'run':
        require(0.1 <= args.interval <= 3600, 'poll interval outside bound')
        running = True
        def stop(*_):
            nonlocal running
            running = False
        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)
        previous = None
        while running:
            with Node(config) as node:
                report = node.tick()
            comparable = {k: v for k, v in report.items() if k != 'observed_at_unix'}
            if comparable != previous:
                print(json.dumps(report), flush=True)
                previous = comparable
            deadline = time.monotonic() + args.interval
            while running and time.monotonic() < deadline:
                time.sleep(min(0.1, args.interval))
        return
    with Node(config) as node:
        if args.action == 'enqueue':
            result = {'packet_id': node.enqueue(evidence.read_file(args.frame, evidence.MAX_FRAME), args.destination_node, args.hop_limit)}
        elif args.action == 'export-received':
            result = {'frame_id': node.export_received(args.packet_id, args.output), 'ledger_accepted': False}
        elif args.action == 'tick':
            result = node.tick()
        else:
            result = node.status()
        print(json.dumps(result))


if __name__ == '__main__':
    main()
