"""Actual native joint caller recovery; no mocked cryptographic authority."""
import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import interstellar_mesh as mesh
from regional_bft_autonomous_epoch_campaign import Campaign
from regional_bft_node import Runtime
from regional_contact_node import Native
from regional_contact_campaign import public

BINARY=Path(os.environ.get('RLD_CONTACT_BINARY',str(Path(__file__).parent/'regional-ledger/target/debug/rld-regional-ledger-candidate'))).resolve()


class JointRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rld-joint-caller-')
        self.c=Campaign(BINARY,Path(self.temp.name).resolve()/'fixture')
        for n in range(4):
            self.c.configs[n]['joint_epoch']['select_height']=1
            self.c.file(f'bft-config-{n}',self.c.configs[n]).chmod(0o600)
        context=self.c.cli('earth',1,'bft-context')['context']
        plan={'currency':self.c.currency,'region':self.c.regions['earth'],'previous_epoch':context['epoch'],
              'number':1,'validators':[public(s) for s in self.c.new_seeds]}
        self.c.checkpoint('earth',[{'Reconfigure':plan}])
        self.scope=self.c.cli('earth',1,'bft-epoch-proposal')
        self.native=Native(BINARY,self.c.node('earth',1),public(1),self.c.currency)
        self.runtime=None
        self.update_old_heads()

    def update_old_heads(self):
        for n in range(4):
            path=self.c.root/f'caller-head-{n}/head.json'
            mesh.atomic(path,dict(mesh.load(path,8*1024*1024),head=self.c.heads['earth',n]))

    def tearDown(self):
        if self.runtime:self.runtime.close()
        self.c.cleanup();self.temp.cleanup()

    def open(self):
        self.runtime=Runtime(self.native,mesh.load(self.c.root/'mesh-config-1.json',65536),self.c.root/'bft-config-1.json')
        return self.runtime

    def activation(self):
        proof=copy.deepcopy(self.scope['proposal'])
        for n in (1,2,3):
            context=self.c.cli('earth',n,'bft-context')['context']
            receipt=self.c.sign('earth',n,{'EpochFence':{'context':context,**self.scope}})
            proof['old_approvals'].append(receipt['message']['EpochApproval']['approval'])
            head=mesh.load(self.c.root/f'candidate-caller-{n}/head.json',8*1024*1024)['head']
            signed=self.c.cli('earth',n,'sign-handoff','--signer-dir',self.c.root/f'candidate-{n}',
                              '--expected-lock',head,'--file',self.c.file(f'activation-{n}',self.scope['proposal']),
                              '--key-file',self.c.root/f'next-key-{n}.json')
            proof['new_approvals'].append(signed['approval'])
            path=self.c.root/f'candidate-caller-{n}/head.json'
            mesh.atomic(path,dict(mesh.load(path,8*1024*1024),head=signed['lock_head']))
        self.update_old_heads()
        for n in (1,2,3):self.c.cli('earth',n,'install-epoch','--file',self.c.file('complete-activation',proof))
        return proof

    def test_candidate_lost_response_recovers_exact_without_private_key_after_activation(self):
        runtime=self.open();joint=runtime.joint
        joint.save_approval(dict(joint.approval,pending=self.scope))
        response=runtime.with_json('sign-handoff',self.scope['proposal'],'--signer-dir',joint.approval_dir,
                                  '--expected-lock',joint.approval['head'],'--key-file',joint.new['key_file'])
        runtime.close();self.runtime=None
        # Build a valid full activation retaining this exact candidate response.
        proof=copy.deepcopy(self.scope['proposal'])
        for n in (1,2,3):
            context=self.c.cli('earth',n,'bft-context')['context']
            old=self.c.sign('earth',n,{'EpochFence':{'context':context,**self.scope}})
            proof['old_approvals'].append(old['message']['EpochApproval']['approval'])
            if n==1:proof['new_approvals'].append(response['approval']);continue
            path=self.c.root/f'candidate-caller-{n}/head.json';head=mesh.load(path,8*1024*1024)
            new=self.c.cli('earth',n,'sign-handoff','--signer-dir',self.c.root/f'candidate-{n}',
                           '--expected-lock',head['head'],'--file',self.c.file(f'approval-{n}',self.scope['proposal']),
                           '--key-file',self.c.root/f'next-key-{n}.json')
            proof['new_approvals'].append(new['approval'])
        self.update_old_heads()
        self.c.cli('earth',1,'install-epoch','--file',self.c.file('activated',proof))
        joint.new['key_file'].unlink()
        restored=self.open();self.assertEqual(restored.joint.approval['head'],response['lock_head'])
        self.assertIsNone(restored.joint.approval['pending']);self.assertIsNone(restored.joint.approval['outbox'])
        self.assertEqual(restored.joint.approval_status()['votes'],1)
        self.assertTrue(any(body.get('EpochApproval',{}).get('approval')==response['approval']
                            for _,body,_,_ in restored.state['messages'].bodies()))

    def test_candidate_unsigned_pending_never_first_signs(self):
        runtime=self.open();head=runtime.joint.approval['head']
        runtime.joint.save_approval(dict(runtime.joint.approval,pending=self.scope))
        runtime.close();self.runtime=None
        restored=self.open()
        self.assertEqual(restored.joint.approval['head'],head)
        self.assertEqual(restored.joint.approval_status()['votes'],0)
        self.assertIsNone(restored.joint.approval['pending'])

    def test_candidate_persistence_failure_prevents_native_handoff(self):
        runtime=self.open();joint=runtime.joint;before=(joint.approval_dir/'signer.json').read_bytes()
        atomic=mesh.atomic
        def fail(path,value):
            if path==joint.approval_path:raise OSError('injected independent candidate head failure')
            return atomic(path,value)
        with patch.object(mesh,'atomic',side_effect=fail),self.assertRaises(OSError):joint.tick()
        self.assertTrue(runtime.failed)
        self.assertEqual((joint.approval_dir/'signer.json').read_bytes(),before)

    def test_new_empty_native_initialization_lost_response_recovers_exact_marker(self):
        self.activation();call=self.native.call
        def lost(action,*args):
            response=call(action,*args)
            if action=='bft-init':raise OSError('injected native creation response loss')
            return response
        with patch.object(self.native,'call',side_effect=lost),self.assertRaises(OSError):self.open()
        path=self.c.root/'next-caller-1/head.json';retained=mesh.load(path,8*1024*1024)
        self.assertIsNone(retained['head']);self.assertIsNotNone(retained['initialization'])
        (self.c.root/'next-key-1.json').unlink()
        restored=self.open();status=restored.signer_status()
        self.assertEqual(status['records'],0);self.assertEqual(status['creation'],retained['initialization'])
        self.assertIsNone(restored.head['initialization']);self.assertEqual(restored.head['head'],status['head'])

    def test_new_empty_journal_without_independent_marker_refuses_unchanged(self):
        self.activation();self.native.call('bft-init','--signer-dir',self.c.root/'next-voter-1','--key',public(self.c.new_seeds[1]))
        path=self.c.root/'next-caller-1/head.json';head=path.read_bytes()
        journal=self.c.root/'next-voter-1/bft.json';before=journal.read_bytes()
        with self.assertRaisesRegex(ValueError,'without retained initialization'):self.open()
        self.assertEqual(journal.read_bytes(),before)
        self.assertIsNone(mesh.load(path,8*1024*1024)['initialization'])
        self.assertIsNone(mesh.load(path,8*1024*1024)['head'])
        self.assertEqual(path.read_bytes(),head)

    def test_candidate_old_backup_refuses_latest_independent_head(self):
        runtime=self.open();joint=runtime.joint;path=joint.approval_dir/'signer.json';old=path.read_bytes()
        joint.save_approval(dict(joint.approval,pending=self.scope))
        response=runtime.with_json('sign-handoff',self.scope['proposal'],'--signer-dir',joint.approval_dir,
                                  '--expected-lock',joint.approval['head'],'--key-file',joint.new['key_file'])
        joint.reconcile_approval();self.assertEqual(joint.approval['head'],response['lock_head'])
        latest=joint.approval_path.read_bytes();runtime.close();self.runtime=None
        path.write_bytes(old);path.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'separately retained caller head'):self.open()
        self.assertEqual(joint.approval_path.read_bytes(),latest)

    def test_new_voter_old_backup_refuses_latest_independent_head(self):
        self.activation();runtime=self.open();path=runtime.signer/'bft.json';old=path.read_bytes()
        runtime.sign({'Timeout':{'context':self.native.call('bft-context')['context'],'round':0}})
        latest=runtime.head_path.read_bytes();runtime.close();self.runtime=None
        path.write_bytes(old);path.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'separately retained caller head'):self.open()
        self.assertEqual((self.c.root/'next-caller-1/head.json').read_bytes(),latest)

    def test_initialization_marker_failure_prevents_native_directory_creation(self):
        self.activation();path=self.c.root/'next-caller-1/head.json';before=path.read_bytes();atomic=mesh.atomic
        def fail(destination,value):
            if destination==path:raise OSError('injected initialization marker failure')
            return atomic(destination,value)
        with patch.object(mesh,'atomic',side_effect=fail),self.assertRaises(OSError):self.open()
        self.assertEqual(path.read_bytes(),before);self.assertFalse((self.c.root/'next-voter-1').exists())

    def test_new_voter_lost_response_recovers_before_startup_head_comparison(self):
        self.activation();runtime=self.open()
        request={'Timeout':{'context':self.native.call('bft-context')['context'],'round':0}}
        runtime.save_head(dict(runtime.head,pending=request))
        response=runtime.with_json('bft-sign',request,'--signer-dir',runtime.signer,
                                  '--expected-head',runtime.head['head'],'--key-file',runtime.key_file)
        runtime.key_file.unlink();runtime.close();self.runtime=None
        restored=self.open()
        self.assertEqual(restored.head['head'],response['head'])
        self.assertIsNone(restored.head['pending']);self.assertIsNone(restored.head['outbox'])
        self.assertEqual(restored.signer_status()['records'],1)

    def test_nonparticipant_at_historical_boundary_remains_keyless_readonly(self):
        proof=self.activation()
        envelope={'format':'RLD-REGIONAL-BFT-NETWORK-V2','currency':self.c.currency,
                  'region':self.c.regions['earth'],'evidence':self.c.cli('earth',1,'proof'),
                  'body':{'EpochActivation':proof}}
        packed=self.c.cli('earth',0,'bft-network-pack','--file',self.c.file('boundary-envelope',envelope))
        self.c.cli('earth',0,'bft-epoch-activate','--file',self.c.file('boundary-wire',packed))
        native=Native(BINARY,self.c.node('earth',0),public(1),self.c.currency)
        self.runtime=runtime=Runtime(native,mesh.load(self.c.root/'mesh-config-0.json',65536),self.c.root/'bft-config-0.json')
        self.assertEqual(runtime.joint.active,'new');self.assertIsNone(runtime.head['head'])
        self.assertIsNone(runtime.signer_status()['records'])
        self.assertFalse((self.c.root/'next-voter-0').exists())
        runtime.tick();self.assertFalse((self.c.root/'next-voter-0').exists())
        self.assertEqual(runtime.joint.approval_status()['votes'],0)

    def test_wallet_signing_height_replays_native_finalize_and_epoch_events(self):
        self.activation();runtimes={1:self.open()}
        try:
            for n in (2,3):
                native=Native(BINARY,self.c.node('earth',n),public(1),self.c.currency)
                runtimes[n]=Runtime(native,mesh.load(self.c.root/f'mesh-config-{n}.json',65536),self.c.root/f'bft-config-{n}.json')
            def sign(n,request):
                runtime=runtimes[n];runtime.sign(request)
                return runtime.native.call('bft-retained-messages','--signer-dir',runtime.signer)[-1]
            for height in (2,3):
                leader=height-1
                snapshot=self.native.call('bft-candidate','--miner',public(10),'--commands',self.c.file('empty-new-commands',[]))
                proposal=sign(leader,{'Propose':{'round':0,'snapshot':snapshot,'timeout':None}})['Proposal']
                votes=[sign(n,{'Prepare':proposal})['Vote'] for n in (1,2,3)]
                prepared=runtimes[1].with_json('bft-quorum',votes)
                votes=[sign(n,{'Commit':{'proposal':proposal,'prepared':prepared}})['Vote'] for n in (1,2,3)]
                committed=runtimes[1].with_json('bft-quorum',votes)
                certificate=runtimes[1].with_json('bft-certify',{'proposal':proposal,'prepared':prepared,'committed':committed})
                for runtime in runtimes.values():runtime.with_json('finalize',certificate)
            wallet=self.c.root/'new-era-owner-wallet'
            created=self.native.call('wallet-init','--wallet-dir',wallet,'--owner',public(10))
            request={'owner':public(10),'inputs':None,'outputs':[{'owner':public(14),'amount':'30'}],
                     'remote':None,'fee':'1','valid_for_blocks':8}
            draft=self.native.call('wallet-prepare','--wallet-dir',wallet,'--expected-wallet-head',created['wallet_head'],
                                   '--file',self.c.file('new-era-owner-request',request))
            key=self.c.file('owner-private-input',{'secret_key':(bytes([10])*32).hex()});key.chmod(0o600)
            before=self.native.call('status')['ledger']
            signed=self.native.call('wallet-sign','--wallet-dir',wallet,'--expected-wallet-head',draft['wallet_head'],
                                    '--file',self.c.file('new-era-owner-review',draft),'--review',draft['review_commitment'],'--key-file',key)
            self.assertEqual(self.native.call('status')['ledger'],before)
            view=self.native.call('wallet-view','--wallet-dir',wallet,'--expected-wallet-head',signed['wallet_head'])
            self.assertNotEqual(view['reserved_owned_outputs'],'0')
        finally:
            for n in (2,3):
                if n in runtimes:runtimes[n].close()

    def test_stopped_joint_retention_requires_explicit_native_admission_and_authenticates_every_envelope(self):
        from regional_bft_retention import verify_stopped_state
        self.activation();runtime=self.open();runtime.close();self.runtime=None
        config=mesh.load(self.c.root/'bft-config-1.json',65536)
        before=(Path(config['state'])/'state.json').read_bytes()
        result=verify_stopped_state(self.native,config,self.native.call('status'),self.c.root)
        self.assertTrue(result['full_native_authentication']);self.assertGreater(result['messages_authenticated'],0)
        self.assertEqual((Path(config['state'])/'state.json').read_bytes(),before)
        with self.assertRaises(ValueError):
            verify_stopped_state(self.native,dict(config,format='RLD-REGIONAL-BFT-NODE-V1'),self.native.call('status'),self.c.root)

    def test_exact_installed_activation_is_checked_every_time_without_reinstalling(self):
        proof=self.activation();runtime=self.open()
        envelope=runtime.envelope({'EpochActivation':proof})
        before=(self.c.node('earth',1)/'journal.json').read_bytes()
        heads=[p.read_bytes() for p in (runtime.head_path,runtime.joint.approval_path,runtime.joint.old['head_path'])]
        with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls:
            runtime.retain(envelope);retained=runtime.state['messages'].payload(mesh.digest(envelope['body']))
            runtime.retain(copy.deepcopy(envelope))
        actions=[c.args[0] for c in calls.call_args_list]
        self.assertEqual(actions.count('bft-network-check'),2)
        self.assertNotIn('bft-epoch-activate',actions)
        self.assertEqual(retained,runtime.state['messages'].payload(mesh.digest(envelope['body'])))
        self.assertEqual((self.c.node('earth',1)/'journal.json').read_bytes(),before)
        self.assertEqual([p.read_bytes() for p in (runtime.head_path,runtime.joint.approval_path,runtime.joint.old['head_path'])],heads)

    def test_installed_carried_epoch_does_not_skip_invalid_later_complete_envelope(self):
        proof=self.activation();runtime=self.open()
        runtime.sign({'Timeout':{'context':self.native.call('bft-context')['context'],'round':0}})
        message=self.native.call('bft-retained-messages','--signer-dir',runtime.signer)[-1]
        envelope=runtime.envelope({'EpochSigned':{'message':message,'epochs':[proof]}})
        with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls:runtime.retain(envelope)
        self.assertIn('bft-network-check',[c.args[0] for c in calls.call_args_list])
        self.assertNotIn('bft-epoch-activate',[c.args[0] for c in calls.call_args_list])
        retained=runtime.state['messages'].payload(mesh.digest(envelope['body']))
        before={p:p.read_bytes() for p in [self.c.node('earth',1)/'journal.json',runtime.state_path,runtime.head_path,
                                           runtime.joint.approval_path,runtime.joint.old['head_path']]}
        foreign=copy.deepcopy(envelope);foreign['currency']='ff'*32
        forged=copy.deepcopy(envelope)
        approval=forged['evidence']['snapshots'][0]['snapshot']['bft']['committed']['votes'][0]['approval']
        signature=approval['signature'];approval['signature']=('0' if signature[0]!='0' else '1')+signature[1:]
        for altered in (foreign,forged):
            with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls,self.assertRaises(ValueError):
                runtime.retain(altered)
            self.assertEqual([c.args[0] for c in calls.call_args_list],['bft-network-check'])
            self.assertEqual(retained,runtime.state['messages'].payload(mesh.digest(envelope['body'])))
            self.assertTrue(all(p.read_bytes()==raw for p,raw in before.items()))

    def test_valid_different_complete_quorum_proof_still_uses_native_activation(self):
        proof=self.activation();runtime=self.open();variant=copy.deepcopy(proof)
        self.c.cli('earth',0,'bft-sync','--file',self.c.file('fourth-boundary',self.c.cli('earth',1,'proof')))
        context=self.c.cli('earth',0,'bft-context')['context']
        signed=self.c.sign('earth',0,{'EpochFence':{'context':context,**self.scope}})
        variant['old_approvals'].append(signed['message']['EpochApproval']['approval'])
        head=mesh.load(self.c.root/'candidate-caller-0/head.json',8*1024*1024)['head']
        new=self.c.cli('earth',0,'sign-handoff','--signer-dir',self.c.root/'candidate-0',
                       '--expected-lock',head,'--file',self.c.file('fourth-approval',self.scope['proposal']),
                       '--key-file',self.c.root/'next-key-0.json')
        variant['new_approvals'].append(new['approval'])
        for field in ('old_approvals','new_approvals'):variant[field].sort(key=lambda a:a['key'])
        self.assertEqual(variant['statement'],proof['statement']);self.assertNotEqual(variant,proof)
        installed=self.native.call('bft-context')['epochs']
        envelope=runtime.envelope({'EpochActivation':variant})
        with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls:runtime.retain(envelope)
        self.assertEqual([c.args[0] for c in calls.call_args_list].count('bft-epoch-activate'),1)
        self.assertEqual(self.native.call('bft-context')['epochs'],installed)

    def test_missing_native_activation_still_installs_before_keyless_advance(self):
        proof=self.activation()
        envelope={'format':'RLD-REGIONAL-BFT-NETWORK-V2','currency':self.c.currency,
                  'region':self.c.regions['earth'],'evidence':self.c.cli('earth',1,'proof'),
                  'body':{'EpochActivation':proof}}
        packed=self.c.cli('earth',0,'bft-network-pack','--file',self.c.file('fresh-wire',envelope))
        native=Native(BINARY,self.c.node('earth',0),public(1),self.c.currency)
        self.runtime=runtime=Runtime(native,mesh.load(self.c.root/'mesh-config-0.json',65536),self.c.root/'bft-config-0.json')
        self.assertEqual(runtime.joint.active,'old')
        with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls:runtime.retain(packed)
        self.assertEqual([c.args[0] for c in calls.call_args_list].count('bft-epoch-activate'),1)
        self.assertEqual(runtime.joint.active,'new');self.assertFalse((self.c.root/'next-voter-0').exists())
        self.assertIsNone(runtime.head['head']);self.assertEqual(runtime.joint.approval_status()['votes'],0)

    def test_native_known_transition_is_not_reported_as_an_active_epoch(self):
        proof=self.activation();runtimes={1:self.open()}
        try:
            for n in (2,3):
                native=Native(BINARY,self.c.node('earth',n),public(1),self.c.currency)
                runtimes[n]=Runtime(native,mesh.load(self.c.root/f'mesh-config-{n}.json',65536),self.c.root/f'bft-config-{n}.json')
            def sign(n,request):
                runtimes[n].sign(request)
                return runtimes[n].native.call('bft-retained-messages','--signer-dir',runtimes[n].signer)[-1]
            snapshot=self.native.call('bft-candidate','--miner',public(10),'--commands',self.c.file('known-era-empty',[]))
            proposal=sign(1,{'Propose':{'round':0,'snapshot':snapshot,'timeout':None}})['Proposal']
            prepared=runtimes[1].with_json('bft-quorum',[sign(n,{'Prepare':proposal})['Vote'] for n in (1,2,3)])
            committed=runtimes[1].with_json('bft-quorum',[sign(n,{'Commit':{'proposal':proposal,'prepared':prepared}})['Vote'] for n in (1,2,3)])
            certificate=runtimes[1].with_json('bft-certify',{'proposal':proposal,'prepared':prepared,'committed':committed})
            runtimes[1].with_json('finalize',certificate)
            evidence=self.native.call('proof')
        finally:
            for runtime in runtimes.values():runtime.close()
            self.runtime=None
        # Retain a fully native-verified future prefix without adopting local
        # ledger progress. Its carried epoch is knowledge, not activation.
        self.c.cli('earth',0,'evidence','--file',self.c.file('known-not-active',evidence))
        observed=self.c.cli('earth',0,'bft-context')
        self.assertTrue(observed['epochs']);self.assertIsNone(observed['active_epoch_proof'])
        self.assertEqual(observed['context']['parent_height'],0)
        native=Native(BINARY,self.c.node('earth',0),public(1),self.c.currency)
        self.runtime=runtime=Runtime(native,mesh.load(self.c.root/'mesh-config-0.json',65536),self.c.root/'bft-config-0.json')
        self.assertEqual(runtime.joint.active,'old')
        envelope=runtime.envelope({'EpochActivation':proof})
        with patch.object(runtime,'with_json',wraps=runtime.with_json) as calls:runtime.retain(envelope)
        actions=[c.args[0] for c in calls.call_args_list]
        self.assertEqual(actions.count('bft-network-check'),1);self.assertEqual(actions.count('bft-sync'),1)
        self.assertNotIn('bft-epoch-activate',actions) # Native sync installed the complete certified prefix.
        active=native.call('bft-context')['active_epoch_proof']
        self.assertEqual(active,proof);self.assertEqual(runtime.joint.active,'new')
        self.assertFalse((self.c.root/'next-voter-0').exists())


if __name__=='__main__':unittest.main()
