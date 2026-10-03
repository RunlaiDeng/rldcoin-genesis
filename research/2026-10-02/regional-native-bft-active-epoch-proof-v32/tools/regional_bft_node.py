#!/usr/bin/env python3
"""Bounded autonomous ground consensus companion; native Rust owns all votes.

Only explicitly configured, admitted validator keys sign. Authenticated mesh
carriage supplies bytes, not authority. Caller-head consent survives response
loss independently of the signer/runtime directories. No stellar RTT claim.
"""
import fcntl
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time

import interstellar_mesh as mesh
import interstellar_transfer as wire
from regional_bft_retention import Messages, pack_state, unpack_state
from regional_bft_joint_epoch import JointEpoch, FORMAT as JOINT_FORMAT, signed_body

FORMAT = 'RLD-REGIONAL-BFT-NODE-V1'
NETWORK = 'RLD-REGIONAL-BFT-NETWORK-V2'
MAX_MESSAGES = 512
MAX_STATE = 32*1024*1024


def private(path, directory=False, missing=False):
    path = Path(path)
    mesh.require(path.is_absolute() and not any(p.is_symlink() for p in [path, *path.parents]), 'BFT private path must be absolute without symlinks')
    if missing and not path.exists():
        private(path.parent,True)
        return path
    info = path.lstat()
    mesh.require((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))
                 and info.st_uid == os.getuid() and not info.st_mode & 0o077
                 and (directory or info.st_nlink == 1), 'BFT private ownership/type/permissions invalid')
    return path


