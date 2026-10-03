//! Bounded full-replay journal; exclusive OS lock and fsync/rename replacement.
//! An external monotonic checkpoint is still required against old-backup rollback.
use super::*;
use crate::conflict::{CertifiedHistory, Conflict, Safety, MAX_INCIDENTS};
use std::{
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum Event {
    Block(Box<Block>),
    Finalize(Hash),
    Epoch(Hash),
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Journal {
    pub bootstrap: Bootstrap,
    pub region: Hash,
    pub evidence: Evidence,
    pub events: Vec<Event>,
    pub incident_ids: BTreeSet<Hash>,
    pub epoch_proofs: Vec<epoch::Transition>,
    pub contact_records: BTreeMap<Hash, crate::contact::Record>,
}
impl Journal {
    pub fn replay(&self, authority: &str, pin: Hash) -> Result<(Trust, VerifiedEvidence, Chain)> {
        require(
            self.events.len() <= MAX_BLOCKS + MAX_SNAPSHOTS + epoch::MAX_EPOCHS,
            "journal event bound",
        )?;
        encode("journal", self)?;
        let trust = Trust::verify(&self.bootstrap, authority, pin)?;
        let mut evidence = VerifiedEvidence::verify(&self.evidence, &trust)?;
        require(
            self.epoch_proofs.len() <= epoch::MAX_EPOCHS,
            "local epoch proof bound",
        )?;
        for proof in &self.epoch_proofs {
            evidence.install_epoch(proof.clone(), &trust)?;
        }
        let mut chain = Chain::new(self.region, &trust)?;
        for event in &self.events {
            match event {
                Event::Block(block) => chain.accept((**block).clone(), &trust, &evidence)?,
                Event::Finalize(id) => {
                    require(
                        evidence.snapshot(*id)?.statement.epoch == chain.epoch,
                        "local finality event uses another era",
                    )?;
                    chain.install(*id, &evidence)?;
                }
                Event::Epoch(id) => {
                    let proof = self
                        .epoch_proofs
                        .iter()
                        .find(|p| p.statement.id().ok() == Some(*id))
                        .ok_or("epoch event lacks durable proof")?;
                    require(
                        proof.statement.region == chain.region
                            && proof.statement.previous_epoch == chain.epoch
                            && chain.finalized == Some(proof.statement.closing_checkpoint)
                            && chain.height() == proof.statement.closing_height,
                        "local epoch event has wrong region, predecessor or closing checkpoint",
                    )?;
                    chain.epoch = *id;
                }
            }
        }
        require(
            self.contact_records.len() <= crate::contact::MAX_CONTACTS,
            "native contact record bound",
        )?;
        for (ident, record) in &self.contact_records {
            require(
                *ident == record.message_id,
                "native contact record index mismatch",
            )?;
            record.verify(&trust, &evidence, chain.region)?;
        }
        Ok((trust, evidence, chain))
    }
}
fn io(error: std::io::Error) -> String {
    error.to_string()
}
pub(crate) fn safe_dir(path: &Path) -> Result<()> {
    require(path.is_absolute(), "store directory must be absolute")?;
    for part in path.ancestors() {
        let meta = fs::symlink_metadata(part).map_err(io)?;
        require(
            meta.is_dir() && !meta.file_type().is_symlink(),
            "symlink or non-directory in store path",
        )?;
    }
    Ok(())
}
pub fn read_bytes(path: &Path, limit: usize) -> Result<Vec<u8>> {
    require(limit <= MAX_BYTES, "input limit outside native bounds")?;
    let meta = fs::symlink_metadata(path).map_err(io)?;
    require(
        meta.is_file() && !meta.file_type().is_symlink() && meta.len() <= limit as u64,
        "unsafe or oversized input file",
    )?;
    let mut bytes = vec![];
    File::open(path)
        .map_err(io)?
        .take(limit as u64 + 1)
        .read_to_end(&mut bytes)
        .map_err(io)?;
    require(bytes.len() <= limit, "input grew beyond bound")?;
    Ok(bytes)
}
pub fn read_json<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    serde_json::from_slice(&read_bytes(path, MAX_BYTES)?).map_err(|e| e.to_string())
}
pub struct Store {
    dir: PathBuf,
    _lock: File,
    pub journal: Journal,
    pub trust: Trust,
    pub evidence: VerifiedEvidence,
    pub chain: Chain,
    pub safety: Safety,
    pub conflicts: Vec<Conflict>,
    authority: String,
    pin: Hash,
    healthy: bool,
}
impl Store {
    pub fn create(
        dir: &Path,
        bootstrap: Bootstrap,
        region: Hash,
        authority: &str,
        pin: Hash,
    ) -> Result<Self> {
        let journal = Journal {
            bootstrap,
            region,
            evidence: Evidence::default(),
            events: vec![],
            incident_ids: BTreeSet::new(),
            epoch_proofs: vec![],
            contact_records: BTreeMap::new(),
        };
        let (trust, evidence, chain) = journal.replay(authority, pin)?;
        safe_dir(dir.parent().ok_or("store parent missing")?)?;
        fs::create_dir(dir).map_err(io)?;
        let lock = OpenOptions::new()
            .read(true)
            .write(true)
            .create_new(true)
            .open(dir.join("LOCK"))
            .map_err(io)?;
        lock.try_lock().map_err(|e| e.to_string())?;
        fs::create_dir(dir.join("incidents")).map_err(io)?;
        let mut guard = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(dir.join("INCIDENT_GUARD"))
            .map_err(io)?;
        guard.write_all(&Hash::ZERO.0).map_err(io)?;
        guard.sync_all().map_err(io)?;
        let store = Self {
            dir: dir.into(),
            _lock: lock,
            journal,
            trust,
            evidence,
            chain,
            authority: authority.into(),
            pin,
            healthy: true,
            safety: Safety::default(),
            conflicts: vec![],
        };
        store.persist(&store.journal)?;
        Ok(store)
    }
    pub fn open(dir: &Path, authority: &str, pin: Hash) -> Result<Self> {
        safe_dir(dir)?;
        let lock_path = dir.join("LOCK");
        let meta = fs::symlink_metadata(&lock_path).map_err(io)?;
        require(
            meta.is_file() && !meta.file_type().is_symlink(),
            "unsafe lock file",
        )?;
        let lock = OpenOptions::new()
            .read(true)
            .write(true)
            .open(lock_path)
            .map_err(io)?;
        lock.try_lock().map_err(|e| e.to_string())?;
        let journal: Journal = read_json(&dir.join("journal.json"))?;
        let (trust, evidence, chain) = journal.replay(authority, pin)?;
        let (conflicts, safety) = read_incidents(dir, &journal, &trust, None)?;
        let mut store = Self {
            dir: dir.into(),
            _lock: lock,
            journal,
            trust,
            evidence,
            chain,
            authority: authority.into(),
            pin,
            healthy: true,
            safety,
            conflicts,
        };
        let pending = read_guard(dir)?;
        if !pending.is_zero() {
            require(store.conflicts.iter().any(|p|p.id().ok()==Some(pending)),"pending authenticated incident is not durably retained; recovery proof is required")?;
            store.commit(store.journal.clone())?;
            write_guard(dir, Hash::ZERO)?;
        }
        Ok(store)
    }
    fn persist(&self, journal: &Journal) -> Result<()> {
        let bytes = serde_json::to_vec(journal).map_err(|e| e.to_string())?;
        require(bytes.len() <= MAX_BYTES, "journal byte bound")?;
        let dest = self.dir.join("journal.json");
        if dest.exists() {
            let meta = fs::symlink_metadata(&dest).map_err(io)?;
            require(
                meta.is_file() && !meta.file_type().is_symlink(),
                "unsafe journal destination",
            )?;
        }
        let temp = self.dir.join("journal.next");
        // A residue after interruption is never trusted, removed or overwritten
        // automatically; the operator can inspect it while the store is closed.
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp)
            .map_err(io)?;
        let result = (|| {
            file.write_all(&bytes).map_err(io)?;
            file.sync_all().map_err(io)?;
            fs::rename(&temp, &dest).map_err(io)?;
            File::open(&self.dir).map_err(io)?.sync_all().map_err(io)
        })();
        if result.is_err() {
            let _ = fs::remove_file(temp);
        }
        result
    }
    pub(crate) fn commit(&mut self, mut journal: Journal) -> Result<()> {
        for proof in &self.conflicts {
            journal.incident_ids.insert(proof.id()?);
        }
        require(
            self.healthy,
            "store requires replay after persistence failure",
        )?;
        let (trust, evidence, chain) = journal.replay(&self.authority, self.pin)?;
        if let Err(error) = self.persist(&journal) {
            self.healthy = false;
            return Err(error);
        }
        self.journal = journal;
        self.trust = trust;
        self.evidence = evidence;
        self.chain = chain;
        Ok(())
    }
    pub fn template(&self, commands: Vec<Command>, miner: String) -> Result<Block> {
        require(
            self.healthy,
            "store requires replay after persistence failure",
        )?;
        self.safety.check(&self.chain, &commands, &self.evidence)?;
        self.chain
            .template(commands, miner, &self.trust, &self.evidence)
    }
    pub(crate) fn validate_partial_owner(&self, signed: SignedIntent) -> Result<()> {
        require(
            self.healthy,
            "store requires replay after persistence failure",
        )?;
        let command = Command::Spend(Box::new(signed.clone()));
        self.safety.check(&self.chain, &[command], &self.evidence)?;
        self.chain
            .validate_partial_owner(signed, &self.trust, &self.evidence)
    }
    pub fn accept(&mut self, block: Block) -> Result<()> {
        self.safety
            .check(&self.chain, &block.commands, &self.evidence)?;
        let mut journal = self.journal.clone();
        journal.events.push(Event::Block(Box::new(block)));
        self.commit(journal)
    }
    pub fn observe_conflict(&mut self, proof: Conflict) -> Result<Hash> {
        require(
            self.healthy,
            "store requires replay after persistence failure",
        )?;
        proof.verify(&self.trust)?;
        let iid = proof.id()?;
        if self.conflicts.iter().any(|p| p.id().ok() == Some(iid)) {
            return Ok(iid);
        }
        if let Err(error) = write_guard(&self.dir, iid) {
            self.healthy = false;
            return Err(error);
        }
        if self.conflicts.len() >= MAX_INCIDENTS {
            self.healthy = false;
            return Err(
                "incident capacity full; pending guard refuses restart without retained proof"
                    .into(),
            );
        }
        let mut conflicts = self.conflicts.clone();
        conflicts.push(proof.clone());
        let safety = Safety::from_conflicts(&conflicts, &self.trust)?;
        // Persist a separately bounded immutable proof before changing the
        // journal. Reopening finds a valid orphan if interrupted between writes.
        let result = publish_incident(&self.dir, &proof, iid, &self.trust);
        self.safety = safety;
        self.conflicts = conflicts;
        if let Err(error) = result {
            self.healthy = false;
            return Err(error);
        }
        self.commit(self.journal.clone())?;
        if let Err(error) = write_guard(&self.dir, Hash::ZERO) {
            self.healthy = false;
            return Err(error);
        }
        Ok(iid)
    }
    pub fn add_evidence(&mut self, evidence: Evidence) -> Result<()> {
        let journal = self.stage_evidence(evidence)?;
        self.commit(journal)
    }
    pub(crate) fn stage_evidence(&mut self, evidence: Evidence) -> Result<Journal> {
        require(
            evidence.snapshots.len() <= MAX_SNAPSHOTS,
            "incoming snapshot bound",
        )?;
        encode("evidence", &evidence)?;
        // Preserve independently authenticated signer failures even though the
        // accompanying value archive is rejected. No branch is installed.
        for (index, snapshot) in evidence.snapshots.iter().enumerate() {
            let incoming = CertifiedHistory::from_snapshot(snapshot);
            incoming.verify(&self.trust)?;
            for old in self
                .journal
                .evidence
                .snapshots
                .iter()
                .chain(evidence.snapshots[..index].iter())
            {
                if old.statement.region == snapshot.statement.region {
                    let proof = Conflict::from_snapshots(old, snapshot)?;
                    if proof.verify(&self.trust).is_ok() {
                        let iid = self.observe_conflict(proof)?;
                        return Err(format!("authenticated conflicting checkpoint retained as {}; archive not installed",iid.to_hex()));
                    }
                }
            }
        }
        let mut journal = self.journal.clone();
        for snapshot in evidence.snapshots {
            let sid = snapshot.statement.id()?;
            if let Some(old) = journal
                .evidence
                .snapshots
                .iter()
                .find(|s| s.statement.id().ok() == Some(sid))
            {
                require(old == &snapshot, "inconsistent duplicate evidence")?;
            } else {
                journal.evidence.snapshots.push(snapshot);
            }
        }
        Ok(journal)
    }
    pub fn snapshot_request(&self) -> Result<Snapshot> {
        self.safety.check_region(self.chain.region)?;
        let mut proof = self.evidence.epoch_proofs(self.chain.region);
        if self.chain.epoch == epoch::Registry::initial(&self.trust, self.chain.region)? {
            proof.clear();
        } else {
            let count = proof
                .iter()
                .position(|p| p.statement.id().ok() == Some(self.chain.epoch))
                .ok_or("local epoch lacks verified authority")?
                + 1;
            proof.truncate(count);
        }
        Ok(Snapshot {
            statement: self.chain.statement(&self.trust)?,
            approvals: vec![],
            blocks: self.chain.blocks.clone(),
            epochs: proof,
        })
    }
    pub fn epoch_request(&self, validators: Vec<String>) -> Result<epoch::Transition> {
        self.safety.check_region(self.chain.region)?;
        let sid = self
            .chain
            .finalized
            .ok_or("handoff needs an installed closing checkpoint")?;
        let closing = epoch::Anchor::from_snapshot(self.evidence.snapshot(sid)?);
        require(
            closing.statement.height == self.chain.height(),
            "handoff must close the exact local tip",
        )?;
        let (previous, number, keys, floor) =
            self.evidence.epoch_state(&self.trust, self.chain.region)?;
        require(
            previous == self.chain.epoch,
            "local epoch must match latest authority",
        )?;
        let proposal = epoch::Transition {
            statement: epoch::EpochStatement {
                currency: self.trust.currency()?,
                region: self.chain.region,
                number: number + 1,
                previous_epoch: previous,
                closing_checkpoint: sid,
                closing_height: self.chain.height(),
                validators,
            },
            closing,
            old_approvals: vec![],
            new_approvals: vec![],
        };
        proposal.validate_request(&self.trust, previous, number, &keys, floor)?;
        Ok(proposal)
    }
    pub fn install_epoch(&mut self, proof: epoch::Transition) -> Result<Hash> {
        self.safety.check_region(self.chain.region)?;
        let existing = self.evidence.epoch_proofs(proof.statement.region);
        for (i, old) in existing.iter().enumerate() {
            if old.statement.previous_epoch == proof.statement.previous_epoch
                && old.statement.id()? != proof.statement.id()?
            {
                let conflict = Conflict::from_handoffs(old, &proof, &existing[..i])?;
                if conflict.verify(&self.trust).is_ok() {
                    let iid = self.observe_conflict(conflict)?;
                    return Err(format!(
                        "authenticated incompatible handoffs retained as {}",
                        iid.to_hex()
                    ));
                }
            }
        }
        let mut authority_path = existing.clone();
        authority_path.push(proof.clone());
        let authority = CertifiedHistory {
            statement: proof.closing.statement.clone(),
            approvals: proof.closing.approvals.clone(),
            headers: proof.closing.headers.clone(),
            epochs: authority_path,
        };
        if authority.verify(&self.trust).is_ok() {
            for old in &self.journal.evidence.snapshots {
                if old.statement.region == proof.statement.region {
                    let conflict = Conflict::canonical(
                        authority.clone(),
                        CertifiedHistory::from_snapshot(old),
                    )?;
                    if conflict.verify(&self.trust).is_ok() {
                        let iid = self.observe_conflict(conflict)?;
                        return Err(format!(
                            "retired-era finality conflicts with handoff retained as {}",
                            iid.to_hex()
                        ));
                    }
                }
            }
        }
        require(
            proof.statement.region == self.chain.region
                && proof.statement.previous_epoch == self.chain.epoch
                && self.chain.finalized == Some(proof.statement.closing_checkpoint)
                && self.chain.height() == proof.statement.closing_height,
            "local handoff identity, current epoch or finality mismatch",
        )?;
        let mut verified = self.evidence.clone();
        let eid = verified.install_epoch(proof.clone(), &self.trust)?;
        let mut journal = self.journal.clone();
        journal.epoch_proofs.push(proof);
        journal.events.push(Event::Epoch(eid));
        self.commit(journal)?;
        Ok(eid)
    }
    pub fn finalize(&mut self, snapshot: Snapshot) -> Result<Hash> {
        CertifiedHistory::from_snapshot(&snapshot).verify(&self.trust)?;
        for old in &self.journal.evidence.snapshots {
            if old.statement.region == snapshot.statement.region {
                let proof = Conflict::from_snapshots(old, &snapshot)?;
                if proof.verify(&self.trust).is_ok() {
                    let iid = self.observe_conflict(proof)?;
                    return Err(format!(
                        "conflicting finalization retained as {}; neither branch adopted",
                        iid.to_hex()
                    ));
                }
            }
        }
        self.safety.check_region(self.chain.region)?;
        require(
            snapshot.statement == self.chain.statement(&self.trust)?
                && snapshot.blocks == self.chain.blocks,
            "local checkpoint does not match actual chain",
        )?;
        let sid = snapshot.statement.id()?;
        let mut journal = self.journal.clone();
        journal.evidence.snapshots.push(snapshot);
        journal.events.push(Event::Finalize(sid));
        self.commit(journal)?;
        Ok(sid)
    }
}

