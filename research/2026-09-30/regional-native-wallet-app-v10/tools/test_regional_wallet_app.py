"""Real loopback wallet UI APIs and native persistence/security boundaries."""
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from regional_contact_campaign import Campaign, public, save
from regional_contact_node import Native
from regional_wallet_app import App, Server, MAX_REQUEST
import interstellar_mesh as mesh

BINARY=Path(os.environ.get('RLD_CONTACT_BINARY',str(Path(__file__).resolve().parent/'regional-ledger/target/debug/rld-regional-ledger-candidate'))).resolve()


class WalletAppTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rld-wallet-app-')
        self.root=Path(self.temp.name).resolve()/'fixture'
        self.c=Campaign(BINARY,self.root)
        for _ in range(4):self.c.mine('earth')
        self.c.certify('earth')
        self.native=Native(BINARY,self.root/'earth',public(1),self.c.currency)
        self.wallet=self.root/'owner-wallet'
        self.heads=self.root/'retained-caller-head'
        self.key=self.root/'owner-key.json'
        save(self.key,{'secret_key':bytes([10]*32).hex()});self.key.chmod(0o600)
        self.app=App(self.native,self.wallet,self.heads,public(10),key=self.key,miner=public(10))
        self.app.act({'action':'init'})
        self.server=Server(self.app)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
        self.app.close();self.c.cleanup();self.temp.cleanup()

    def request(self,action,values=None,headers=None,raw=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=35)
        h={'Content-Type':'application/json','Origin':self.server.origin,'Authorization':'Bearer '+self.server.token}
        if headers:h.update(headers)
        body=raw or json.dumps({'action':action,**(values or {})})
        connection.request('POST','/api',body,h)
        response=connection.getresponse();data=json.loads(response.read());status=response.status
        connection.close();return status,data

    def prepare(self,remote=None):
        req={'owner':public(10),'inputs':None,'outputs':[] if remote else [{'owner':public(14),'amount':'30'}],
            'remote':remote,'fee':'1','valid_for_blocks':8}
        status,p=self.request('prepare',{'request':req});self.assertEqual(status,200,p)
        return p

    def sign(self,p):
        return self.request('sign',{'review_id':p['review_id'],'review_commitment':p['review_commitment']})

    def test_auth_origin_host_framing_and_static_assets_never_expose_capability(self):
        before=self.app.path.read_bytes()
        for headers in [{'Authorization':'Bearer '+'0'*64},{'Origin':'http://attacker.invalid'},
            {'Host':'attacker.invalid'},{'Sec-Fetch-Site':'cross-site'}]:
            status,_=self.request('status',headers=headers);self.assertNotEqual(status,200)
        status,_=self.request('status',raw='{"action":"status","action":"init"}')
        self.assertNotEqual(status,200)
        status,_=self.request('status',headers={'Content-Length':str(MAX_REQUEST+1)},raw='{}')
        self.assertNotEqual(status,200)
        status,_=self.request('status',values={'key_file':'/other/key'})
        self.assertNotEqual(status,200)
        self.assertEqual(before,self.app.path.read_bytes())
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        c.request('GET','/');r=c.getresponse();body=r.read().decode()
        self.assertEqual(r.status,200);self.assertNotIn(self.server.token,body)
        self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy'])
        self.assertEqual(r.headers['Cache-Control'],'no-store');c.close()
        old=self.server.token
        self.server.token='f'*64
        status,_=self.request('status',headers={'Authorization':'Bearer '+old})
        self.assertNotEqual(status,200)

    def test_opaque_review_native_signature_reservation_and_actual_submission(self):
        p=self.prepare();before=self.native.call('status')['state']
        status,_=self.request('sign',{'review_id':p['review_id'],'review_commitment':'9'*64})
        self.assertNotEqual(status,200)
        status,s=self.sign(p);self.assertEqual(status,200,s)
        self.assertEqual(before,self.native.call('status')['state'])
        status,v=self.request('status');self.assertEqual(status,200)
        self.assertEqual(v['wallet']['reserved_owned_outputs'],'100')
        self.assertEqual(v['wallet']['available'],'100')
        self.assertEqual(v['wallet']['available_onward_export'],'100')
        self.assertNotIn(bytes([10]*32).hex(),json.dumps(v))
        status,recovered=self.request('recover',{'intent':s['intent_id']});self.assertEqual(status,200)
        self.assertEqual(s['commands'],recovered['commands'])
        status,_=self.request('submit',{'intent':s['intent_id']});self.assertEqual(status,200)
        status,v=self.request('status');self.assertEqual(status,200)
        self.assertEqual(v['wallet']['reserved_owned_outputs'],'0')
        self.assertEqual(v['wallet']['signed'][0]['state'],'INCLUDED_IN_LOCAL_LEDGER')
        self.assertFalse(v['wallet']['signed'][0]['local_export_finalized'])
        status,_=self.request('submit',{'intent':s['intent_id']});self.assertNotEqual(status,200)
        self.c.audit('wallet app local signed payment and duplicate submission refusal')

    def test_stale_review_refuses_signing_then_allows_new_explicit_review(self):
        p=self.prepare();head=self.app.saved['head'];self.c.mine('earth')
        status,_=self.sign(p);self.assertNotEqual(status,200)
        self.assertEqual(head,self.app.saved['head']);self.assertIsNone(self.app.saved['pending'])
        self.assertFalse(self.app.failed)
        status,s=self.sign(self.prepare());self.assertEqual(status,200,s)
        self.assertNotEqual(head,self.app.saved['head'])

    def test_recover_only_native_path_and_unsigned_restart_never_first_sign(self):
        p=self.prepare();prepared={k:v for k,v in p.items() if k!='review_id'}
        result=self.c.cli('earth','wallet-sign','--file',self.save_review(prepared),'--review',prepared['review_commitment'],
            '--wallet-dir',self.wallet,'--expected-wallet-head',self.app.saved['head'],'--recover-only','--key-file',self.key,success=False)
        self.assertIn('cannot first-sign',result['reason'])
        head=self.app.saved['head']
        self.app.save(dict(self.app.saved,pending={'prepared':prepared}));self.app.close()
        restored=App(self.native,self.wallet,self.heads,public(10),key=self.key)
        try:
            self.assertEqual(restored.saved['head'],head);self.assertIsNone(restored.saved['pending'])
            v=restored.status();self.assertEqual(v['wallet']['signed'],[])
            self.assertEqual(v['wallet']['reserved_owned_outputs'],'0')
        finally:restored.close()

    def save_review(self,p):
        path=self.root/'reviewed-native.json';save(path,p);return path

    def test_native_signature_survives_lost_response_and_head_write_failure_without_key(self):
        p=self.prepare();previous=self.app.saved['head'];real_save=self.app.save
        def interrupted(proposed):
            if proposed['head']!=previous:raise OSError('fixture post-sign head persistence failure')
            real_save(proposed)
        with patch.object(self.app,'save',side_effect=interrupted):
            status,_=self.sign(p)
        self.assertNotEqual(status,200);self.assertTrue(self.app.failed)
        self.assertIsNotNone(mesh.load(self.app.path,8*1024*1024)['pending'])
        self.app.close();self.key.unlink()
        restored=App(self.native,self.wallet,self.heads,public(10))
        try:
            self.assertNotEqual(previous,restored.saved['head']);self.assertIsNone(restored.saved['pending'])
            v=restored.status();self.assertEqual(v['wallet']['reserved_owned_outputs'],'100')
            recovered=restored.act({'action':'recover','intent':p['draft']['intent_id']})
            self.assertTrue(recovered['recovered_exact_retry'])
            self.assertEqual(len(v['wallet']['signed']),1)
        finally:restored.close()

    def test_surviving_caller_head_rejects_old_wallet_backup_and_preserves_bytes(self):
        path=self.wallet/'wallet.json';backup=path.read_bytes()
        status,_=self.sign(self.prepare());self.assertEqual(status,200)
        latest_head=self.app.path.read_bytes();self.app.close();path.write_bytes(backup)
        with self.assertRaises(ValueError):App(self.native,self.wallet,self.heads,public(10))
        self.assertEqual(path.read_bytes(),backup);self.assertEqual(self.app.path.read_bytes(),latest_head)

    def test_remote_export_finality_and_recipient_states_are_separate(self):
        remote={'destination':self.c.regions['proxima'],'recipient':{'owner':public(11),'amount':'99'},'destination_fee':'1'}
        p=self.prepare(remote);status,s=self.sign(p);self.assertEqual(status,200)
        status,_=self.request('submit',{'intent':s['intent_id']});self.assertEqual(status,200)
        _,v=self.request('status');self.assertFalse(v['wallet']['signed'][0]['local_export_finalized'])
        self.c.certify('earth');_,v=self.request('status');self.assertTrue(v['wallet']['signed'][0]['local_export_finalized'])
        frame=self.c.cli('earth','contact-export','--export',s['intent_id'])
        frame_path=self.root/'carried-frame.json';save(frame_path,frame)
        pending=self.c.cli('proxima','contact-apply','--file',frame_path)
        dest=App(Native(BINARY,self.root/'proxima',public(1),self.c.currency),self.root/'dest-wallet',self.root/'dest-head',public(11))
        expectation={'currency':self.c.currency,'source':self.c.regions['earth'],'destination':self.c.regions['proxima'],
            'export':s['intent_id'],'recipient':public(11),'net_amount':'98'}
        try:
            r=dest.act({'action':'receipt','expectation':expectation});self.assertEqual(r['state'],'VERIFIED_EVIDENCE_PENDING_IMPORT')
            self.c.cli('proxima','contact-resume','--message',pending['message_id'],'--miner',public(10))
            r=dest.act({'action':'receipt','expectation':expectation});self.assertEqual(r['state'],'IMPORT_ACCEPTED_IMMATURE')
            self.c.mine('proxima');self.c.mine('proxima')
            r=dest.act({'action':'receipt','expectation':expectation});self.assertTrue(r['original_output_spendable_now'])
            self.assertFalse(r['remote_current_state_known']);self.assertFalse(r['transport_receipt_checked'])
        finally:dest.close()
        self.c.audit('wallet app source finality, independent destination import and mature receipt')


if __name__=='__main__':unittest.main()
