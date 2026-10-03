"""Actual native signer/caller-head recovery for the autonomous companion."""
import json
import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import interstellar_mesh as mesh
import interstellar_transfer as wire
from regional_bft_network_campaign import Campaign
from regional_bft_node import Runtime
from regional_contact_node import Native
from regional_contact_campaign import public

BINARY=Path(os.environ.get('RLD_CONTACT_BINARY',str(Path(__file__).parent/'regional-ledger/target/debug/rld-regional-ledger-candidate'))).resolve()


class CallerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rld-autonomous-head-')
        self.c=Campaign(BINARY,Path(self.temp.name).resolve()/'fixture')
        self.native=Native(BINARY,self.c.node('earth',1),self.c.invoke([self.c.helper,'bootstrap','--bft'],helper=True)['currency']['authority'],self.c.currency)
        self.transport=mesh.load(self.c.root/'mesh-config-1.json',65536)
        self.path=self.c.root/'bft-config-1.json'
        self.runtime=None

    def tearDown(self):
        if self.runtime:self.runtime.close()
        self.c.cleanup();self.temp.cleanup()

    def open(self):
        self.runtime=Runtime(self.native,self.transport,self.path)
        return self.runtime

    def timeout(self):
        return {'Timeout':{'context':self.native.call('bft-context')['context'],'round':0}}

    def test_response_lost_after_native_sign_recovers_without_private_key_and_never_signs_again(self):
        runtime=self.open();request=self.timeout()
        runtime.save_head(dict(runtime.head,pending=request))
        result=runtime.with_json('bft-sign',request,'--signer-dir',runtime.signer,'--expected-head',runtime.head['head'],'--key-file',runtime.key_file)
        runtime.close();self.runtime=None
        runtime.key_file.unlink()
        restored=self.open()
        self.assertEqual(restored.head['head'],result['head'])
        self.assertIsNone(restored.head['pending']);self.assertIsNone(restored.head['outbox'])
        self.assertEqual(restored.signer_status()['records'],1)
        self.assertTrue(any(m['envelope']['body']=={'Signed':result['message']} for m in restored.state['messages'].values()))
        restored.tick()
        self.assertEqual(restored.signer_status()['records'],1)

    def test_unsigned_pending_recovery_does_not_first_sign(self):
        runtime=self.open();runtime.save_head(dict(runtime.head,pending=self.timeout()))
        old=runtime.head['head'];runtime.close();self.runtime=None
        restored=self.open()
        self.assertEqual(restored.head['head'],old)
        self.assertIsNone(restored.head['pending'])
        self.assertEqual(restored.signer_status()['records'],0)

    def test_genesis_signing_pause_preserves_certified_catchup_without_new_signatures(self):
        native=Native(BINARY,self.c.node('earth',0),public(1),self.c.currency)
        transport=mesh.load(self.c.root/'mesh-config-0.json',65536)
        path=self.c.root/'bft-config-0.json'
        mesh.atomic(path,dict(mesh.load(path,65536),stop_height=0))
        self.runtime=runtime=Runtime(native,transport,path)
        head=runtime.head['head']
        observed=runtime.tick()
        self.assertTrue(observed['explicit_stop_height_reached'])
        self.assertEqual(runtime.signer_status()['records'],0)
        certificate=self.c.checkpoint('earth')
        runtime.retain({'format':'RLD-REGIONAL-BFT-NETWORK-V1','currency':self.c.currency,
                        'region':self.c.regions['earth'],'evidence':self.c.cli('earth',1,'proof'),
                        'body':{'Finalized':certificate}})
        observed=runtime.tick()
        self.assertEqual(observed['height'],1)
        self.assertTrue(observed['explicit_stop_height_reached'])
        self.assertEqual(native.call('status')['tip'],certificate['statement']['block'])
        self.assertEqual(runtime.head['head'],head)
        self.assertEqual(runtime.signer_status()['records'],0)

    def test_old_signer_backup_latest_external_head_refuses_and_preserves_caller_state(self):
        runtime=self.open();path=runtime.signer/'bft.json';old=path.read_bytes()
        runtime.sign(self.timeout());latest=runtime.head_path.read_bytes()
        runtime.close();self.runtime=None
        path.write_bytes(old);path.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'separately retained'):
            self.open()
        self.assertEqual((self.c.root/'caller-head-1/head.json').read_bytes(),latest)

    def test_caller_persistence_failure_prevents_native_signature_release(self):
        runtime=self.open();before=(runtime.signer/'bft.json').read_bytes()
        atomic=mesh.atomic
        def fail(path,value):
            if path==runtime.head_path:raise OSError('injected caller-head persistence failure')
            return atomic(path,value)
        with patch.object(mesh,'atomic',side_effect=fail),self.assertRaises(OSError):
            runtime.sign(self.timeout())
        self.assertTrue(runtime.failed)
        self.assertEqual((runtime.signer/'bft.json').read_bytes(),before)

    def test_regional_consensus_carriage_has_exact_region_currency_and_payload_binding(self):
        runtime=self.open();runtime.sign(self.timeout())
        message=next(iter(runtime.state['messages'].values()))['envelope']
        payload=wire.canonical(message)
        import hashlib
        raw=wire.make_frame('regional-bft',runtime.region,runtime.region,hashlib.sha256(payload).hexdigest(),payload)
        self.assertEqual(wire.inspect_frame(raw)[1],payload)
        altered=json.loads(raw);altered['destination_chain_id']='9'*64
        with self.assertRaises(ValueError):wire.inspect_frame(wire.canonical(altered))
        with self.assertRaises(ValueError):wire.make_frame('finalized-import',runtime.region,runtime.region,'8'*64,payload)
        body=dict(message,currency='a'*64)
        bad=wire.make_frame('regional-bft',runtime.region,runtime.region,hashlib.sha256(wire.canonical(body)).hexdigest(),wire.canonical(body))
        with mesh.Node(self.transport) as node:
            with self.assertRaises(ValueError):
                node.enqueue(bad,node.id)

    def test_native_submission_file_gossips_without_debit_and_tampering_is_rejected(self):
        for _ in range(3):
            self.c.checkpoint('earth')
        head_path=self.c.root/'caller-head-1/head.json'
        head=mesh.load(head_path,8*1024*1024)
        mesh.atomic(head_path,dict(head,head=self.c.heads['earth',1]))
        wallet=self.c.root/'queue-owner-wallet'
        initialized=self.native.call('wallet-init','--wallet-dir',wallet,'--owner',public(10))
        request={'owner':public(10),'inputs':None,'outputs':[{'owner':public(14),'amount':'30'}],
                 'remote':None,'fee':'1','valid_for_blocks':8}
        prepared=self.native.call('wallet-prepare','--wallet-dir',wallet,'--expected-wallet-head',initialized['wallet_head'],
                                  '--file',self.c.file('queue-payment',request))
        key=self.c.file('queue-owner-key',{'secret_key':(bytes([10])*32).hex()});key.chmod(0o600)
        signed=self.native.call('wallet-sign','--wallet-dir',wallet,'--expected-wallet-head',prepared['wallet_head'],
                                '--file',self.c.file('queue-review',prepared),'--review',prepared['review_commitment'],'--key-file',key)
        before=(self.native.ledger/'journal.json').read_bytes()
        self.native.call('bft-submit','--file',self.c.file('queue-commands',signed['commands']))
        queue=next((self.native.ledger/'bft-submissions').iterdir())
        raw=queue.read_bytes();envelope=wire.decode_json(raw)
        self.assertNotEqual(raw,wire.canonical(envelope))
        runtime=self.open();runtime.tick()
        self.assertTrue(any(m['envelope']['body']=={'Submission':signed['commands']} and m['local']
                            for m in runtime.state['messages'].values()))
        self.assertEqual(before,(self.native.ledger/'journal.json').read_bytes())
        bad=copy.deepcopy(envelope)
        # Alter the already signed payment; native validation must reject it.
        command=bad['body']['Submission'][0]
        self.assertIn('Spend',command)
        command['Spend']['intent']['outputs'][0]['amount']='31'
        queue.write_bytes(json.dumps(bad).encode())
        with self.assertRaises(ValueError):runtime.tick()
        self.assertEqual(before,(self.native.ledger/'journal.json').read_bytes())

    def test_delayed_complete_certificate_installs_after_local_timeout_without_private_key(self):
        certificate=self.c.checkpoint('earth')
        native=Native(BINARY,self.c.node('earth',0),public(1),self.c.currency)
        transport=mesh.load(self.c.root/'mesh-config-0.json',65536)
        self.runtime=runtime=Runtime(native,transport,self.c.root/'bft-config-0.json')
        context=native.call('bft-context')['context']
        for round_number in (0,1):
            runtime.sign({'Timeout':{'context':context,'round':round_number}})
        self.assertEqual(runtime.signer_status()['state']['round'],2)
        runtime.key_file.unlink()
        for n in (1,2,3):
            messages=self.c.cli('earth',n,'bft-retained-messages','--signer-dir',self.c.signer('earth',n))
            for message in messages:
                runtime.retain({'format':'RLD-REGIONAL-BFT-NETWORK-V1','currency':self.c.currency,
                                'region':self.c.regions['earth'],'evidence':{'snapshots':[]},'body':{'Signed':message}})
        before=runtime.signer_status()['records']
        runtime.tick()
        status=native.call('status')
        self.assertEqual(status['height'],1)
        self.assertEqual(status['tip'],certificate['statement']['block'])
        self.assertEqual(runtime.signer_status()['records'],before)

    def test_retained_enqueued_history_does_not_delay_a_new_vote_batch(self):
        runtime=self.open();context=self.native.call('bft-context')['context']
        for round_number in range(7):
            runtime.sign({'Timeout':{'context':context,'round':round_number}})
        with mesh.Node(self.transport) as node:
            for message in runtime.state['messages'].values():
                payload=wire.canonical(message['envelope'])
                raw=wire.make_frame('regional-bft',runtime.region,runtime.region,hashlib.sha256(payload).hexdigest(),payload)
                for peer in set(runtime.peers.values())-{runtime.node_id}:node.enqueue(raw,peer)
        previous=set(runtime.state['messages'])
        runtime.sign({'Timeout':{'context':context,'round':7}})
        newest=(set(runtime.state['messages'])-previous).pop()
        ordered=sorted(runtime.state['messages'])
        runtime.save(dict(runtime.state,cursor=(ordered.index(newest)+1)%len(ordered)))
        runtime.broadcast()
        payload=wire.canonical(runtime.state['messages'][newest]['envelope'])
        content=hashlib.sha256(payload).hexdigest();destinations=set()
        with mesh.Node(self.transport) as node:
            for transit in node.state['messages'].values():
                packet,raw,_=mesh.transit_check(transit,node.network)
                frame,_=wire.inspect_frame(raw)
                if frame['export_id']==content:destinations.add(packet['destination'])
        self.assertEqual(destinations,set(runtime.peers.values())-{runtime.node_id})


if __name__=='__main__':unittest.main()