fn read_incidents(
    dir: &Path,
    journal: &Journal,
    trust: &Trust,
    ignore: Option<Hash>,
) -> Result<(Vec<Conflict>, Safety)> {
    let path = dir.join("incidents");
    safe_dir(&path)?;
    let mut conflicts = vec![];
    let mut ids = BTreeSet::new();
    for entry in fs::read_dir(&path).map_err(io)? {
        require(
            conflicts.len() < MAX_INCIDENTS,
            "incident directory exceeds bound",
        )?;
        let entry = entry.map_err(io)?;
        if ignore
            .is_some_and(|id| entry.file_name().to_str() == Some(&format!("{}.json", id.to_hex())))
        {
            continue;
        }
        let proof: Conflict = read_json(&entry.path())?;
        proof.verify(trust)?;
        let iid = proof.id()?;
        require(
            entry.file_name().to_str() == Some(&format!("{}.json", iid.to_hex()))
                && ids.insert(iid),
            "incident filename mismatch or duplicate",
        )?;
        conflicts.push(proof);
    }
    require(
        journal.incident_ids.is_subset(&ids),
        "indexed incident is missing; refuse recovery",
    )?;
    let safety = Safety::from_conflicts(&conflicts, trust)?;
    Ok((conflicts, safety))
}
fn publish_incident(dir: &Path, proof: &Conflict, iid: Hash, trust: &Trust) -> Result<()> {
    let path = dir.join("incidents");
    safe_dir(&path)?;
    let final_path = path.join(format!("{}.json", iid.to_hex()));
    if final_path.exists() {
        let saved: Conflict = read_json(&final_path)?;
        require(saved.id()? == iid, "immutable incident mismatch")?;
        saved.verify(trust)?;
        return Ok(());
    }
    let bytes = serde_json::to_vec(proof).map_err(|e| e.to_string())?;
    require(bytes.len() <= MAX_BYTES, "incident byte bound")?;
    // A partial write is intentionally left behind. It fails closed on replay,
    // rather than permitting known signer faults to disappear after a crash.
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(final_path)
        .map_err(io)?;
    file.write_all(&bytes).map_err(io)?;
    file.sync_all().map_err(io)?;
    File::open(path).map_err(io)?.sync_all().map_err(io)
}

