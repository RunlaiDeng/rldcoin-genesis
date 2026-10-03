//! Bounded full-replay journal; exclusive OS lock and fsync/rename replacement.
//! An external monotonic checkpoint is still required against old-backup rollback.
use super::*;
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
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Journal {
    pub bootstrap: Bootstrap,
    pub region: Hash,
    pub evidence: Evidence,
    pub events: Vec<Event>,
}
impl Journal {
    pub fn replay(&self, authority: &str, pin: Hash) -> Result<(Trust, VerifiedEvidence, Chain)> {
        require(
            self.events.len() <= MAX_BLOCKS + MAX_SNAPSHOTS,
            "journal event bound",
        )?;
        encode("journal", self)?;
        let trust = Trust::verify(&self.bootstrap, authority, pin)?;
        let evidence = VerifiedEvidence::verify(&self.evidence, &trust)?;
        let mut chain = Chain::new(self.region, &trust)?;
        for event in &self.events {
            match event {
                Event::Block(block) => chain.accept((**block).clone(), &trust, &evidence)?,
                Event::Finalize(id) => chain.install(*id, &evidence)?,
            }
        }
        Ok((trust, evidence, chain))
    }
}
fn io(error: std::io::Error) -> String {
    error.to_string()
}
fn safe_dir(path: &Path) -> Result<()> {
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
pub fn read_json<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    let meta = fs::symlink_metadata(path).map_err(io)?;
    require(
        meta.is_file() && !meta.file_type().is_symlink() && meta.len() <= MAX_BYTES as u64,
        "unsafe or oversized input file",
    )?;
    let mut bytes = vec![];
    File::open(path)
        .map_err(io)?
        .take(MAX_BYTES as u64 + 1)
        .read_to_end(&mut bytes)
        .map_err(io)?;
    require(bytes.len() <= MAX_BYTES, "input grew beyond bound")?;
    serde_json::from_slice(&bytes).map_err(|e| e.to_string())
}
pub struct Store {
    dir: PathBuf,
    _lock: File,
    pub journal: Journal,
    pub trust: Trust,
    pub evidence: VerifiedEvidence,
    pub chain: Chain,
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
        Ok(Self {
            dir: dir.into(),
            _lock: lock,
            journal,
            trust,
            evidence,
            chain,
            authority: authority.into(),
            pin,
            healthy: true,
        })
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
    fn commit(&mut self, journal: Journal) -> Result<()> {
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
    pub fn accept(&mut self, block: Block) -> Result<()> {
        let mut journal = self.journal.clone();
        journal.events.push(Event::Block(Box::new(block)));
        self.commit(journal)
    }
    pub fn add_evidence(&mut self, evidence: Evidence) -> Result<()> {
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
        self.commit(journal)
    }
    pub fn finalize(&mut self, snapshot: Snapshot) -> Result<Hash> {
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