class Runtime:
    def __init__(self, native, transport, path):
        self.native, self.transport = native, transport
        self.failed = False
        self.lock = self.head_lock = None
        self.extra_locks = []
        self.joint = None
        self.last_error = None
        config = mesh.load(private(path), 65536)
        fields={'format','state','signer_dir','head_file','key_file','key','miner','validators','block_interval','round_timeout','stop_height'}
        mesh.require((set(config)==fields and config['format']==FORMAT)
                     or (set(config)==fields|{'joint_epoch'} and config['format']==JOINT_FORMAT),
                     'BFT configuration fields/version invalid')
        self.format=config['format']
        self.key, self.miner = mesh.hex32(config['key']), mesh.hex32(config['miner'])
        self.root = mesh.safe_dir(config['state'])
        private(self.root, True)
        self.signer = private(config['signer_dir'], True)
        self.head_path = private(config['head_file'])
        private(self.head_path.parent,True)
        self.key_file = private(config['key_file'],missing=True)
        mesh.require(all(self.head_path.parent != p and p not in self.head_path.parents for p in (self.root, self.signer, native.ledger)),
                     'BFT caller head must survive signer/runtime/ledger directory backups')
        mesh.require(type(config['block_interval']) in (float,int) and 0.5 <= config['block_interval'] <= 3600
                     and type(config['round_timeout']) in (float,int) and 2 <= config['round_timeout'] <= 3600,
                     'BFT local ground timing outside bound')
        mesh.integer(config['stop_height'], 0, 64)
        self.block_interval, self.round_timeout, self.stop_height = config['block_interval'], config['round_timeout'], config['stop_height']
        try:
            for directory, attr in ((self.root,'lock'), (self.head_path.parent,'head_lock')):
                fd = os.open(directory/'.bft-runtime.lock', os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW, 0o600)
                setattr(self,attr,fd)
                info = os.fstat(fd)
                mesh.require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and not info.st_mode & 0o077 and info.st_nlink == 1, 'BFT runtime lock invalid')
                fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            current = native.call('bft-context')
            self.region = current['context']['region']
            validators = config['validators']
            mesh.require(isinstance(validators,list) and len(validators)==4
                         and (config['format']==JOINT_FORMAT or [v['key'] for v in validators] == current['keys'])
                         and all(set(v)=={'key','node_id'} for v in validators), 'BFT configured validator membership differs from signed admission')
            self.peers = {mesh.hex32(v['key']): mesh.hex32(v['node_id']) for v in validators}
            mesh.require(len(set(self.peers.values())) == 4 and self.key in self.peers, 'BFT validator carrier identities duplicate or key absent')
            with mesh.Node(transport) as node:
                mesh.require(node.id == self.peers[self.key] and node.network == native.currency, 'configured BFT carrier differs from local mesh identity')
                self.node_id = node.id
            self.binding = {'currency':native.currency,'region':self.region,'key':self.key}
            self.signing_binding=self.binding
            self.head=self.load_head(self.head_path,self.signing_binding)
            if self.format==JOINT_FORMAT:
                self.joint=JointEpoch(self,config['joint_epoch'],validators,current)
            self.state_path = self.root/'state.json'
            if self.state_path.exists() or self.state_path.is_symlink():
                self.state = unpack_state(mesh.load(private(self.state_path),MAX_STATE))
                mesh.require(set(self.state)=={'format','binding','messages','height','tip','snapshot_cache','cursor'}
                             and self.state['format']==self.format and self.state['binding']==self.binding, 'BFT runtime state binding differs')
                mesh.integer(self.state['height'],0,64)
                mesh.integer(self.state['cursor'],0,2**63-1)
                mesh.require(isinstance(self.state['messages'],Messages) and len(self.state['messages'])<=MAX_MESSAGES
                             and isinstance(self.state['snapshot_cache'],list) and len(self.state['snapshot_cache'])<=64, 'BFT runtime retained capacity invalid')
                for ident, message in self.state['messages'].items():
                    mesh.require(set(message)=={'envelope','value','local'} and type(message['local']) is bool and ident==mesh.digest(message['envelope']['body']), 'BFT runtime message ID changed')
                    verified = self.with_json('bft-network-check',message['envelope'])
                    mesh.require(verified['value']==message['value'], 'BFT runtime message value changed')
            else:
                self.state = {'format':self.format,'binding':self.binding,'messages':Messages(),'height':0,'tip':self.region,'snapshot_cache':[],'cursor':0}
                self.save(self.state)
            if self.joint is not None:
                self.joint.startup()
            else:
                if self.head['pending'] is not None:self.reconcile()
                self.signer_status()
                self.flush_outbox()
            self.observe()
            retained_dirs=[self.signer] if self.joint is None else [self.joint.old['signer'],self.joint.new['signer']]
            for directory in retained_dirs:
                if not directory.exists():continue
                for message in self.native.call('bft-retained-messages','--signer-dir',directory):
                    self.retain(self.envelope({'Signed':message}),sync=False,local=True)
            proof=self.native.call('proof')
            local=[s for s in proof['snapshots'] if s['statement']['region']==self.region and s['statement']['height']==self.state['height']]
            if local:
                self.retain(self.envelope({'Finalized':local[0]}),sync=False,local=True)
            self.slot = None
            self.entered_at = time.monotonic()
        except BaseException:
            self.close()
            raise

    def close(self):
        for descriptor in self.extra_locks:os.close(descriptor)
        self.extra_locks=[]
        for attr in ('lock','head_lock'):
            descriptor=getattr(self,attr,None)
            if descriptor is not None:
                os.close(descriptor)
                setattr(self,attr,None)

    def save(self, state):
        packed=pack_state(state)
        mesh.require(not self.failed and len(wire.canonical(packed))<=MAX_STATE, 'BFT runtime persistence unavailable/capacity')
        try:
            mesh.atomic(self.state_path,packed)
        except BaseException:
            self.failed=True
            raise
        self.state=state

    def save_head(self, value):
        mesh.require(not self.failed and len(wire.canonical(value))<=8*1024*1024, 'BFT caller-head persistence unavailable/capacity')
        try:
            mesh.atomic(self.head_path,value)
        except BaseException:
            self.failed=True
            raise
        self.head=value

    def with_json(self, action, value, *args):
        with tempfile.NamedTemporaryFile(dir=self.root,prefix='.native-',suffix='.json') as handle:
            handle.write(wire.canonical(value))
            handle.flush()
            os.fsync(handle.fileno())
            return self.native.call(action,'--commands' if action=='bft-candidate' else '--file',handle.name,*args)

    def load_head(self,path,binding,allow_initialization=False):
        value=mesh.load(private(path),8*1024*1024)
        fields={'format','binding','head','pending','outbox'}|({'initialization'} if allow_initialization else set())
        mesh.require(set(value)==fields and value['format']==self.format and value['binding']==binding,
                     'BFT external caller-head binding differs')
        if value['head'] is None:
            mesh.require(allow_initialization and value['pending'] is None and value['outbox'] is None,
                         'only fresh explicit new slot may lack a native head')
        else:mesh.hex32(value['head'])
        return value

    def signer_status(self):
        if self.joint is not None and self.joint.active=='new' and self.head['head'] is None:
            mesh.require(not self.signer.exists() or self.head['initialization'] is not None,
                         'new native journal cannot be adopted without retained initialization')
            return {'binding':self.signing_binding,'head':None,'state':None,'records':None,'uninitialized_late_new_signer':True}
        value=self.native.call('bft-status','--signer-dir',self.signer)
        mesh.require(value['binding']==self.signing_binding and value['head']==self.head['head'], 'BFT signer differs from separately retained caller head')
        return value

    def reconcile(self):
        request=self.head['pending']
        try:
            result=self.with_json('bft-sign',request,'--signer-dir',self.signer,'--expected-head',self.head['head'],'--recover-only')
        except (OSError,ValueError,subprocess.TimeoutExpired):
            # Read-only equality proves that this pending request did not advance
            # the retained native history. Never adopt a different native head.
            self.signer_status()
            self.save_head(dict(self.head,pending=None))
            return
        self.save_head(dict(self.head,head=result['head'],pending=None,outbox=result['message']))

    def flush_outbox(self):
        if self.head['outbox'] is not None:
            self.retain(self.envelope({'Signed':self.head['outbox']}),sync=False,local=True)
            self.save_head(dict(self.head,outbox=None))

    def sign(self, request):
        private(self.key_file)
        mesh.require(self.head['pending'] is None and self.head['outbox'] is None, 'BFT signer has unreconciled request/response')
        self.signer_status()
        self.save_head(dict(self.head,pending=request))
        result=self.with_json('bft-sign',request,'--signer-dir',self.signer,'--expected-head',self.head['head'],'--key-file',self.key_file)
        self.save_head(dict(self.head,head=result['head'],pending=None,outbox=result['message']))
        self.flush_outbox()
        # Give a newly persisted local phase time to propagate. Native one-vote
        # rules bound these resets; arbitrary peer traffic cannot renew a timer.
        self.entered_at=time.monotonic()

    def envelope(self, body):
        if self.joint is not None:body=self.joint.decorate(body)
        envelope={'format':NETWORK,'currency':self.native.currency,'region':self.region,
                  'evidence':self.native.call('proof'),'body':body}
        envelope=self.with_json('bft-network-pack',envelope)
        mesh.require(len(wire.canonical(envelope))<=wire.MAX_PAYLOAD,'BFT network payload capacity; retain signed native response')
        return envelope

    def observe(self):
        value=self.native.call('bft-context')['context']
        mesh.require(value['parent_height']>=self.state['height']
                     and (value['parent_height']!=self.state['height'] or value['parent_block']==self.state['tip']),
                     'BFT native ledger rolled back beneath retained runtime observation')
        if value['parent_height']!=self.state['height']:
            self.save(dict(self.state,height=value['parent_height'],tip=value['parent_block']))
        return value

    def retain(self, envelope, sync=True, local=False):
        ident=mesh.digest(envelope['body'])
        # A retained signed body does not authenticate a later envelope's proof.
        # Check every complete envelope before deduplication and let newly
        # certified dependencies reach native sync without replacing old bytes.
        verified=self.with_json('bft-network-check',envelope)
        mesh.require(ident in self.state['messages'] or len(self.state['messages'])<MAX_MESSAGES,
                     'BFT message capacity; retain existing evidence')
        # Use only the complete evidence returned by native wire reconstruction
        # and authentication. Python neither expands prefixes nor grants rights.
        snapshots=list(verified['evidence']['snapshots'])
        if 'Finalized' in envelope['body']:
            final=envelope['body']['Finalized']
            if not any(s['statement']==final['statement'] for s in snapshots):
                snapshots.append(final)
        fingerprints=[mesh.digest(s['statement']) for s in snapshots]
        if sync and any(f not in self.state['snapshot_cache'] for f in fingerprints):
            self.with_json('bft-sync',{'snapshots':snapshots})
            self.observe()
            self.save(dict(self.state,snapshot_cache=sorted(set(self.state['snapshot_cache']+fingerprints))))
        if sync and self.joint is not None:
            proofs=verified.get('epochs',[])
            activation=envelope['body'].get('EpochActivation')
            # This observation is reconstructed by native replay under this
            # store's pinned trust, after every complete received envelope was
            # authenticated and its newly certified dependencies synchronized.
            # Compare full canonical proof bytes, never a statement/body digest
            # or a retained Python cache. An exact already installed proof needs
            # no second proof/pack/activation operation; all other proofs still
            # take the ordinary native activation path.
            installed=self.native.call('bft-context')['active_epoch_proof'] if proofs or activation is not None else None
            def present(proof):
                raw=wire.canonical(proof)
                return installed is not None and raw==wire.canonical(installed)
            if activation is not None and not present(activation):
                self.with_json('bft-epoch-activate',envelope)
                installed=self.native.call('bft-context')['active_epoch_proof']
            for proof in proofs:
                if not present(proof):
                    self.with_json('bft-epoch-activate',self.envelope({'EpochActivation':proof}))
                    installed=self.native.call('bft-context')['active_epoch_proof']
            self.joint.advance()
            self.observe()
        if ident in self.state['messages']:
            if local and not self.state['messages'].record(ident)['local']:
                messages=self.state['messages'].with_local(ident)
                self.save(dict(self.state,messages=messages))
            return
        messages=self.state['messages'].append(ident,envelope,verified['value'],local)
        self.save(dict(self.state,messages=messages))

    def receive(self, raw):
        frame,payload=wire.inspect_frame(raw)
        mesh.require(frame['kind']=='regional-bft' and frame['source_chain_id']==self.region, 'BFT received foreign region/carriage kind')
        self.retain(wire.decode_json(payload))

    def broadcast(self):
        # Deduplicate from the durable mesh itself across enqueue response loss.
        with mesh.Node(self.transport) as node:
            retained=set()
            for summary in node.summaries().values():
                if summary['source']==node.id and summary['kind']=='regional-bft':
                    retained.add((summary['export_id'],summary['destination']))
            messages=sorted(i for i,_,_,local in self.state['messages'].bodies() if local)
            pending=[]
            for ident in messages:
                content=self.state['messages'].content(ident)
                for peer in sorted(set(self.peers.values())-{self.node_id}):
                    if (content,peer) not in retained:
                        pending.append((content,ident,peer))
            # Already enqueued archive messages must not consume the entire
            # selection batch and delay a newly persisted vote for many ticks.
            # Rotate only unsent message/recipient pairs, preserving every byte.
            if pending:
                offset=self.state['cursor']%len(pending)
                pending=(pending[offset:]+pending[:offset])[:4]
            for content,ident,peer in pending:
                payload=self.state['messages'].payload(ident)
                node.enqueue(wire.make_frame('regional-bft',self.region,self.region,content,payload),peer)
        self.save(dict(self.state,cursor=(self.state['cursor']+4)%(2**63)))

    def signed(self, context, round_number, kind, phase=None, value=None):
        result=[]
        for _,body,message_value,_ in self.state['messages'].bodies():
            message=signed_body(body)
            if kind not in message:
                continue
            payload=message[kind]
            c=payload.get('context') if kind!='Proposal' else None
            if kind=='Proposal':
                s=payload['snapshot']['statement']
                matches=(s['currency']==context['currency'] and s['region']==context['region']
                         and s['epoch']==context['epoch'] and s['previous']==context['previous']
                         and s['height']==context['parent_height']+1)
            else:
                matches=c==context
            if (matches and payload['round']==round_number and (phase is None or payload.get('phase')==phase)
                    and (value is None or message_value==value)):
                result.append((payload,message_value))
        return result

    def quorum(self, context, round_number, phase, value):
        voters={v['approval']['key']:v for v,_ in self.signed(context,round_number,'Vote',phase,value)}
        if len(voters)<3:
            return None
        return self.with_json('bft-quorum',[voters[k] for k in sorted(voters)[:3]])

    def timeout_certificate(self, context, round_number):
        voters={v['approval']['key']:v for v,_ in self.signed(context,round_number,'Timeout')}
        if len(voters)<3:
            return None
        return self.with_json('bft-timeout-certificate',[voters[k] for k in sorted(voters)[:3]])

    def candidate(self, context, high=None):
        if high is not None:
            for _,body,message_value,_ in self.state['messages'].bodies():
                p=signed_body(body).get('Proposal')
                if p and message_value==high and p['snapshot']['statement']['height']==context['parent_height']+1:
                    return p['snapshot']
            raise ValueError('highest prepared value retained without its proposal; wait for carriage')
        commands=[]
        incoming=[]
        if self.joint is not None:
            plan=self.joint.plan_command(context)
            if plan is not None:incoming.append(plan)
        for _,body,_,_ in self.state['messages'].bodies():
            incoming.extend(body.get('Submission',body.get('EpochSubmission',{}).get('commands',[])))
        incoming.extend(self.native.call('bft-pending-imports'))
        seen=set()
        for command in incoming:
            ident=mesh.digest(command)
            if ident in seen or len(commands)>=4:
                continue
            seen.add(ident)
            try:
                self.with_json('bft-candidate',commands+[command],'--miner',self.miner)
            except ValueError:
                continue  # retain stale/invalid submission; never rewrite or cancel it.
            commands.append(command)
        return self.with_json('bft-candidate',commands,'--miner',self.miner)

    def tick(self):
        mesh.require(not self.failed, 'BFT runtime requires restart after persistence failure')
        if self.head['pending'] is not None:
            self.reconcile()
        self.flush_outbox()
        queue=self.native.ledger/'bft-submissions'
        if queue.exists():
            private(queue,True)
            files=sorted(queue.iterdir())
            mesh.require(len(files)<=32, 'BFT submission spool capacity')
            for path in files[:32]:
                # Native serde field order is not the mesh's sorted JSON wire
                # order. Bound/read the native file, then let Rust authenticate
                # its complete typed contents before canonical wire packing.
                envelope=wire.decode_json(wire.read_file(private(path),wire.MAX_PAYLOAD))
                if mesh.digest(envelope['body']) not in self.state['messages']:
                    self.retain(envelope,local=True)
        if self.joint is not None and self.joint.tick():
            self.broadcast()
            context=self.observe()
            status=self.signer_status()
            return self.report(context,None,status,stopped=True)
        context=self.observe()
        status=self.signer_status()
        active=status['state'] if status['state'] is not None and status['state']['context']==context else {'round':0,'prepared':None,'committed':None,'proposed':False}
        round_number=active['round']
        slot=(mesh.digest(context),round_number)
        if self.slot!=slot:
            self.slot,self.entered_at=slot,time.monotonic()
        stopped=context['parent_height']>=self.stop_height or not self.key_file.exists() or self.head['head'] is None
        # A local timeout does not invalidate a complete certificate for this
        # parent. Install delayed certified rounds even after moving ahead, and
        # even in read-only/keyless mode; only Rust authorizes the state change.
        for certified_round in range(32):
            for proposal,value in self.signed(context,certified_round,'Proposal'):
                prepared=self.quorum(context,certified_round,'Prepare',value)
                committed=self.quorum(context,certified_round,'Commit',value)
                if prepared is not None and committed is not None:
                    certificate=self.with_json('bft-certify',{'proposal':proposal,'prepared':prepared,'committed':committed})
                    self.with_json('finalize',certificate)
                    self.retain(self.envelope({'Finalized':certificate}),sync=False,local=True)
                    self.observe()
                    self.broadcast()
                    return self.report(context,round_number,status,stopped=self.state['height']>=self.stop_height)
        if not stopped:
            for proposal,value in self.signed(context,round_number,'Proposal'):
                prepared=self.quorum(context,round_number,'Prepare',value)
                if active['prepared'] is None:
                    self.sign({'Prepare':proposal})
                    break
                if active['prepared']==value and active['committed'] is None and prepared is not None:
                    self.sign({'Commit':{'proposal':proposal,'prepared':prepared}})
                    break
            else:
                leader=sorted(self.peers)[(context['parent_height']+round_number)%4]
                tc=None if round_number==0 else self.timeout_certificate(context,round_number-1)
                if (leader==self.key and not active['proposed'] and (round_number==0 or tc is not None)
                        and time.monotonic()-self.entered_at>=self.block_interval):
                    highs=[v['high'] for v in tc['votes'] if v['high'] is not None] if tc else []
                    high=max(highs,key=lambda q:q['round'])['value'] if highs else None
                    self.sign({'Propose':{'round':round_number,'snapshot':self.candidate(context,high),'timeout':tc}})
            # Learn certified future rounds rather than timing out forever one
            # round behind. Native Prepare validates the immediate timeout QC.
            future=[]
            for later in range(round_number+1,32):
                future.extend(self.signed(context,later,'Proposal'))
            if future:
                proposal,_=max(future,key=lambda p:p[0]['round'])
                self.sign({'Prepare':proposal})
            elif time.monotonic()-self.entered_at>=min(3600,self.round_timeout*(round_number+1)):
                self.sign({'Timeout':{'context':context,'round':round_number}})
        self.broadcast()
        return self.report(context,round_number,status,stopped)

    def report(self, context, round_number, status, stopped):
        return {'format':self.format,'currency':self.native.currency,'region':self.region,'validator':self.key,
                'height':self.state['height'],'round':None if status['state'] is None else round_number,'native_records':status['records'],
                'retained_messages':len(self.state['messages']),'autonomous_signing_enabled':self.key_file.exists() and self.head['head'] is not None,
                'joint_epoch_lifecycle_enabled':self.joint is not None,'joint_active_slot':self.joint.active if self.joint is not None else None,
                'explicit_stop_height_reached':self.state['height']>=self.stop_height,'caller_head_pending':self.head['pending'] is not None,
                'caller_head_rollback_qualification':False,'independent_bft_qualified':False,
                'physical_interstellar_route_qualified':False,'local_ground_timing_only':True}
