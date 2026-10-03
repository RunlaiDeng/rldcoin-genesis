//! Typed public consensus carriage. The mesh never supplies validator rights.
//! Standalone proof verification precedes catch-up or any new local signature.
use super::*;
use crate::{bft, storage::Store};

pub const FORMAT: &str = "RLD-REGIONAL-BFT-NETWORK-V1";
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum Body {
    Signed(Box<bft::Message>),
    Finalized(Box<Snapshot>),
    Submission(Vec<Command>),
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Envelope {
    pub format: String,
    pub currency: Hash,
    pub region: Hash,
    pub evidence: Evidence,
    pub body: Body,
}
impl Envelope {
    pub fn value(&self) -> Result<Option<Hash>> {
        match &self.body {
            Body::Signed(message) => match message.as_ref() {
                bft::Message::Proposal(p) => Ok(Some(p.snapshot.statement.id()?)),
                bft::Message::Vote(v) => Ok(Some(v.value)),
                bft::Message::Timeout(_) => Ok(None),
            },
            Body::Finalized(s) => Ok(Some(s.statement.id()?)),
            Body::Submission(_) => Ok(None),
        }
    }
    pub fn verify(&self, node: &Store) -> Result<Hash> {
        require(
            self.format == FORMAT
                && self.currency == node.trust.currency()?
                && self.region == node.chain.region
                && node.trust.region(self.region)?.rules == bft::RULES,
            "consensus envelope domain/profile mismatch",
        )?;
        let evidence = VerifiedEvidence::verify(&self.evidence, &node.trust)?;
        match &self.body {
            Body::Signed(message) => {
                let c = match message.as_ref() {
                    bft::Message::Proposal(p) => {
                        p.verify(&node.trust, &evidence)?;
                        p.context()?
                    }
                    bft::Message::Vote(v) => {
                        v.verify(&v.context.keys(&node.trust, &evidence)?)?;
                        v.context.clone()
                    }
                    bft::Message::Timeout(t) => {
                        t.verify(&t.context.keys(&node.trust, &evidence)?)?;
                        t.context.clone()
                    }
                };
                require(
                    c.currency == self.currency && c.region == self.region,
                    "consensus message differs from envelope domain",
                )?;
                // Even votes bind an independently certified native parent.
                if let Some(previous) = c.previous {
                    let parent = evidence.snapshot(previous)?;
                    require(
                        parent.statement.region == c.region
                            && parent.statement.height == c.parent_height
                            && parent.statement.block == c.parent_block
                            && parent.statement.state == c.parent_state,
                        "consensus message omits or changes certified parent",
                    )?;
                } else {
                    require(
                        c.parent_height == 0
                            && c.parent_block == c.region
                            && c.parent_state == Ledger::default().root()?,
                        "consensus message changes native genesis parent",
                    )?;
                }
            }
            Body::Finalized(snapshot) => {
                require(
                    snapshot.statement.region == self.region,
                    "foreign finality message",
                )?;
                let mut verified = evidence.clone();
                verified.add((**snapshot).clone(), &node.trust)?;
            }
            Body::Submission(commands) => {
                require(
                    !commands.is_empty() && commands.len() <= 4,
                    "submission command bound",
                )?;
                let local = self
                    .evidence
                    .snapshots
                    .iter()
                    .filter(|s| s.statement.region == self.region)
                    .max_by_key(|s| s.statement.height);
                let mut chain = Chain::new(self.region, &node.trust)?;
                if let Some(s) = local {
                    for block in &s.blocks {
                        chain.accept(block.clone(), &node.trust, &evidence)?;
                    }
                    chain.install(s.statement.id()?, &evidence)?;
                }
                // Validate real signed commands against the supplied certified
                // parent. Receiving a submission neither signs nor debits.
                chain.template(
                    commands.clone(),
                    node.trust.region(self.region)?.validators[0].clone(),
                    &node.trust,
                    &evidence,
                )?;
            }
        }
        id("bft-network-envelope-v1", self)
    }
}

pub fn sync(node: &mut Store, evidence: Evidence) -> Result<()> {
    bft::Context::current(node)?;
    VerifiedEvidence::verify(&evidence, &node.trust)?;
    node.add_evidence(evidence)?;
    let mut snapshots = node
        .journal
        .evidence
        .snapshots
        .iter()
        .filter(|s| s.statement.region == node.chain.region)
        .cloned()
        .collect::<Vec<_>>();
    snapshots.sort_by_key(|s| s.statement.height);
    for snapshot in snapshots {
        if snapshot.statement.height > node.chain.height() {
            // Every step remains an atomic next-block/finality native commit.
            node.finalize(snapshot)?;
        }
    }
    Ok(())
}
