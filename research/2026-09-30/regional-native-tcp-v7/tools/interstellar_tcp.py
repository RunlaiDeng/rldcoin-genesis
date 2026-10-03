#!/usr/bin/env python3
"""Signed, bounded IPv4 TCP contact adapter; no ledger or issuance authority.

Configured peer identities/addresses only. Each exchange is committed before
acknowledgment, all socket waits occur outside mesh locks, and failure retains
the original queued evidence. This low-latency duplex ground adapter is not
BPv7, encrypted transport, NAT traversal or interstellar-link qualification.
"""
import copy
import os
import socket
import struct
import threading
import time

import interstellar_mesh as mesh
import interstellar_transfer as wire

ADAPTER = 'RLD-CONTACT-TCP-V1'
MAX_WIRE = mesh.MAX_BATCH + 4096
MAX_WORKERS = 2
MAX_OUTBOUND_PER_TICK = 4
ATTEMPT_SECONDS = 3.0


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


def outgoing(node, peer):
    bundle = node.exchange(peer)
    mesh.require(len(wire.canonical(bundle)) <= mesh.MAX_BATCH, 'TCP exchange byte bound')
    # Durable rotation prevents a failed early batch starving later packets.
    node.state['cursor'] = (node.state['cursor'] + 1) % (2**63)
    node.save()
    return bundle


def request(node, peer):
    bundle = outgoing(node, peer)
    return mesh.sign(node.key,'tcp-request',{'format':mesh.VERSION,'adapter':ADAPTER,'network':node.network,
        'node_id':node.id,'to':peer,'nonce':os.urandom(32).hex(),'bundle':bundle})


def check_request(value, network, recipient, peers):
    body = mesh.verify(value,'tcp-request',network)
    mesh.require(set(body)=={'format','adapter','network','node_id','to','nonce','bundle'}
        and body['adapter']==ADAPTER and body['to']==recipient and body['node_id'] in peers,
        'TCP request identity or configured peer mismatch')
    mesh.hex32(body['nonce'])
    mesh.require(len(wire.canonical(body['bundle'])) <= mesh.MAX_BATCH,'TCP exchange byte bound')
    exchange = mesh.verify(body['bundle'],'exchange',network)
    mesh.require(exchange['node_id']==body['node_id'] and exchange['to']==recipient,'TCP request/bundle identity mismatch')
    return body


def check_response(value, network, requester, peer, sent):
    body=mesh.verify(value,'tcp-response',network)
    mesh.require(set(body)=={'format','adapter','network','node_id','to','nonce','exchange_id','accepted','bundle','error'}
        and body['adapter']==ADAPTER and body['node_id']==peer and body['to']==requester
        and body['nonce']==sent['body']['nonce'] and body['exchange_id']==mesh.digest(sent['body']['bundle']),
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
    def __init__(self,config,listen=('127.0.0.1',0)):
        self.config=copy.deepcopy(config)
        with mesh.Node(config) as node:
            self.id,self.network,self.key=node.id,node.network,node.key
            self.peers={peer:dict(c) for peer,c in node.contacts.items() if 'host' in c}
        self.running=True
        self.guard=threading.Lock()
        self.connections=set()
        self.workers=set()
        self.observations={}
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
        try:
            deadline=time.monotonic()+ATTEMPT_SECONDS
            value=receive(connection,deadline)
            body=check_request(value,self.network,self.id,self.peers)
            peer=body['node_id']
            accepted,bundle=False,None
            try:
                with mesh.Node(self.config,nonblocking=True) as node:
                    mesh.require(node.id==self.id,'TCP runtime identity changed')
                    node.receive(body['bundle'],peer)
                    accepted=True  # receive fsyncs its complete verified state first.
                    bundle=outgoing(node,peer)
                self.mark(peer,'inbound',True)
            except (OSError,ValueError):
                accepted,bundle=False,None
                self.mark(peer,'inbound',False)
            response=mesh.sign(self.key,'tcp-response',{'format':mesh.VERSION,'adapter':ADAPTER,'network':self.network,
                'node_id':self.id,'to':peer,'nonce':body['nonce'],'exchange_id':mesh.digest(body['bundle']),
                'accepted':accepted,'bundle':bundle,'error':None if accepted else 'CONTACT_REJECTED'})
            send(connection,response,deadline)
        except (OSError,ValueError,KeyError,TypeError,RecursionError):
            pass  # No unauthenticated/corrupt request receives a custody assertion.
        finally:
            connection.close()
            with self.guard:
                self.connections.discard(connection)
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
                    with mesh.Node(self.config,nonblocking=True) as node:
                        mesh.require(node.id==self.id,'TCP runtime identity changed')
                        sent=request(node,peer)
                    # No mesh lock is held across connect/write/read.
                    deadline=time.monotonic()+ATTEMPT_SECONDS
                    c=self.peers[peer]
                    with socket.create_connection((c['host'],c['port']),timeout=ATTEMPT_SECONDS) as connection:
                        send(connection,sent,deadline)
                        response=receive(connection,deadline)
                    bundle=check_response(response,self.network,self.id,peer,sent)
                    with mesh.Node(self.config,nonblocking=True) as node:
                        mesh.require(node.id==self.id,'TCP runtime identity changed')
                        node.receive(bundle,peer)
                    self.mark(peer,'outbound',True)
                except (OSError,ValueError,KeyError,TypeError) as error:
                    self.mark(peer,'outbound',False)
                    errors.append(str(error)[:256])
        return {'adapter':ADAPTER,'listener':{'host':self.address[0],'port':self.address[1]},
            'contacts':self.report(),'errors':errors[:mesh.MAX_CONTACTS],
            'limits':{'inbound_workers':MAX_WORKERS,'outbound_contacts_per_tick':MAX_OUTBOUND_PER_TICK,
                'wire_bytes':MAX_WIRE,'local_attempt_seconds':ATTEMPT_SECONDS},
            'encrypted':False,'ledger_acceptance_from_transport':False,'physical_route_qualified':False}

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
