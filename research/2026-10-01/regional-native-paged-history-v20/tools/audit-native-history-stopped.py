from pathlib import Path
import argparse,hashlib,json,subprocess,datetime
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--run-report',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads(a.manifest.read_text());run=json.loads(a.run_report.read_text());assert run.get('native_implementation',run.get('implementation'))==m['native_implementation']
for e in m['files']:assert sha(a.source/e['path'])==e['sha256']
assert a.root.is_absolute() and a.binary.is_absolute()
bootstrap=json.loads((a.root/'bootstrap.json').read_text());authority=bootstrap['currency']['authority'];currency=bootstrap['admissions'][0]['currency']
assert bootstrap['currency']['implementation']==m['native_implementation']
assert all(x['currency']==currency for x in bootstrap['admissions'])
if 'currency' in run:assert run['currency']==currency
else:
 assert run['completed'] and run['owned_process_cleanup_verified'] and run['mode']=='fresh_fault_profile'
 assert run['runtime_source_set_sha256']==m['source_set_sha256']
 assert run['result']['recipient']['expected']['currency']==currency
for line in subprocess.check_output(['ps','-A','-o','args='],text=True).splitlines():
 if str(a.root) in line and (line.startswith(str(a.binary)) or ('regional_contact_node.py' in line and line.split() and Path(line.split()[0]).name.lower().startswith('python'))):raise ValueError('owned fixture process still running; stopped audit refused')
assert authority=='8a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c'
before={str(f.relative_to(a.root)):sha(f) for f in a.root.rglob('*') if f.is_file()}
rows=[]
for region in ('earth','proxima','andromeda'):
 for replica in range(4):
  directory=a.root/f'{region}-{replica}'
  assert directory.is_dir(),directory
  def call(*args):
   return json.loads(subprocess.check_output([str(a.binary),'--dir',str(directory),'--authority',authority,'--currency',currency,*args],timeout=30))
  observation=call('history-head');check=call('history-check','--expected-head',observation['history_head']);assert check==observation
  manifest=json.loads((directory/'journal.json').read_text());objects=list((directory/'history').iterdir())
  assert manifest['format']=='RLD-NATIVE-HISTORY-MANIFEST-V1' and observation['logical_native_replay_complete']
  rows.append({'region':region,'replica':replica,'height':observation['height'],'permanent_import_entries':observation['permanent_import_entries'],'external_exact_head_check_passed':True,'native_reconstructed_replay_passed':True,'manifest_bytes':(directory/'journal.json').stat().st_size,'logical_journal_bytes':manifest['journal_bytes'],'referenced_snapshots':len(manifest['snapshots']),'event_pages':len(manifest['pages']),'retained_objects_including_old_tails':len(objects),'retained_object_bytes':sum(f.stat().st_size for f in objects)})
after={str(f.relative_to(a.root)):sha(f) for f in a.root.rglob('*') if f.is_file()};assert before==after
for e in m['files']:assert sha(a.source/e['path'])==e['sha256']
out={'format':'RLD-NATIVE-PAGED-HISTORY-STOPPED-AUDIT-V1','source_set_sha256':m['source_set_sha256'],'native_implementation':m['native_implementation'],'run_report_sha256':sha(a.run_report),'verifier_sha256':sha(Path(__file__)),'replicas':rows,'native_replays_and_exact_head_checks':12,'all_private_files_unchanged':True,'frozen_source_unchanged':True,'fixture_only':True,'live_rld':False,'same_host_same_controller':True,'independent_latest_state_anchor_qualified':False,'long_history_qualified':False,'cross_host_qualified':False,'power_loss_qualified':False,'fresh_target_recovery_implemented':False,'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
a.report.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'native_paged_replays':12,'all_private_files_unchanged':True,'largest_manifest_bytes':max(x['manifest_bytes'] for x in rows),'largest_logical_journal_bytes':max(x['logical_journal_bytes'] for x in rows),'total_event_pages':sum(x['event_pages'] for x in rows)}))
