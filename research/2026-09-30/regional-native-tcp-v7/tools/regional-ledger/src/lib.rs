//! Bounded, incompatible, fixture-only generic regional ledger candidate.
//! No existing genesis, live assets, BFT protocol or production mode.
use rld_core::{validate_ed25519_public_key, verify_bytes, AdmissionHash32 as Hash, Amount};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

pub type Result<T> = std::result::Result<T, String>;
pub const MAX_BLOCKS: usize = 256;
pub const MAX_SNAPSHOTS: usize = 64;
pub const MAX_BYTES: usize = 8 * 1024 * 1024;
pub const MAX_COMMANDS: usize = 16;
pub const MAX_COINS: usize = 4096;
const DOMAIN: &str = "RLD-REGIONAL-FIXTURE-V1";
fn require(ok: bool, msg: &str) -> Result<()> {
    if ok {
        Ok(())
    } else {
        Err(msg.into())
    }
}
fn encode<T: Serialize>(domain: &str, value: &T) -> Result<Vec<u8>> {
    let mut bytes = format!("{DOMAIN}:{domain}\0").into_bytes();
    bytes.extend(serde_json::to_vec(value).map_err(|e| e.to_string())?);
    require(bytes.len() <= MAX_BYTES, "encoded evidence exceeds bound")?;
    Ok(bytes)
}
pub fn id<T: Serialize>(domain: &str, value: &T) -> Result<Hash> {
    Ok(Hash(Sha256::digest(encode(domain, value)?).into()))
}
fn add(a: Amount, b: Amount) -> Result<Amount> {
    a.checked_add(b).map_err(|e| e.to_string())
}
fn sum(mut values: impl Iterator<Item = Amount>) -> Result<Amount> {
    values.try_fold(Amount::ZERO, add)
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Currency {
    pub format: String,
    pub fixture_only: bool,
    pub implementation: Hash,
    pub origin: String,
    pub authority: String,
    pub cap: Amount,
    pub block_reward: Amount,
    pub maturity: u64,
    pub signature: String,
}
impl Currency {
    pub fn bytes(&self) -> Result<Vec<u8>> {
        encode(
            "currency",
            &(
                &self.format,
                self.fixture_only,
                self.implementation,
                &self.origin,
                &self.authority,
                self.cap,
                self.block_reward,
                self.maturity,
            ),
        )
    }
    pub fn id(&self) -> Result<Hash> {
        Ok(Hash(Sha256::digest(self.bytes()?).into()))
    }
    pub fn verify(&self, trusted_authority: &str, pin: Hash) -> Result<()> {
        require(
            self.format == DOMAIN
                && self.fixture_only
                && self.implementation == implementation()?
                && self.authority == trusted_authority
                && self.id()? == pin
                && !pin.is_zero(),
            "untrusted currency or non-fixture profile",
        )?;
        validate_ed25519_public_key(&self.authority)?;
        name(&self.origin)?;
        require(
            self.cap.0 > 0
                && self.cap <= Amount::TOTAL_SUPPLY
                && self.block_reward.0 > 0
                && self.block_reward <= self.cap
                && (1..=100).contains(&self.maturity),
            "invalid issuance or maturity",
        )?;
        verify_bytes(&self.authority, &self.bytes()?, &self.signature)
    }
}
pub fn implementation() -> Result<Hash> {
    id(
        "implementation",
        &(
            env!("RLD_REGIONAL_SOURCE"),
            rld_core::implementation_source::IMPLEMENTATION_SOURCE_COMMITMENT,
        ),
    )
}
fn name(value: &str) -> Result<()> {
    require(
        !value.is_empty()
            && value.len() <= 32
            && value
                .bytes()
                .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == b'-'),
        "invalid regional label",
    )
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Admission {
    pub currency: Hash,
    pub region: String,
    pub rules: String,
    pub validators: Vec<String>,
    pub signature: String,
}
impl Admission {
    pub fn bytes(&self) -> Result<Vec<u8>> {
        encode(
            "admission",
            &(self.currency, &self.region, &self.rules, &self.validators),
        )
    }
    pub fn id(&self) -> Result<Hash> {
        Ok(Hash(Sha256::digest(self.bytes()?).into()))
    }
    pub fn verify(&self, currency: &Currency) -> Result<()> {
        name(&self.region)?;
        require(
            self.currency == currency.id()?
                && self.rules == DOMAIN
                && self.validators.len() == 4
                && self.validators.windows(2).all(|v| v[0] < v[1]),
            "wrong admission identity, rules or validator set",
        )?;
        for key in &self.validators {
            validate_ed25519_public_key(key)?;
        }
        verify_bytes(&currency.authority, &self.bytes()?, &self.signature)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Bootstrap {
    pub currency: Currency,
    pub admissions: Vec<Admission>,
}
#[derive(Clone)]
pub struct Trust {
    currency: Currency,
    regions: BTreeMap<Hash, Admission>,
}
impl Trust {
    pub fn verify(package: &Bootstrap, authority: &str, pin: Hash) -> Result<Self> {
        package.currency.verify(authority, pin)?;
        require(
            !package.admissions.is_empty() && package.admissions.len() <= 16,
            "admission bound",
        )?;
        let mut regions = BTreeMap::new();
        let mut labels = BTreeSet::new();
        for a in &package.admissions {
            a.verify(&package.currency)?;
            require(labels.insert(a.region.clone()), "duplicate regional label")?;
            regions.insert(a.id()?, a.clone());
        }
        require(
            labels.contains(&package.currency.origin),
            "origin admission missing",
        )?;
        Ok(Self {
            currency: package.currency.clone(),
            regions,
        })
    }
    pub fn region(&self, id: Hash) -> Result<&Admission> {
        self.regions
            .get(&id)
            .ok_or("unknown regional genesis".into())
    }
    pub fn named(&self, label: &str) -> Result<Hash> {
        self.regions
            .iter()
            .find(|(_, a)| a.region == label)
            .map(|(id, _)| *id)
            .ok_or("unknown region".into())
    }
    pub fn currency(&self) -> Result<Hash> {
        self.currency.id()
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Payment {
    pub owner: String,
    pub amount: Amount,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Intent {
    pub currency: Hash,
    pub region: Hash,
    pub inputs: Vec<Hash>,
    pub outputs: Vec<Payment>,
    pub fee: Amount,
    pub destination: Option<Hash>,
    pub remote: Option<Payment>,
    pub destination_fee: Amount,
    pub valid_through: u64,
}
impl Intent {
    pub fn bytes(&self) -> Result<Vec<u8>> {
        encode("owner-intent", self)
    }
    pub fn id(&self) -> Result<Hash> {
        id("owner-intent", self)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Approval {
    pub key: String,
    pub signature: String,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SignedIntent {
    pub intent: Intent,
    pub approvals: Vec<Approval>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub enum Command {
    Spend(Box<SignedIntent>),
    Import { snapshot: Hash, export: Hash },
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Coin {
    pub payment: Payment,
    pub created: u64,
    pub mature: u64,
    pub dependencies: BTreeSet<Hash>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Export {
    pub id: Hash,
    pub source: Hash,
    pub destination: Hash,
    pub recipient: Payment,
    pub destination_fee: Amount,
    pub height: u64,
    pub dependencies: BTreeSet<Hash>,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Ledger {
    pub coins: BTreeMap<Hash, Coin>,
    pub exports: BTreeMap<Hash, Export>,
    pub imports: BTreeMap<Hash, Hash>,
    pub minted: Amount,
    pub received: Amount,
}
impl Ledger {
    pub fn root(&self) -> Result<Hash> {
        self.audit()?;
        id("state", self)
    }
    pub fn audit(&self) -> Result<()> {
        require(
            self.coins.len() <= MAX_COINS
                && self.exports.len() <= MAX_COINS
                && self.imports.len() <= MAX_COINS,
            "permanent ledger index full",
        )?;
        let liquid = sum(self.coins.values().map(|c| c.payment.amount))?;
        let outbound = sum(self.exports.values().map(|e| e.recipient.amount))?;
        require(
            add(self.minted, self.received)? == add(liquid, outbound)?,
            "regional conservation failure",
        )
    }
    fn output(
        &mut self,
        tx: Hash,
        index: u32,
        payment: Payment,
        height: u64,
        mature: u64,
        deps: &BTreeSet<Hash>,
    ) -> Result<()> {
        validate_ed25519_public_key(&payment.owner)?;
        require(payment.amount.0 > 0, "zero output")?;
        let key = id("output", &(tx, index))?;
        require(!self.coins.contains_key(&key), "output collision")?;
        self.coins.insert(
            key,
            Coin {
                payment,
                created: height,
                mature,
                dependencies: deps.clone(),
            },
        );
        Ok(())
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Header {
    pub currency: Hash,
    pub region: Hash,
    pub parent: Hash,
    pub anchor: Option<Hash>,
    pub height: u64,
    pub miner: String,
    pub commands: Hash,
    pub state: Hash,
    pub nonce: u64,
}
impl Header {
    pub fn id(&self) -> Result<Hash> {
        id("block", self)
    }
    pub fn work_valid(&self) -> Result<bool> {
        Ok(self.id()?.0[0] == 0)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Block {
    pub header: Header,
    pub commands: Vec<Command>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Statement {
    pub currency: Hash,
    pub region: Hash,
    pub height: u64,
    pub block: Hash,
    pub state: Hash,
    pub previous: Option<Hash>,
    pub epoch: Hash,
}
impl Statement {
    pub fn bytes(&self) -> Result<Vec<u8>> {
        encode("unanimous-checkpoint", self)
    }
    pub fn id(&self) -> Result<Hash> {
        id("unanimous-checkpoint", self)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Snapshot {
    pub statement: Statement,
    pub approvals: Vec<Approval>,
    pub blocks: Vec<Block>,
    pub epochs: Vec<epoch::Transition>,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Evidence {
    pub snapshots: Vec<Snapshot>,
}
#[derive(Clone, Default)]
pub struct VerifiedEvidence {
    snapshots: BTreeMap<Hash, (Snapshot, Ledger)>,
    pub(crate) epochs: epoch::Registry,
}
impl VerifiedEvidence {
    pub fn verify(evidence: &Evidence, trust: &Trust) -> Result<Self> {
        require(evidence.snapshots.len() <= MAX_SNAPSHOTS, "snapshot bound")?;
        encode("evidence", evidence)?;
        let mut result = Self::default();
        for snapshot in &evidence.snapshots {
            result.add(snapshot.clone(), trust)?;
        }
        Ok(result)
    }
    pub fn add(&mut self, snapshot: Snapshot, trust: &Trust) -> Result<Hash> {
        let statement = &snapshot.statement;
        let sid = statement.id()?;
        if let Some((old, _)) = self.snapshots.get(&sid) {
            require(old == &snapshot, "inconsistent duplicate snapshot")?;
            return Ok(sid);
        }
        require(
            self.snapshots.len() < MAX_SNAPSHOTS && snapshot.blocks.len() <= MAX_BLOCKS,
            "snapshot or block bound",
        )?;
        let mut prepared = self.clone();
        require(
            snapshot.epochs.len() <= epoch::MAX_EPOCHS,
            "snapshot epoch bound",
        )?;
        for proof in &snapshot.epochs {
            require(
                proof.statement.region == statement.region,
                "snapshot carries wrong-region epoch",
            )?;
            prepared
                .epochs
                .install(proof.clone(), trust, &self.snapshots)?;
        }
        let keys = prepared.epochs.checkpoint_keys(trust, statement)?;
        let all = prepared.epochs.proofs(statement.region);
        let count = if statement.epoch == epoch::Registry::initial(trust, statement.region)? {
            0
        } else {
            all.iter()
                .position(|p| p.statement.id().ok() == Some(statement.epoch))
                .ok_or("unknown checkpoint epoch context")?
                + 1
        };
        require(
            snapshot
                .epochs
                .iter()
                .map(|p| p.statement.id())
                .collect::<Result<Vec<_>>>()?
                == all[..count]
                    .iter()
                    .map(|p| p.statement.id())
                    .collect::<Result<Vec<_>>>()?,
            "snapshot omits or overstates its epoch authority chain",
        )?;
        epoch::approvals(&snapshot.approvals, &keys, &statement.bytes()?)?;
        require(
            statement.currency == trust.currency()? && statement.height > 0,
            "invalid checkpoint identity",
        )?;
        // One compatible, monotonic certificate chain per region. No conflict
        // resolution or BFT view changes are manufactured by this prototype.
        let latest = self
            .snapshots
            .iter()
            .filter(|(_, (s, _))| s.statement.region == statement.region)
            .max_by_key(|(_, (s, _))| s.statement.height);
        require(
            statement.previous == latest.map(|(id, _)| *id),
            "checkpoint is stale, conflicting or missing predecessor",
        )?;
        if let Some((_, (old, _))) = latest {
            require(
                statement.height > old.statement.height && snapshot.blocks.starts_with(&old.blocks),
                "checkpoint fork or rollback",
            )?;
        }
        let mut chain = Chain::new(statement.region, trust)?;
        for block in &snapshot.blocks {
            chain.accept(block.clone(), trust, self)?;
        }
        chain.epoch = statement.epoch;
        require(
            chain.statement(trust)? == *statement,
            "checkpoint differs from replayed history",
        )?;
        self.epochs = prepared.epochs;
        self.snapshots.insert(sid, (snapshot, chain.ledger));
        Ok(sid)
    }
    pub fn epoch_proofs(&self, region: Hash) -> Vec<epoch::Transition> {
        self.epochs.proofs(region)
    }
    pub fn epoch_state(
        &self,
        trust: &Trust,
        region: Hash,
    ) -> Result<(Hash, u64, Vec<String>, u64)> {
        self.epochs.latest(trust, region)
    }
    pub fn install_epoch(&mut self, proof: epoch::Transition, trust: &Trust) -> Result<Hash> {
        self.epochs.install(proof, trust, &self.snapshots)
    }
    pub fn snapshot(&self, sid: Hash) -> Result<&Snapshot> {
        self.snapshots
            .get(&sid)
            .map(|(s, _)| s)
            .ok_or("missing verified source checkpoint".into())
    }
    pub fn export(&self, sid: Hash, eid: Hash) -> Result<&Export> {
        self.snapshots
            .get(&sid)
            .ok_or("missing dependency checkpoint")?
            .1
            .exports
            .get(&eid)
            .ok_or("export absent from finalized source".into())
    }
}
#[derive(Clone)]
pub struct Chain {
    pub region: Hash,
    pub blocks: Vec<Block>,
    pub ledger: Ledger,
    pub finalized: Option<Hash>,
    pub epoch: Hash,
}
impl Chain {
    pub fn new(region: Hash, trust: &Trust) -> Result<Self> {
        trust.region(region)?;
        Ok(Self {
            region,
            blocks: vec![],
            ledger: Ledger::default(),
            finalized: None,
            epoch: epoch::Registry::initial(trust, region)?,
        })
    }
    pub fn height(&self) -> u64 {
        self.blocks.len() as u64
    }
    pub fn tip(&self) -> Result<Hash> {
        self.blocks
            .last()
            .map(|b| b.header.id())
            .unwrap_or(Ok(self.region))
    }
    pub fn install(&mut self, sid: Hash, evidence: &VerifiedEvidence) -> Result<()> {
        let snapshot = evidence.snapshot(sid)?;
        require(
            snapshot.statement.region == self.region && self.blocks.starts_with(&snapshot.blocks),
            "checkpoint does not cover this local history",
        )?;
        require(
            snapshot.statement.previous == self.finalized,
            "local checkpoint predecessor mismatch",
        )?;
        self.finalized = Some(sid);
        Ok(())
    }
    pub fn statement(&self, trust: &Trust) -> Result<Statement> {
        Ok(Statement {
            currency: trust.currency()?,
            region: self.region,
            height: self.height(),
            block: self.tip()?,
            state: self.ledger.root()?,
            previous: self.finalized,
            epoch: self.epoch,
        })
    }
    fn execute(
        &self,
        commands: &[Command],
        miner: &str,
        trust: &Trust,
        evidence: &VerifiedEvidence,
    ) -> Result<Ledger> {
        require(commands.len() <= MAX_COMMANDS, "command bound")?;
        validate_ed25519_public_key(miner)?;
        let height = self.height().checked_add(1).ok_or("height overflow")?;
        let maturity = height
            .checked_add(trust.currency.maturity)
            .ok_or("maturity overflow")?;
        let mut ledger = self.ledger.clone();
        for command in commands {
            match command {
                Command::Spend(signed) => {
                    let intent = &signed.intent;
                    require(
                        intent.currency == trust.currency()?
                            && intent.region == self.region
                            && intent.valid_through >= height
                            && !intent.inputs.is_empty()
                            && intent.inputs.len() <= 16
                            && intent.inputs.windows(2).all(|v| v[0] < v[1])
                            && intent.outputs.len() <= 16,
                        "invalid spend identity, expiry or inputs",
                    )?;
                    let mut owners = BTreeSet::new();
                    let mut deps = BTreeSet::new();
                    let mut total = Amount::ZERO;
                    for input in &intent.inputs {
                        let coin = ledger.coins.get(input).ok_or("input absent or spent")?;
                        require(height >= coin.mature, "immature input")?;
                        owners.insert(coin.payment.owner.clone());
                        deps.extend(&coin.dependencies);
                        total = add(total, coin.payment.amount)?;
                    }
                    require(
                        signed.approvals.len() == owners.len(),
                        "every input owner must authorize",
                    )?;
                    for (approval, owner) in signed.approvals.iter().zip(&owners) {
                        require(&approval.key == owner, "wrong input owner")?;
                        verify_bytes(owner, &intent.bytes()?, &approval.signature)?;
                    }
                    let mut used = add(sum(intent.outputs.iter().map(|p| p.amount))?, intent.fee)?;
                    let tx = intent.id()?;
                    match (&intent.destination, &intent.remote) {
                        (Some(destination), Some(remote)) => {
                            trust.region(*destination)?;
                            validate_ed25519_public_key(&remote.owner)?;
                            require(
                                *destination != self.region
                                    && remote.amount.0 > 0
                                    && intent.destination_fee < remote.amount,
                                "invalid export destination or fee",
                            )?;
                            let final_height = evidence
                                .snapshot(
                                    self.finalized
                                        .ok_or("onward export requires local finality")?,
                                )?
                                .statement
                                .height;
                            require(
                                intent
                                    .inputs
                                    .iter()
                                    .all(|i| ledger.coins[i].created <= final_height),
                                "export input is not locally finalized",
                            )?;
                            used = add(used, remote.amount)?;
                            require(!ledger.exports.contains_key(&tx), "duplicate export")?;
                            ledger.exports.insert(
                                tx,
                                Export {
                                    id: tx,
                                    source: self.region,
                                    destination: *destination,
                                    recipient: remote.clone(),
                                    destination_fee: intent.destination_fee,
                                    height,
                                    dependencies: deps.clone(),
                                },
                            );
                        }
                        (None, None) => require(
                            intent.destination_fee.is_zero(),
                            "local spend has remote fee",
                        )?,
                        _ => return Err("incomplete export intent".into()),
                    }
                    require(
                        used == total,
                        "inputs, change, fees and export do not conserve",
                    )?;
                    for input in &intent.inputs {
                        ledger.coins.remove(input);
                    }
                    for (i, payment) in intent.outputs.iter().enumerate() {
                        ledger.output(tx, i as u32, payment.clone(), height, height, &deps)?;
                    }
                    if !intent.fee.is_zero() {
                        ledger.output(
                            tx,
                            16,
                            Payment {
                                owner: miner.into(),
                                amount: intent.fee,
                            },
                            height,
                            maturity,
                            &deps,
                        )?;
                    }
                }
                Command::Import { snapshot, export } => {
                    let source = evidence.snapshot(*snapshot)?;
                    let record = evidence.export(*snapshot, *export)?;
                    require(
                        source.statement.currency == trust.currency()?
                            && source.statement.region == record.source
                            && record.destination == self.region
                            && record.source != self.region
                            && record.height <= source.statement.height,
                        "wrong source, destination or checkpoint",
                    )?;
                    require(
                        !ledger.imports.contains_key(export),
                        "permanent import tombstone rejects replay",
                    )?;
                    let mut deps = record.dependencies.clone();
                    deps.insert(*snapshot);
                    for dependency in &deps {
                        evidence.snapshot(*dependency)?;
                    }
                    let amount = record
                        .recipient
                        .amount
                        .checked_sub(record.destination_fee)
                        .map_err(|e| e.to_string())?;
                    ledger.output(
                        *export,
                        0,
                        Payment {
                            owner: record.recipient.owner.clone(),
                            amount,
                        },
                        height,
                        maturity,
                        &deps,
                    )?;
                    if !record.destination_fee.is_zero() {
                        ledger.output(
                            *export,
                            16,
                            Payment {
                                owner: miner.into(),
                                amount: record.destination_fee,
                            },
                            height,
                            maturity,
                            &deps,
                        )?;
                    }
                    ledger.received = add(ledger.received, record.recipient.amount)?;
                    ledger.imports.insert(*export, *snapshot);
                }
            }
        }
        if trust.region(self.region)?.region == trust.currency.origin {
            let remaining = trust
                .currency
                .cap
                .checked_sub(ledger.minted)
                .map_err(|e| e.to_string())?;
            let reward = remaining.min(trust.currency.block_reward);
            if !reward.is_zero() {
                let tx = id("issuance", &(self.region, height, self.tip()?))?;
                ledger.output(
                    tx,
                    0,
                    Payment {
                        owner: miner.into(),
                        amount: reward,
                    },
                    height,
                    maturity,
                    &BTreeSet::new(),
                )?;
                ledger.minted = add(ledger.minted, reward)?;
            }
        }
        ledger.audit()?;
        Ok(ledger)
    }
    pub fn template(
        &self,
        commands: Vec<Command>,
        miner: String,
        trust: &Trust,
        evidence: &VerifiedEvidence,
    ) -> Result<Block> {
        require(self.blocks.len() < MAX_BLOCKS, "history bound")?;
        let ledger = self.execute(&commands, &miner, trust, evidence)?;
        Ok(Block {
            header: Header {
                currency: trust.currency()?,
                region: self.region,
                parent: self.tip()?,
                anchor: self.finalized,
                height: self.height() + 1,
                miner,
                commands: id("commands", &commands)?,
                state: ledger.root()?,
                nonce: 0,
            },
            commands,
        })
    }
    pub fn accept(
        &mut self,
        block: Block,
        trust: &Trust,
        evidence: &VerifiedEvidence,
    ) -> Result<()> {
        require(self.blocks.len() < MAX_BLOCKS, "history bound")?;
        encode("block", &block)?;
        let mut next = self.clone();
        if block.header.anchor != next.finalized {
            next.install(block.header.anchor.ok_or("checkpoint rollback")?, evidence)?;
        }
        require(
            block.header.currency == trust.currency()?
                && block.header.region == self.region
                && block.header.parent == self.tip()?
                && block.header.height == self.height() + 1
                && block.header.commands == id("commands", &block.commands)?
                && block.header.work_valid()?,
            "invalid block identity, order, commitment or work",
        )?;
        next.ledger = next.execute(&block.commands, &block.header.miner, trust, evidence)?;
        require(
            next.ledger.root()? == block.header.state,
            "replayed state root mismatch",
        )?;
        next.blocks.push(block);
        *self = next;
        Ok(())
    }
}
pub fn mine(block: &mut Block) -> Result<()> {
    while !block.header.work_valid()? {
        block.header.nonce = block.header.nonce.checked_add(1).ok_or("nonce exhausted")?;
    }
    Ok(())
}

/// Evidence-set accounting, not a global live balance oracle. Input chains must
/// be compatible replayed histories; historical exports are counted only once.
pub fn conservation(chains: &[Chain]) -> Result<(Amount, Amount, Amount)> {
    let mut regions = BTreeSet::new();
    let mut issued = Amount::ZERO;
    let mut liquid = Amount::ZERO;
    let mut exports = BTreeMap::new();
    let mut imports = BTreeSet::new();
    for chain in chains {
        require(
            regions.insert(chain.region),
            "duplicate region in accounting",
        )?;
        chain.ledger.audit()?;
        issued = add(issued, chain.ledger.minted)?;
        liquid = add(
            liquid,
            sum(chain.ledger.coins.values().map(|c| c.payment.amount))?,
        )?;
        for (id, export) in &chain.ledger.exports {
            require(
                exports.insert(*id, export).is_none(),
                "duplicate export identity",
            )?;
        }
        for id in chain.ledger.imports.keys() {
            require(imports.insert(*id), "export imported more than once")?;
        }
    }
    for imported in &imports {
        require(
            exports.contains_key(imported),
            "incomplete compatible evidence set",
        )?;
    }
    let pending = sum(exports
        .iter()
        .filter(|(id, _)| !imports.contains(id))
        .map(|(_, e)| e.recipient.amount))?;
    require(
        issued == add(liquid, pending)?,
        "global evidence-set conservation failure",
    )?;
    Ok((issued, liquid, pending))
}
pub mod conflict;
pub mod contact;
pub mod epoch;
pub mod signer;
pub mod storage;
#[cfg(test)]
mod tests;
pub mod wallet;
pub mod wallet_agent;
