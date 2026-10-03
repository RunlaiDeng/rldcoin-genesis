#!/usr/bin/env python3
"""Cold native/custody verification after a completed no-value fault drill.

Read only after owned processes stop. The separate verifier never signs,
constructs a quorum, applies evidence or installs a checkpoint. It reports only
sanitized projections; private journals, keys, configs and backups stay local.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    result={};total=0
    for p in root.rglob('*'):
        if p.is_symlink():raise ValueError('private fixture symlink refused')
        if p.is_file():
            s=p.stat();total+=s.st_size
            if len(result)>=65536 or s.st_size>64*1024*1024 or total>6*1024**3:
                raise ValueError('private fixture verification capacity exceeded')
            result[str(p.relative_to(root))]=(sha(p),s.st_uid,s.st_mode,s.st_nlink)
    return result


def verify(args):
    stage=args.source.resolve();root=args.root.resolve();binary=args.binary.resolve()
    manifest=json.loads(args.manifest.read_text());run=json.loads(args.run_report.read_text())
    commitment=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if commitment!=manifest['source_set_sha256'] or commitment!=run['runtime_source_set_sha256']:
        raise ValueError('named runtime commitment differs')
    for entry in manifest['files']:
        p=stage/entry['path']
        if not p.resolve().is_relative_to(stage) or any(q.is_symlink() for q in [p,*p.parents]) or not p.is_file() or p.stat().st_size!=entry['size_bytes'] or sha(p)!=entry['sha256']:
            raise ValueError('frozen source changed: '+entry['path'])
    if sha(stage/'tools/regional_bft_sustained_campaign.py')!=run['drill_source_sha256']:
        raise ValueError('executed drill source differs')
    if not (run['completed'] and run['fixture_only'] and not run['live_rld']
            and run['sealed_source_state_unchanged'] and run['owned_process_cleanup_verified']):
        raise ValueError('completed stopped no-value drill required; preserve failed evidence')
    if run.get('mode','fresh_fault_profile')!='fresh_fault_profile':
        raise ValueError('retained-payment recovery is separately scoped; fresh full-profile verification refused')
    for field in ('controller_generated_consensus_messages','controller_carried_payment_proofs','controller_installed_checkpoints'):
        if run[field]!=0:raise ValueError('controller authority/carriage exceeded declared scope')
    for line in subprocess.check_output(['ps','-A','-o','args='],text=True).splitlines():
        if str(root) in line and (line.startswith(str(binary)) or
                (line.split() and Path(line.split()[0]).name.lower().startswith('python') and 'regional_contact_node.py' in line)):
            raise ValueError('owned fixture process still running; cold verification refused')
    before=files(root)
    sys.path.insert(0,str(stage/'tools'))
    import interstellar_mesh as mesh
    from regional_contact_node import Native
    bootstrap=json.loads((root/'bootstrap.json').read_text())
    currency=bootstrap['admissions'][0]['currency'];authority=bootstrap['currency']['authority']
    if bootstrap['currency']['implementation']!=manifest['native_implementation'] or run['native_implementation']!=manifest['native_implementation']:
        raise ValueError('native implementation binding differs')
    expected=json.loads((root/'sustained-receipt-expectation.json').read_text())
    if expected['currency']!=currency or expected['net_amount']!='9':raise ValueError('exact retained payment expectation differs')
    ledgers=[];rows=[];archive_rows=[];receipts=[]
    for name in ('earth','proxima','andromeda'):
        states=[]
        for n in range(4):
            native=Native(binary,root/f'{name}-{n}',authority,currency)
            state=native.call('status');states.append(state)
            if not state['fixture_only'] or state['live_rld']:raise ValueError('native fixture domain differs')
            config=mesh.load(root/f'bft-config-{name}-{n}.json',65536)
            head=mesh.load(Path(config['head_file']),8*1024*1024)
            signer=native.call('bft-status','--signer-dir',config['signer_dir'])
            binding={'currency':currency,'region':state['region'],'key':config['key']}
            if signer['binding']!=binding or head['binding']!=binding or signer['head']!=head['head'] or head['pending'] is not None or head['outbox'] is not None:
                raise ValueError('caller head/outbox unresolved after claimed quiescence')
            if name=='earth' and expected['export'] not in state['ledger']['exports']:raise ValueError('original export debit missing')
            if name=='proxima':
                receipt=native.call('wallet-receipt','--file',root/'sustained-receipt-expectation.json')
                if not (receipt['expected']==expected and receipt['import_accepted'] and receipt['maturity_reached']
                        and receipt['original_output_spendable_now'] and receipt['local_finality_covers_import']
                        and not receipt['quarantined'] and receipt['original_output_remaining']=='9'):
                    raise ValueError('native recipient debit/import/maturity binding differs')
                receipts.append(receipt)
            rows.append({'region':name,'replica':n,'height':state['height'],'tip':state['tip'],'native_signer_records':signer['records'],'separate_head_matches':True})
            with mesh.Node(mesh.load(root/f'mesh-config-{name}-{n}.json',65536)) as node:
                for ident in node.state['archives']:node.archived(ident)
                inventory,total=node.archive_inventory()
                archive_rows.append({'region':name,'replica':n,'archived_records':len(node.state['archives']),
                                     'retained_files':len(inventory),'retained_bytes':total,'full_cold_authentication':True})
        for state in states[1:]:
            if any(state[k]!=states[0][k] for k in ('height','tip','state','ledger','finality','validator_epoch')):
                raise ValueError('cold native replicas disagree')
        if states[0]['height']!=run['result']['final_heights'][name]:raise ValueError('terminal height differs')
        ledgers.append(states[0]['ledger'])
    issued=sum(int(l['minted']) for l in ledgers)
    liquid=sum(int(c['payment']['amount']) for l in ledgers for c in l['coins'].values())
    transit=sum(int(e['recipient']['amount']) for l in ledgers for e in l['exports'].values())-sum(int(l['received']) for l in ledgers)
    if issued!=liquid+transit or transit<0:raise ValueError('native conservation failed')
    if files(root)!=before:raise ValueError('private fixture changed during read-only verification')
    report={'format':'RLD-SUSTAINED-COLD-VERIFICATION-V1','fixture_only':True,'live_rld':False,'same_host_same_controller':True,
            'run_report_sha256':sha(args.run_report),'source_set_sha256':commitment,'verifier_sha256':sha(Path(__file__)),
            'native_implementation':manifest['native_implementation'],'binary_sha256':sha(binary),'native_replays':12,
            'replicas':rows,'native_replicas_agree':True,'recipient_checks':len(receipts),'new_export_debit_retained':True,
            'unique_import_and_original_output_maturity_verified':True,'native_conservation':{'issued':str(issued),'liquid':str(liquid),'in_transit':str(transit),'conserved':True},
            'archive_reads':archive_rows,'all_private_fixture_files_unchanged':True,
            'within_recorded_observation_bounds':all(p['elapsed_seconds']<=p['observation_bound_seconds'] for p in run['observations']),
            'sustained_BFT_liveness_qualified':False,'independent_operators_qualified':False,'cross_host_qualified':False,'power_loss_qualified':False,'physical_route_qualified':False}
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'cold_verified':True,'native_replays':12,'authenticated_archive_records':sum(r['archived_records'] for r in archive_rows)}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','manifest','run-report','binary','root','report'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    try:verify(args)
    except Exception as error:
        raise SystemExit(str(error).replace(str(args.root.resolve()),'<private-fixture>')) from None


if __name__=='__main__':main()
