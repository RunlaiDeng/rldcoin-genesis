"""Actual native wallet CLI: current review, signed debit and recipient replay.

All keys are public fixtures; temporary keys/state never enter the public report.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from regional_contact_campaign import Campaign, public, save
import interstellar_transfer as wire

BINARY = Path(os.environ.get('RLD_CONTACT_BINARY', str(Path(__file__).resolve().parent/'regional-ledger/target/debug/rld-regional-ledger-candidate'))).resolve()


class NativeWalletTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rld-native-wallet-')
        self.root = Path(self.temp.name).resolve()/'fixture'
        self.c = Campaign(BINARY, self.root)
        self.c.mine('earth')
        self.c.mine('earth')
        self.c.mine('earth')
        self.c.mine('earth')
        self.c.certify('earth')

    def tearDown(self):
        self.c.cleanup()
        self.temp.cleanup()

    def request(self, owner=10, amount=30, remote=None):
        return {'owner':public(owner), 'inputs':None,
            'outputs':[] if remote else [{'owner':public(14), 'amount':str(amount)}],
            'remote':remote, 'fee':'1', 'valid_for_blocks':8}

    def prepare(self, name, request):
        path=self.root/'wallet-request.json'
        save(path, request)
        prepared=self.c.cli(name,'wallet-prepare','--file',path)
        path=self.root/'wallet-reviewed.json'
        save(path,prepared)
        return prepared,path

    def sign(self, name, prepared, path, seed=10, review=None, success=True):
        key=self.root/f'owner-{seed}.json'
        save(key, {'secret_key':(bytes([seed])*32).hex()})
        key.chmod(0o600)
        return self.c.cli(name,'wallet-sign','--file',path,'--key-file',key,
            '--review',review or prepared['review_commitment'],success=success)

    def view(self, name, seed):
        return self.c.cli(name,'wallet-view','--owner',public(seed))

    def receipt(self, expected, success=True):
        path=self.root/'receipt-expectation.json'
        save(path,expected)
        return self.c.cli('proxima','wallet-receipt','--file',path,success=success)

    def test_review_rejection_real_signed_payment_and_current_balance(self):
        before=(self.root/'earth/journal.json').read_bytes()
        prepared,path=self.prepare('earth',self.request())
        self.assertEqual(prepared['draft']['change'],'69')
        self.sign('earth',prepared,path,review='9'*64,success=False)
        self.sign('earth',prepared,path,seed=11,success=False)
        command=self.sign('earth',prepared,path)
        self.assertNotIn((bytes([10])*32).hex(),json.dumps(command))
        self.assertEqual(before,(self.root/'earth/journal.json').read_bytes())
        self.c.mine('earth',command)
        self.assertEqual(self.view('earth',14)['spendable'],'30')
        self.sign('earth',prepared,path,success=False)
        self.c.audit('wallet actual signed local payment')

    def test_remote_export_pending_import_maturity_and_original_output_spent(self):
        remote={'destination':self.c.regions['proxima'],
            'recipient':{'owner':public(11),'amount':'99'},'destination_fee':'1'}
        prepared,path=self.prepare('earth',self.request(remote=remote))
        commands=self.sign('earth',prepared,path)
        self.c.mine('earth',commands)
        export=prepared['draft']['intent_id']
        self.c.certify('earth')
        expected={'currency':self.c.currency,'source':self.c.regions['earth'],
            'destination':self.c.regions['proxima'],'export':export,'recipient':public(11),'net_amount':'98'}
        self.receipt(expected,success=False)
        frame=self.c.cli('earth','contact-export','--export',export)
        frame_path=self.root/'carried-frame.json'
        frame_path.write_bytes(wire.canonical(frame))
        pending=self.c.cli('proxima','contact-apply','--file',frame_path)
        self.assertFalse(pending['import_accepted'])
        self.assertEqual(self.receipt(expected)['state'],'VERIFIED_EVIDENCE_PENDING_IMPORT')
        self.assertEqual(self.view('proxima',11)['spendable'],'0')
        self.c.cli('proxima','contact-resume','--message',pending['message_id'],'--miner',public(10))
        self.assertEqual(self.receipt(expected)['state'],'IMPORT_ACCEPTED_IMMATURE')
        self.c.mine('proxima')
        self.c.mine('proxima')
        receipt=self.receipt(expected)
        self.assertTrue(receipt['original_output_spendable_now'])
        self.assertFalse(receipt['local_finality_covers_import'])
        wrong=dict(expected,recipient=public(14))
        self.receipt(wrong,success=False)
        wrong=dict(expected,net_amount='99')
        self.receipt(wrong,success=False)
        prepared,path=self.prepare('proxima',self.request(owner=11))
        command=self.sign('proxima',prepared,path,seed=11)
        self.c.mine('proxima',command)
        receipt=self.receipt(expected)
        self.assertEqual(receipt['state'],'ORIGINAL_OUTPUT_SPENT')
        self.assertTrue(receipt['import_accepted'])
        self.assertFalse(receipt['original_output_spendable_now'])
        self.assertEqual(self.view('proxima',11)['spendable'],'67')
        self.assertEqual(self.view('proxima',14)['spendable'],'30')
        self.assertFalse(receipt['transport_receipt_checked'])
        self.c.audit('wallet verified onward-ready local recipient payment')


if __name__=='__main__':
    unittest.main()
