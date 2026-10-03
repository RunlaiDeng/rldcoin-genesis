//! Authenticated incompatible checkpoint histories, not a consensus repair.
//! Histories authenticate ancestry only; a signed invalid ledger is still a
//! signer safety failure. Neither branch is installed by an incident proof.
use super::*;
pub const MAX_INCIDENTS: usize = 16;
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CertifiedHistory {
    pub statement: Statement,
    pub approvals: Vec<Approval>,
    pub headers: Vec<Header>,
}
impl CertifiedHistory {
    pub fn from_snapshot(snapshot: &Snapshot) -> Self {
        Self {
            statement: snapshot.statement.clone(),
            approvals: snapshot.approvals.clone(),
            headers: snapshot.blocks.iter().map(|b| b.header.clone()).collect(),
        }
    }
    pub fn verify(&self, trust: &Trust) -> Result<()> {
        let statement = &self.statement;
        let admission = trust.region(statement.region)?;
        require(
            statement.currency == trust.currency()?
                && statement.height > 0
                && self.headers.len() <= MAX_BLOCKS
                && self.headers.len() as u64 == statement.height
                && self.approvals.len() == admission.validators.len(),
            "invalid incident certificate identity or bounds",
        )?;
        for (approval, key) in self.approvals.iter().zip(&admission.validators) {
            require(&approval.key == key, "wrong incident signer")?;
            verify_bytes(key, &statement.bytes()?, &approval.signature)?;
        }
        let mut parent = statement.region;
        for (index, header) in self.headers.iter().enumerate() {
            require(
                header.currency == statement.currency
                    && header.region == statement.region
                    && header.height == index as u64 + 1
                    && header.parent == parent
                    && header.work_valid()?,
                "incident ancestry is not bound to signed checkpoint",
            )?;
            validate_ed25519_public_key(&header.miner)?;
            parent = header.id()?;
        }
        require(
            parent == statement.block
                && self
                    .headers
                    .last()
                    .is_some_and(|h| h.state == statement.state),
            "incident terminal header differs from signature",
        )
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Conflict {
    pub left: CertifiedHistory,
    pub right: CertifiedHistory,
}
impl Conflict {
    pub fn from_snapshots(left: &Snapshot, right: &Snapshot) -> Result<Self> {
        let (left, right) = if left.statement.id()? < right.statement.id()? {
            (left, right)
        } else {
            (right, left)
        };
        Ok(Self {
            left: CertifiedHistory::from_snapshot(left),
            right: CertifiedHistory::from_snapshot(right),
        })
    }
    pub fn id(&self) -> Result<Hash> {
        id(
            "authenticated-checkpoint-conflict",
            &(self.left.statement.id()?, self.right.statement.id()?),
        )
    }
    pub fn region(&self) -> Hash {
        self.left.statement.region
    }
    pub fn verify(&self, trust: &Trust) -> Result<()> {
        encode("incident", self)?;
        self.left.verify(trust)?;
        self.right.verify(trust)?;
        require(
            self.left.statement.region == self.right.statement.region
                && self.left.statement.id()? < self.right.statement.id()?,
            "incident regions differ or pair is not canonical",
        )?;
        let common = self.left.headers.len().min(self.right.headers.len());
        require(
            (0..common).any(|i| self.left.headers[i].id().ok() != self.right.headers[i].id().ok()),
            "compatible certificates are not conflict evidence",
        )
    }
}
#[derive(Clone, Default, Debug, Serialize)]
pub struct Safety {
    pub regions: BTreeMap<Hash, BTreeSet<Hash>>,
}
#[derive(Debug, Serialize)]
pub struct Exposure {
    pub quarantined_coins: Vec<Hash>,
    pub retained_coin_amount: Amount,
    pub affected_historical_exports: Vec<Hash>,
    pub retained_historical_export_amount: Amount,
    pub refunds_or_balance_reversals: bool,
}
impl Safety {
    pub fn from_conflicts(conflicts: &[Conflict], trust: &Trust) -> Result<Self> {
        require(conflicts.len() <= MAX_INCIDENTS, "incident count bound")?;
        let mut result = Self::default();
        for proof in conflicts {
            proof.verify(trust)?;
            result
                .regions
                .entry(proof.region())
                .or_default()
                .insert(proof.id()?);
        }
        Ok(result)
    }
    pub fn check_region(&self, region: Hash) -> Result<()> {
        require(
            !self.regions.contains_key(&region),
            "local region has authenticated conflicting finality; new operations are quarantined",
        )
    }
    fn affected(&self, dependencies: &BTreeSet<Hash>, evidence: &VerifiedEvidence) -> Result<bool> {
        for dependency in dependencies {
            if self
                .regions
                .contains_key(&evidence.snapshot(*dependency)?.statement.region)
            {
                return Ok(true);
            }
        }
        Ok(false)
    }
    pub fn check(
        &self,
        chain: &Chain,
        commands: &[Command],
        evidence: &VerifiedEvidence,
    ) -> Result<()> {
        self.check_region(chain.region)?;
        for command in commands {
            match command {
                Command::Spend(signed) => {
                    for input in &signed.intent.inputs {
                        if let Some(coin) = chain.ledger.coins.get(input) {
                            require(!self.affected(&coin.dependencies,evidence)?,"input depends on quarantined finality; retained assets cannot be newly spent or exported")?;
                        }
                    }
                }
                Command::Import { snapshot, export } => {
                    let record = evidence.export(*snapshot, *export)?;
                    require(
                        !self
                            .regions
                            .contains_key(&evidence.snapshot(*snapshot)?.statement.region)
                            && !self.affected(&record.dependencies, evidence)?,
                        "new import depends on quarantined finality",
                    )?;
                }
            }
        }
        Ok(())
    }
    pub fn exposure(&self, chain: &Chain, evidence: &VerifiedEvidence) -> Result<Exposure> {
        let local = self.regions.contains_key(&chain.region);
        let mut coins = vec![];
        let mut amount = Amount::ZERO;
        let mut exports = vec![];
        let mut exported = Amount::ZERO;
        for (id, coin) in &chain.ledger.coins {
            if local || self.affected(&coin.dependencies, evidence)? {
                coins.push(*id);
                amount = add(amount, coin.payment.amount)?;
            }
        }
        for (id, record) in &chain.ledger.exports {
            if local || self.affected(&record.dependencies, evidence)? {
                exports.push(*id);
                exported = add(exported, record.recipient.amount)?;
            }
        }
        Ok(Exposure {
            quarantined_coins: coins,
            retained_coin_amount: amount,
            affected_historical_exports: exports,
            retained_historical_export_amount: exported,
            refunds_or_balance_reversals: false,
        })
    }
}
