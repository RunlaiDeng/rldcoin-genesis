"""Actual loopback sockets: multi-hop custody, restart and hostile admission."""
import copy
from pathlib import Path
import socket
import struct
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import interstellar_mesh as mesh
import interstellar_tcp as tcp
import interstellar_transfer as wire

NETWORK = 'a'*64


class Fixture:
    def __init__(self, root, names=('earth','proxima','andromeda'), edges=None):
        self.root=Path(root).resolve()
        self.names=list(names)
        self.ids={n:mesh.initialize(self.root/n,NETWORK,str(i+1)*64,n)['node_id']
            for i,n in enumerate(names)}
        self.ports={}
        self.servers={}
        held=[]
        try:
            for name in names:
                s=socket.socket()
                s.bind(('127.0.0.1',0))
                held.append(s)
                self.ports[name]=s.getsockname()[1]
            self.configs={n:{'format':mesh.VERSION,'state':str(self.root/n),
                'network':NETWORK,'contacts':[]} for n in names}
            for a,b in edges or list(zip(names,names[1:])):
                for source,target in [(a,b),(b,a)]:
                    self.configs[source]['contacts'].append({'peer':self.ids[target],
                        'host':'127.0.0.1','port':self.ports[target]})
        finally:
            for s in held:
                s.close()
        for name in names:
            self.start(name)

    def start(self,name):
        self.servers[name]=tcp.Server(self.configs[name],('127.0.0.1',self.ports[name]))

    def stop(self,name):
        self.servers.pop(name).close()

    def close(self):
        for name in list(self.servers):
            self.stop(name)

    def rounds(self,count=5):
        for _ in range(count):
            for server in list(self.servers.values()):
                server.tick()

    def node(self,name):
        return mesh.Node(self.configs[name])

    def frame(self,index=0):
        return wire.make_frame('source-finality','1'*64,'3'*64,'4'*64,
            wire.canonical({'ground_fixture':index,'ledger_validation':'required'}))


class TcpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f=Fixture(self.temp.name)
        self.addCleanup(self.f.close)

    def exchange(self,value,target='proxima'):
        with socket.create_connection(self.f.servers[target].address,timeout=2) as c:
            deadline=time.monotonic()+tcp.ATTEMPT_SECONDS
            tcp.send(c,value,deadline)
            return tcp.receive(c,deadline)

    def sent(self):
        with self.f.node('earth') as node:
            return tcp.request(node,self.f.ids['proxima'])

    def await_condition(self,condition):
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            if condition():
                return
            time.sleep(0.01)
        self.fail('bounded socket test observation timeout')

    def test_actual_two_hop_transfer_receipt_and_restart_without_shared_spools(self):
        self.f.rounds()
        with self.f.node('earth') as node:
            self.assertEqual(node.route(self.f.ids['andromeda']),[self.f.ids[n] for n in self.f.names])
            raw=self.f.frame()
            ident=node.enqueue(raw,self.f.ids['andromeda'])
        self.f.rounds()
        self.f.stop('andromeda')
        self.f.start('andromeda')
        self.f.rounds(1)
        with self.f.node('andromeda') as node:
            self.assertEqual(len(node.state['messages'][ident]['hops']),2)
            target=self.f.root/'received.frame.json'
            node.export_received(ident,target)
            self.assertEqual(target.read_bytes(),raw)
            self.assertFalse(node.status()['payment_authorized'])
        with self.f.node('earth') as node:
            self.assertEqual(node.status()['messages'][ident],'EVIDENCE_STORED_NOT_LEDGER_ACCEPTED')
            self.assertIn(ident,node.state['messages'])
        self.assertFalse((self.f.root/'links').exists())
        for name,server in self.f.servers.items():
            self.assertTrue(server.report()['observations'])
            self.assertTrue(all('host' in c and 'inbox' not in c for c in self.f.configs[name]['contacts']))

    def test_disconnected_middle_and_sender_restart_retain_then_resume(self):
        self.f.rounds()
        self.f.stop('proxima')
        with self.f.node('earth') as node:
            ident=node.enqueue(self.f.frame(),self.f.ids['andromeda'])
        self.assertTrue(self.f.servers['earth'].tick()['errors'])
        self.f.stop('earth')
        self.f.start('earth')
        with self.f.node('earth') as node:
            self.assertIn(ident,node.state['messages'])
            self.assertNotIn(ident,node.state['receipts'])
        self.f.start('proxima')
        self.f.rounds()
        with self.f.node('earth') as node:
            self.assertIn(ident,node.state['receipts'])

    def test_added_alternate_socket_route_delivers_after_preferred_relay_stops(self):
        f=Fixture(self.f.root/'diamond',('source','left','right','destination'),
            [('source','left'),('left','destination'),('source','right'),('right','destination')])
        self.addCleanup(f.close)
        f.stop('right')
        f.rounds()
        with f.node('source') as node:
            self.assertEqual(len(node.state['adverts']),3)
        f.start('right')
        f.rounds()
        with f.node('source') as node:
            self.assertEqual(len(node.state['adverts']),4)
            preferred=node.route(f.ids['destination'])[1]
            ident=node.enqueue(f.frame(),f.ids['destination'])
        stopped=next(n for n in ('left','right') if f.ids[n]==preferred)
        f.stop(stopped)
        f.rounds()
        with f.node('destination') as node:
            self.assertIn(ident,node.state['receipts'])
            self.assertNotIn(preferred,mesh.transit_check(node.state['messages'][ident],NETWORK)[2])

    def test_duplex_concurrent_contacts_do_not_hold_mesh_locks_across_waits(self):
        errors=[]
        threads=[threading.Thread(target=lambda s=s:errors.extend(s.tick()['errors']))
            for s in self.f.servers.values()]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=8)
            self.assertFalse(thread.is_alive(),'cross-node lock deadlock')
        # A simultaneous local writer may conservatively refuse; retry succeeds.
        self.f.rounds()
        with self.f.node('earth') as node:
            self.assertEqual(len(node.state['adverts']),3)

    def test_response_loss_exact_request_retry_deduplicates_durable_custody(self):
        self.f.rounds()
        with self.f.node('earth') as node:
            ident=node.enqueue(self.f.frame(),self.f.ids['proxima'])
        sent=self.sent()
        with socket.create_connection(self.f.servers['proxima'].address,timeout=2) as c:
            tcp.send(c,sent,time.monotonic()+tcp.ATTEMPT_SECONDS)
            # Sender disappears before reading an acknowledgment.
        path=self.f.root/'proxima/mesh-state.json'
        self.await_condition(lambda:ident in mesh.load(path,mesh.MAX_STATE)['messages'])
        response=self.exchange(sent)
        tcp.check_response(response,NETWORK,self.f.ids['earth'],self.f.ids['proxima'],sent)
        with self.f.node('proxima') as node:
            self.assertEqual(list(node.state['messages']),[ident])
            self.assertIn(ident,node.state['receipts'])
        with self.f.node('earth') as node:
            self.assertIn(ident,node.state['messages'])
            self.assertNotIn(ident,node.state['receipts'])

    def test_wrong_nonce_recipient_network_and_identity_cannot_acknowledge(self):
        sent=self.sent()
        response=self.exchange(sent)
        body=response['body']
        with self.f.node('proxima') as node:
            for field,value in [('nonce','f'*64),('to',self.f.ids['andromeda']),('network','f'*64),
                    ('exchange_id','e'*64),('accepted','true')]:
                forged=mesh.sign(node.key,'tcp-response',{**body,field:value})
                with self.assertRaises(ValueError):
                    tcp.check_response(forged,NETWORK,self.f.ids['earth'],node.id,sent)
        with self.f.node('andromeda') as node:
            forged=mesh.sign(node.key,'tcp-response',{**body,'node_id':node.id})
        with self.assertRaises(ValueError):
            tcp.check_response(forged,NETWORK,self.f.ids['earth'],self.f.ids['proxima'],sent)
        newer=self.sent()
        with self.assertRaises(ValueError):
            tcp.check_response(response,NETWORK,self.f.ids['earth'],self.f.ids['proxima'],newer)

    def test_unconfigured_peer_tamper_and_oversize_frame_leave_receiver_unchanged(self):
        sent=self.sent()
        before=(self.f.root/'proxima/mesh-state.json').read_bytes()
        with self.f.node('earth') as node:
            wrong_to=mesh.sign(node.key,'tcp-request',{**sent['body'],'to':self.f.ids['andromeda']})
            wrong_net=mesh.sign(node.key,'tcp-request',{**sent['body'],'network':'f'*64})
        with self.f.node('andromeda') as node:
            forged=mesh.sign(node.key,'tcp-request',{**sent['body'],'node_id':node.id})
        # Andromeda is a configured neighbor of Proxima; Earth cannot impersonate it.
        tamper=copy.deepcopy(sent)
        tamper['body']['bundle']['body']['adverts'][0]['body']['label']='forged'
        stranger=mesh.initialize(self.f.root/'stranger',NETWORK,'f'*64,'stranger')
        config={'format':mesh.VERSION,'state':str(self.f.root/'stranger'),'network':NETWORK,'contacts':[]}
        with mesh.Node(config) as node:
            unknown=tcp.request(node,self.f.ids['proxima'])
        self.assertNotIn(stranger['node_id'],self.f.servers['proxima'].peers)
        for value in (wrong_to,wrong_net,forged,tamper,unknown):
            with self.assertRaises((OSError,ValueError)):
                self.exchange(value)
        with socket.create_connection(self.f.servers['proxima'].address,timeout=2) as c:
            c.sendall(struct.pack('!I',tcp.MAX_WIRE+1))
            self.assertEqual(c.recv(1),b'')
        self.assertEqual(before,(self.f.root/'proxima/mesh-state.json').read_bytes())

    def test_busy_receiver_or_failed_commit_refuses_ack_and_keeps_evidence(self):
        self.f.rounds()
        with self.f.node('earth') as node:
            ident=node.enqueue(self.f.frame(),self.f.ids['proxima'])
        sent=self.sent()
        with self.f.node('proxima') as node:
            before=node.path.read_bytes()
            response=self.exchange(sent)
            self.assertFalse(response['body']['accepted'])
            self.assertEqual(before,node.path.read_bytes())
        original=mesh.atomic
        target=self.f.root/'proxima/mesh-state.json'
        def fail_custody(path,value):
            if Path(path)==target and ident in value.get('messages',{}):
                raise OSError('injected durable write failure')
            return original(path,value)
        with patch.object(mesh,'atomic',side_effect=fail_custody):
            response=self.exchange(sent)
            self.assertFalse(response['body']['accepted'])
        self.assertEqual(before,target.read_bytes())
        with self.f.node('earth') as node:
            self.assertIn(ident,node.state['messages'])
        self.f.rounds()
        with self.f.node('proxima') as node:
            self.assertIn(ident,node.state['receipts'])

    def test_bounded_capacity_refusal_preserves_prior_state_and_source_queue(self):
        self.f.rounds()
        with self.f.node('proxima') as node:
            node.enqueue(self.f.frame(1),'b'*64)
            before=node.path.read_bytes()
        with self.f.node('earth') as node:
            ident=node.enqueue(self.f.frame(2),self.f.ids['proxima'])
        sent=self.sent()
        with patch.object(mesh,'MAX_MESSAGES',1):
            response=self.exchange(sent)
        self.assertFalse(response['body']['accepted'])
        self.assertEqual(before,(self.f.root/'proxima/mesh-state.json').read_bytes())
        with self.f.node('earth') as node:
            self.assertIn(ident,node.state['messages'])
            self.assertNotIn(ident,node.state['receipts'])

    def test_bounded_workers_oversize_and_incomplete_input_close_cleanly(self):
        server=self.f.servers['proxima']
        clients=[socket.create_connection(server.address,timeout=2) for _ in range(tcp.MAX_WORKERS)]
        for c in clients:
            self.addCleanup(c.close)
            c.sendall(b'\x00')
        self.await_condition(lambda:len(server.workers)==tcp.MAX_WORKERS)
        with socket.create_connection(server.address,timeout=2) as c:
            self.assertEqual(c.recv(1),b'')
        self.await_condition(lambda:server.report()['refused_connections']==1)
        server.close()
        self.assertFalse(server.thread.is_alive())
        self.assertFalse(server.workers)
        self.assertFalse(server.connections)

    def test_more_than_one_batch_rotates_and_delivers_all_retained_packets(self):
        self.f.rounds()
        with self.f.node('earth') as node:
            ids=[node.enqueue(self.f.frame(i),self.f.ids['andromeda']) for i in range(11)]
        self.f.rounds(14)
        with self.f.node('earth') as node:
            self.assertEqual(set(ids),set(node.state['receipts']))
            self.assertEqual(set(ids),set(node.state['messages']))

    def test_operator_endpoint_schema_rejects_dns_urls_ipv6_and_zero_contact_port(self):
        for host,port in [('localhost',1000),('https://example.com',80),('::1',1000),
                ('127.0.0.1',0),('0.0.0.0',1000),('224.0.0.1',1000),('127.0.0.1',True)]:
            config=copy.deepcopy(self.f.configs['earth'])
            config['contacts'][0].update(host=host,port=port)
            with self.assertRaises(ValueError):
                mesh.Node(config)

    def test_deep_invalid_json_is_rejected_and_listener_still_accepts_valid_exchange(self):
        before=(self.f.root/'proxima/mesh-state.json').read_bytes()
        raw=b'['*2000+b'0'+b']'*2000
        with socket.create_connection(self.f.servers['proxima'].address,timeout=2) as c:
            c.sendall(struct.pack('!I',len(raw))+raw)
            self.assertEqual(c.recv(1),b'')
        self.assertEqual(before,(self.f.root/'proxima/mesh-state.json').read_bytes())
        response=self.exchange(self.sent())
        self.assertTrue(response['body']['accepted'])


if __name__=='__main__':
    unittest.main()
