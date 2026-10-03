#!/usr/bin/env python3
"""Signed, bounded IPv4 TCP contact adapter; no ledger or issuance authority.

Configured peer identities/addresses only. Each exchange is committed before
acknowledgment, all socket waits occur outside mesh locks, and failure retains
the original queued evidence. This low-latency duplex ground adapter is not
BPv7, NAT traversal or interstellar-link qualification. TLS 1.3 is the default;
literal endpoints and certificate hashes are independently pinned in config.
"""
import copy
import datetime
import hashlib
import os
import socket
import ssl
import struct
import threading
import time

import interstellar_mesh as mesh
import interstellar_transfer as wire
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

ADAPTER = 'RLD-CONTACT-TCP-V4'
MAX_WIRE = mesh.MAX_BATCH + 4096
MAX_WORKERS = 2
MAX_OUTBOUND_PER_TICK = 4
ATTEMPT_SECONDS = 3.0
CERTIFICATE_DAYS = 90


def certificate_check(cert, network, peer, now=None):
    now=now or datetime.datetime.now(datetime.timezone.utc)
    mesh.require(cert.not_valid_before_utc <= now <= cert.not_valid_after_utc,
        'ground TLS certificate outside validity; preserve evidence')
    mesh.require(cert.subject==cert.issuer
        and cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)==[x509.NameAttribute(x509.NameOID.COMMON_NAME,peer)]
        and cert.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)==[x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME,network)]
        and isinstance(cert.public_key(),Ed25519PublicKey),
        'TLS certificate identity/network or algorithm mismatch')
    try:
        cert.public_key().verify(cert.signature,cert.tbs_certificate_bytes)
    except InvalidSignature as error:
        raise ValueError('TLS certificate self-signature invalid') from error


def tls_material(root, network, peer):
    mesh.hex32(network)
    mesh.hex32(peer)
    root=mesh.safe_dir(root)
    path=root/'tcp-tls.private.pem'
    if not path.exists():
        key=Ed25519PrivateKey.generate()
        now=datetime.datetime.now(datetime.timezone.utc)
        name=x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME,peer),
            x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME,network)])
        cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(minutes=5))
            .not_valid_after(now+datetime.timedelta(days=CERTIFICATE_DAYS))
            .add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True).sign(key,None))
        raw=cert.public_bytes(serialization.Encoding.PEM)+key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
        # One owner-only, fsynced file commits certificate and key together.
        wire.write_new(path,raw)
    raw=wire.read_file(path,8192)
    mesh.require(path.stat().st_mode & 0o077 == 0,'TLS private file permissions too broad')
    cert=x509.load_pem_x509_certificate(raw)
    key=serialization.load_pem_private_key(raw,password=None)
    mesh.require(isinstance(key,Ed25519PrivateKey),'TLS private key algorithm mismatch')
    certificate_check(cert,network,peer)
    mesh.require(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        ==cert.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw),'TLS private key/certificate mismatch')
    canonical=cert.public_bytes(serialization.Encoding.PEM)+key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    mesh.require(raw==canonical,'TLS private material malformed; preserve file')
    return path,hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),cert.not_valid_after_utc.isoformat()


def public_tls_identity(config):
    with mesh.Node(config) as node:
        _,fingerprint,expires=tls_material(node.root,node.network,node.id)
        return {'node_id':node.id,'network':node.network,'tls_cert_sha256':fingerprint,
            'certificate_valid_until_utc':expires}


def client_context():
    mesh.require(ssl.HAS_TLSv1_3,'TLS 1.3 required; no downgrade')
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname=False
    # Authentication uses the independent exact DER pin plus signed mesh ID,
    # not a public CA or a hostname supplied by an advertisement.
    context.verify_mode=ssl.CERT_NONE
    context.minimum_version=context.maximum_version=ssl.TLSVersion.TLSv1_3
    return context


def client_connect(address, fingerprint, network, peer, deadline):
    context=client_context()
    connection=socket.create_connection(address,timeout=max(0.001,deadline-time.monotonic()))
    try:
        connection.settimeout(max(0.001,deadline-time.monotonic()))
        connection=context.wrap_socket(connection,server_hostname=None)
        mesh.require(connection.version()=='TLSv1.3','TLS downgrade refused')
        raw=connection.getpeercert(binary_form=True)
        mesh.require(hashlib.sha256(raw).hexdigest()==mesh.hex32(fingerprint),'TLS certificate pin mismatch; no fallback')
        certificate_check(x509.load_der_x509_certificate(raw),network,peer)
        return connection
    except BaseException:
        connection.close()
        raise