fn read_guard(dir: &Path) -> Result<Hash> {
    let path = dir.join("INCIDENT_GUARD");
    let meta = fs::symlink_metadata(&path).map_err(io)?;
    require(
        meta.is_file() && !meta.file_type().is_symlink() && meta.len() == 32,
        "invalid incident guard",
    )?;
    let bytes = fs::read(path).map_err(io)?;
    let value: [u8; 32] = bytes
        .try_into()
        .map_err(|_| "invalid incident guard bytes")?;
    Ok(Hash(value))
}
fn write_guard(dir: &Path, iid: Hash) -> Result<()> {
    read_guard(dir)?;
    let mut file = OpenOptions::new()
        .write(true)
        .open(dir.join("INCIDENT_GUARD"))
        .map_err(io)?;
    file.write_all(&iid.0).map_err(io)?;
    file.sync_all().map_err(io)
}
/// Retry the exact authenticated proof named by a failed/pending guard. This
/// never clears safety state or removes an incident, and takes the same lock.
pub fn recover_incident(dir: &Path, authority: &str, pin: Hash, proof: Conflict) -> Result<()> {
    safe_dir(dir)?;
    let lock_path = dir.join("LOCK");
    let metadata = fs::symlink_metadata(&lock_path).map_err(io)?;
    require(
        metadata.is_file() && !metadata.file_type().is_symlink(),
        "unsafe recovery lock",
    )?;
    let lock = OpenOptions::new()
        .read(true)
        .write(true)
        .open(lock_path)
        .map_err(io)?;
    lock.try_lock().map_err(|e| e.to_string())?;
    let journal: Journal = read_json(&dir.join("journal.json"))?;
    let (trust, _, _) = journal.replay(authority, pin)?;
    proof.verify(&trust)?;
    let iid = proof.id()?;
    let pending = read_guard(dir)?;
    require(
        pending == iid || (pending.is_zero() && journal.incident_ids.contains(&iid)),
        "recovery proof differs from pending or indexed incident",
    )?;
    let mut remaining = journal.clone();
    remaining.incident_ids.remove(&iid);
    let (retained, _) = read_incidents(dir, &remaining, &trust, Some(iid))?;
    require(
        retained.len() < MAX_INCIDENTS || retained.iter().any(|p| p.id().ok() == Some(iid)),
        "recovery incident capacity full; existing records remain retained",
    )?;
    write_guard(dir, iid)?;
    let target = dir.join("incidents").join(format!("{}.json", iid.to_hex()));
    if target.exists() && read_json::<Conflict>(&target).ok().as_ref() != Some(&proof) {
        let meta = fs::symlink_metadata(&target).map_err(io)?;
        require(
            meta.is_file() && !meta.file_type().is_symlink() && meta.len() <= MAX_BYTES as u64,
            "unsafe damaged incident",
        )?;
        let residue = dir.join(format!("damaged-incident-{}.bin", iid.to_hex()));
        require(
            !residue.exists(),
            "damaged incident residue already exists; retain it for review",
        )?;
        fs::rename(&target, &residue).map_err(io)?;
        File::open(dir).map_err(io)?.sync_all().map_err(io)?;
    }
    publish_incident(dir, &proof, iid, &trust)
}