def challenge(key,network,peer,fingerprint):
    return mesh.sign(key,'tcp-challenge',{'format':mesh.VERSION,'adapter':ADAPTER,'network':network,
        'node_id':peer,'nonce':os.urandom(32).hex(),'tls_cert_sha256':fingerprint})


def check_challenge(value, network, peer, fingerprint):
    body=mesh.verify(value,'tcp-challenge',network)
    mesh.require(set(body)=={'format','adapter','network','node_id','nonce','tls_cert_sha256'}
        and body['adapter']==ADAPTER and body['node_id']==peer
        and body['tls_cert_sha256']==fingerprint,'TCP connection challenge binding mismatch')
    return mesh.hex32(body['nonce'])


def read_exact(connection, length, deadline):
    chunks = []
    remaining = length
    while remaining:
        available = deadline-time.monotonic()
        mesh.require(available > 0, 'TCP local attempt deadline reached; retain evidence')
        connection.settimeout(available)
        chunk = connection.recv(min(remaining, 65536))
        mesh.require(bool(chunk), 'incomplete TCP frame; retain evidence')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def receive(connection, deadline):
    length = struct.unpack('!I', read_exact(connection, 4, deadline))[0]
    mesh.require(0 < length <= MAX_WIRE, 'TCP wire byte bound; retain evidence')
    raw = read_exact(connection, length, deadline)
    value = wire.decode_json(raw)
    mesh.require(raw == wire.canonical(value), 'noncanonical TCP frame')
    return value


def send(connection, value, deadline):
    data = wire.canonical(value)
    mesh.require(0 < len(data) <= MAX_WIRE, 'TCP wire byte bound; retain evidence')
    remaining = deadline-time.monotonic()
    mesh.require(remaining > 0, 'TCP local attempt deadline reached; retain evidence')
    connection.settimeout(remaining)
    connection.sendall(struct.pack('!I',len(data))+data)


def outgoing(node, peer, accepted_transits=None):
    bundle = node.exchange(peer,accepted_transits)
    mesh.require(len(wire.canonical(bundle)) <= mesh.MAX_BATCH, 'TCP exchange byte bound')
    # Durable rotation prevents a failed early batch starving later packets.
    node.state['cursor'] = (node.state['cursor'] + 1) % (2**63)
    node.save()
    return bundle


def request(node, peer, connection_nonce, accepted_transits=None):
    bundle = outgoing(node, peer,accepted_transits)
    return mesh.sign(node.key,'tcp-request',{'format':mesh.VERSION,'adapter':ADAPTER,'network':node.network,
        'node_id':node.id,'to':peer,'nonce':os.urandom(32).hex(),
        'challenge':mesh.hex32(connection_nonce),'bundle':bundle})


def check_request(value, network, recipient, peers, connection_nonce):
    body = mesh.verify(value,'tcp-request',network)
    mesh.require(set(body)=={'format','adapter','network','node_id','to','nonce','challenge','bundle'}
        and body['adapter']==ADAPTER and body['to']==recipient and body['node_id'] in peers
        and body['challenge']==connection_nonce,
        'TCP request identity or configured peer mismatch')
    mesh.hex32(body['nonce'])
    mesh.require(len(wire.canonical(body['bundle'])) <= mesh.MAX_BATCH,'TCP exchange byte bound')
    exchange = mesh.verify(body['bundle'],'exchange',network)
    mesh.require(exchange['node_id']==body['node_id'] and exchange['to']==recipient,'TCP request/bundle identity mismatch')
    return body


def check_response(value, network, requester, peer, sent):
    body=mesh.verify(value,'tcp-response',network)
    mesh.require(set(body)=={'format','adapter','network','node_id','to','nonce','challenge','exchange_id','accepted','bundle','error'}
        and body['adapter']==ADAPTER and body['node_id']==peer and body['to']==requester
        and body['nonce']==sent['body']['nonce'] and body['challenge']==sent['body']['challenge']
        and body['exchange_id']==mesh.digest(sent['body']['bundle']),
        'TCP response identity, nonce or exact exchange mismatch')
    mesh.require(type(body['accepted']) is bool, 'invalid TCP acknowledgment')
    if not body['accepted']:
        mesh.require(body['bundle'] is None and body['error']=='CONTACT_REJECTED','invalid TCP refusal')
        raise ValueError('TCP peer refused custody; retain queued evidence')
    mesh.require(body['error'] is None and isinstance(body['bundle'],dict)
        and len(wire.canonical(body['bundle']))<=mesh.MAX_BATCH,'invalid TCP success bundle')
    exchange=mesh.verify(body['bundle'],'exchange',network)
    mesh.require(exchange['node_id']==peer and exchange['to']==requester,'TCP response/bundle identity mismatch')
    return body['bundle']


class Server:
    def __init__(self,config,listen=('127.0.0.1',0),insecure=False):
        self.config=copy.deepcopy(config)
        with mesh.Node(config) as node:
            self.id,self.network,self.key=node.id,node.network,node.key
            self.peers={peer:dict(c) for peer,c in node.contacts.items() if 'host' in c}
            self.insecure=insecure
            mesh.require(type(insecure) is bool,'invalid insecure transport selection')
            mesh.require(all(('tls_cert_sha256' in c) != insecure for c in self.peers.values()),
                'TLS certificate pin required, or explicit insecure mode with unpinned peers; no fallback')
            self.fingerprint=None
            self.expires=None
            self.context=None
            if not insecure:
                mesh.require(ssl.HAS_TLSv1_3,'TLS 1.3 required; no downgrade')
                path,self.fingerprint,self.expires=tls_material(node.root,node.network,node.id)
                self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.context.minimum_version=self.context.maximum_version=ssl.TLSVersion.TLSv1_3
                self.context.load_cert_chain(path)
                self.context.num_tickets=0
        self.running=True
        self.guard=threading.Lock()
        self.connections=set()
        self.workers=set()
        self.observations={}
        # Optimization only: a verified reply proves this exact exchange was
        # durably held by this configured next hop. Keep all original carriage,
        # forget suppression on restart, and periodically re-probe all packets.
        # This never creates a destination receipt, ledger credit or refund.
        self.accepted_transits={}
        self.peer_attempts={}
        self.refused_connections=0
        self.cursor=0
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        try:
            self.socket.bind(mesh.tcp_endpoint(*listen,listening=True))
            self.socket.listen(MAX_WORKERS)
            self.socket.settimeout(0.1)
            self.address=self.socket.getsockname()
            self.thread=threading.Thread(target=self.serve,name='rld-tcp-contact-listener',daemon=True)
            self.thread.start()
        except BaseException:
            self.socket.close()
            raise

    def mark(self,peer,direction,success):
        with self.guard:
            entry=self.observations.setdefault(peer,{})
            entry[direction+'_last_attempt_at_unix']=int(time.time())
            entry[direction+'_last_attempt_succeeded']=success
            if success:
                entry[direction+'_last_success_at_unix']=int(time.time())

    def suppressed(self, peer):
        with self.guard:
            return set(self.accepted_transits.get(peer,set()))

    def serve(self):
        while self.running:
            try:
                connection,_=self.socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with self.guard:
                if len(self.workers)>=MAX_WORKERS:
                    self.refused_connections+=1
                    connection.close()
                    continue
                worker=threading.Thread(target=self.handle,args=(connection,),daemon=True)
                self.connections.add(connection)
                self.workers.add(worker)
                # close() must never observe a registered but unstarted worker.
                worker.start()

    def handle(self,connection):
        tracked=connection
        try:
            deadline=time.monotonic()+ATTEMPT_SECONDS
            if not self.insecure:
                connection.settimeout(ATTEMPT_SECONDS)
                with self.guard:
                    mesh.require(self.running,'TLS runtime is stopping; preserve evidence')
                    connection=self.context.wrap_socket(connection,server_side=True,do_handshake_on_connect=False)
                    self.connections.discard(tracked)
                    self.connections.add(connection)
                tracked=connection
                connection.do_handshake()
                mesh.require(connection.version()=='TLSv1.3','TLS downgrade refused')
            hello=challenge(self.key,self.network,self.id,self.fingerprint)
            send(connection,hello,deadline)
            value=receive(connection,deadline)
            body=check_request(value,self.network,self.id,self.peers,hello['body']['nonce'])
            peer=body['node_id']
            accepted,bundle=False,None
            try:
                with mesh.Node(self.config,nonblocking=True) as node:
                    mesh.require(node.id==self.id,'TCP runtime identity changed')
                    node.receive(body['bundle'],peer)
                    accepted=True  # receive fsyncs its complete verified state first.
                    bundle=outgoing(node,peer,self.suppressed(peer))
                self.mark(peer,'inbound',True)
            except (OSError,ValueError):
                accepted,bundle=False,None
                self.mark(peer,'inbound',False)
            response=mesh.sign(self.key,'tcp-response',{'format':mesh.VERSION,'adapter':ADAPTER,'network':self.network,
                'node_id':self.id,'to':peer,'nonce':body['nonce'],'challenge':body['challenge'],
                'exchange_id':mesh.digest(body['bundle']),
                'accepted':accepted,'bundle':bundle,'error':None if accepted else 'CONTACT_REJECTED'})
            send(connection,response,deadline)
        except (OSError,ValueError,KeyError,TypeError,RecursionError):
            pass  # No unauthenticated/corrupt request receives a custody assertion.
        finally:
            connection.close()
            with self.guard:
                self.connections.discard(tracked)
                self.workers.discard(threading.current_thread())

    def tick(self):
        errors=[]
        peers=sorted(self.peers)
        if peers:
            offset=self.cursor%len(peers)
            chosen=(peers[offset:]+peers[:offset])[:MAX_OUTBOUND_PER_TICK]
            self.cursor=(self.cursor+len(chosen))%len(peers)
            for peer in chosen:
                if not self.running:
                    break
                try:
                    # No mesh lock is held across connect/write/read.
                    deadline=time.monotonic()+ATTEMPT_SECONDS
                    c=self.peers[peer]
                    with self.guard:
                        count=self.peer_attempts.get(peer,0)+1
                        self.peer_attempts[peer]=count
                        if count%64==0:
                            self.accepted_transits.pop(peer,None)
                    connection=(socket.create_connection((c['host'],c['port']),timeout=ATTEMPT_SECONDS) if self.insecure else
                        client_connect((c['host'],c['port']),c['tls_cert_sha256'],self.network,peer,deadline))
                    with connection:
                        nonce=check_challenge(receive(connection,deadline),self.network,peer,c.get('tls_cert_sha256'))
                        with mesh.Node(self.config,nonblocking=True) as node:
                            mesh.require(node.id==self.id,'TCP runtime identity changed')
                            sent=request(node,peer,nonce,self.suppressed(peer))
                        send(connection,sent,deadline)
                        response=receive(connection,deadline)
                    bundle=check_response(response,self.network,self.id,peer,sent)
                    with mesh.Node(self.config,nonblocking=True) as node:
                        mesh.require(node.id==self.id,'TCP runtime identity changed')
                        node.receive(bundle,peer)
                    # Only after exact nonce/challenge/exchange verification and
                    # complete local reply custody. A lost/refused reply retries.
                    with self.guard:
                        retained=self.accepted_transits.setdefault(peer,set())
                        retained.update(mesh.digest(t) for t in sent['body']['bundle']['body']['transits'])
                        if len(retained)>mesh.MAX_MESSAGES:
                            # This cache is only an optimization. Forgetting it
                            # safely resends retained evidence, never drops it.
                            self.accepted_transits.pop(peer,None)
                    self.mark(peer,'outbound',True)
                except (OSError,ValueError,KeyError,TypeError,RecursionError) as error:
                    self.mark(peer,'outbound',False)
                    errors.append(str(error)[:256])
        return {'adapter':ADAPTER,'listener':{'host':self.address[0],'port':self.address[1]},
            'contacts':self.report(),'errors':errors[:mesh.MAX_CONTACTS],
            'limits':{'inbound_workers':MAX_WORKERS,'outbound_contacts_per_tick':MAX_OUTBOUND_PER_TICK,
                'wire_bytes':MAX_WIRE,'local_attempt_seconds':ATTEMPT_SECONDS},
            'encrypted':not self.insecure,'tls_version':None if self.insecure else 'TLSv1.3',
            'tls_cert_sha256':self.fingerprint,'certificate_valid_until_utc':self.expires,
            'fallback_to_plaintext':False,'plaintext_selected_explicitly':self.insecure,
            'ledger_acceptance_from_transport':False,'physical_route_qualified':False}

    def report(self):
        with self.guard:
            return {'observations':copy.deepcopy(self.observations),'refused_connections':self.refused_connections}

    def close(self):
        self.running=False
        self.socket.close()
        if hasattr(self,'thread'):
            self.thread.join(timeout=1)
        with self.guard:
            connections=list(self.connections)
            workers=list(self.workers)
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()
        deadline=time.monotonic()+ATTEMPT_SECONDS+1
        for worker in workers:
            worker.join(timeout=max(0,deadline-time.monotonic()))
