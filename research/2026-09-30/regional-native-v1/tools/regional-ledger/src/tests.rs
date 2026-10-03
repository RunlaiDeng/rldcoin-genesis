use super::*;
use ed25519_dalek::SigningKey;
use rld_core::sign_bytes;
use storage::Store;
fn public(seed: u8) -> String {
    hex::encode(
        SigningKey::from_bytes(&[seed; 32])
            .verifying_key()
            .to_bytes(),
    )
}
fn signature(seed: u8, bytes: &[u8]) -> String {
    sign_bytes(&hex::encode([seed; 32]), bytes).unwrap()
}
fn keys() -> Vec<u8> {
    let mut seeds = vec![2, 3, 4, 5];
    seeds.sort_by_key(|s| public(*s));
    seeds
}
fn bootstrap() -> Bootstrap {
    let mut currency = Currency {
        format: DOMAIN.into(),
        fixture_only: true,
        implementation: implementation().unwrap(),
        origin: "earth".into(),
        authority: public(1),
        cap: Amount(300),
        block_reward: Amount(100),
        maturity: 2,
        signature: String::new(),
    };
    currency.signature = signature(1, &currency.bytes().unwrap());
    let admissions = ["earth", "proxima", "andromeda"]
        .into_iter()
        .map(|region| {
            let mut a = Admission {
                currency: currency.id().unwrap(),
                region: region.into(),
                rules: DOMAIN.into(),
                validators: keys().into_iter().map(public).collect(),
                signature: String::new(),
            };
            a.signature = signature(1, &a.bytes().unwrap());
            a
        })
        .collect();
    Bootstrap {
        currency,
        admissions,
    }
}
fn checkpoint(chain: &Chain, trust: &Trust) -> Snapshot {
    let statement = chain.statement(trust).unwrap();
    let approvals = keys()
        .into_iter()
        .map(|seed| Approval {
            key: public(seed),
            signature: signature(seed, &statement.bytes().unwrap()),
        })
        .collect();
    Snapshot {
        statement,
        approvals,
        blocks: chain.blocks.clone(),
    }
}
fn advance(chain: &mut Chain, trust: &Trust, evidence: &VerifiedEvidence, commands: Vec<Command>) {
    let mut block = chain
        .template(commands, public(10), trust, evidence)
        .unwrap();
    mine(&mut block).unwrap();
    chain.accept(block, trust, evidence).unwrap();
}
fn finalize(chain: &mut Chain, trust: &Trust, evidence: &mut VerifiedEvidence) -> Hash {
    let sid = evidence.add(checkpoint(chain, trust), trust).unwrap();
    chain.install(sid, evidence).unwrap();
    sid
}
#[allow(clippy::too_many_arguments)] // Fixture builder mirrors the signed wire fields.
fn intent(
    chain: &Chain,
    trust: &Trust,
    inputs: Vec<Hash>,
    outputs: Vec<Payment>,
    destination: Option<Hash>,
    remote: Option<Payment>,
    fee: u128,
    destination_fee: u128,
    seeds: &[u8],
) -> SignedIntent {
    let mut inputs = inputs;
    inputs.sort();
    let intent = Intent {
        currency: trust.currency().unwrap(),
        region: chain.region,
        inputs,
        outputs,
        fee: Amount(fee),
        destination,
        remote,
        destination_fee: Amount(destination_fee),
        valid_through: 100,
    };
    let mut approvals = seeds
        .iter()
        .map(|seed| Approval {
            key: public(*seed),
            signature: signature(*seed, &intent.bytes().unwrap()),
        })
        .collect::<Vec<_>>();
    approvals.sort_by(|a, b| a.key.cmp(&b.key));
    SignedIntent { intent, approvals }
}
fn coins(chain: &Chain, owner: u8) -> Vec<Hash> {
    chain
        .ledger
        .coins
        .iter()
        .filter(|(_, c)| c.payment.owner == public(owner) && c.mature <= chain.height() + 1)
        .map(|(id, _)| *id)
        .collect()
}
struct Fixture {
    trust: Trust,
    earth: Chain,
    proxima: Chain,
    andromeda: Chain,
    evidence: VerifiedEvidence,
}
impl Fixture {
    fn new() -> Self {
        let b = bootstrap();
        let trust = Trust::verify(&b, &public(1), b.currency.id().unwrap()).unwrap();
        let mut earth = Chain::new(trust.named("earth").unwrap(), &trust).unwrap();
        let proxima = Chain::new(trust.named("proxima").unwrap(), &trust).unwrap();
        let andromeda = Chain::new(trust.named("andromeda").unwrap(), &trust).unwrap();
        let mut evidence = VerifiedEvidence::default();
        for _ in 0..4 {
            advance(&mut earth, &trust, &evidence, vec![]);
        }
        finalize(&mut earth, &trust, &mut evidence);
        Self {
            trust,
            earth,
            proxima,
            andromeda,
            evidence,
        }
    }
    fn audit(&self) {
        conservation(&[
            self.earth.clone(),
            self.proxima.clone(),
            self.andromeda.clone(),
        ])
        .unwrap();
    }
    fn export_earth(&mut self) -> (Hash, Hash) {
        let signed = intent(
            &self.earth,
            &self.trust,
            vec![coins(&self.earth, 10)[0]],
            vec![Payment {
                owner: public(10),
                amount: Amount(19),
            }],
            Some(self.proxima.region),
            Some(Payment {
                owner: public(11),
                amount: Amount(80),
            }),
            1,
            2,
            &[10],
        );
        let eid = signed.intent.id().unwrap();
        advance(
            &mut self.earth,
            &self.trust,
            &self.evidence,
            vec![Command::Spend(Box::new(signed))],
        );
        self.audit();
        let sid = finalize(&mut self.earth, &self.trust, &mut self.evidence);
        (sid, eid)
    }
    fn imported(&mut self) -> (Hash, Hash) {
        let (sid, eid) = self.export_earth();
        advance(
            &mut self.proxima,
            &self.trust,
            &self.evidence,
            vec![Command::Import {
                snapshot: sid,
                export: eid,
            }],
        );
        self.audit();
        (sid, eid)
    }
}
#[test]
fn currency_and_offline_admission_are_exact() {
    let b = bootstrap();
    let pin = b.currency.id().unwrap();
    Trust::verify(&b, &public(1), pin).unwrap();
    assert!(Trust::verify(&b, &public(2), pin).is_err());
    assert!(Trust::verify(&b, &public(1), Hash([9; 32])).is_err());
    let mut bad = b.clone();
    bad.currency.fixture_only = false;
    assert!(Trust::verify(&bad, &public(1), pin).is_err());
    bad = b.clone();
    bad.admissions[1].validators[0] = public(11);
    assert!(Trust::verify(&bad, &public(1), pin).is_err());
    bad = b;
    bad.admissions[1].rules = "unknown".into();
    assert!(Trust::verify(&bad, &public(1), pin).is_err());
}
#[test]
fn three_region_onward_and_value_return_preserve_supply() {
    let mut f = Fixture::new();
    let (_, first) = f.imported();
    for _ in 0..2 {
        advance(&mut f.proxima, &f.trust, &f.evidence, vec![]);
    }
    finalize(&mut f.proxima, &f.trust, &mut f.evidence);
    let pay = intent(
        &f.proxima,
        &f.trust,
        coins(&f.proxima, 11),
        vec![
            Payment {
                owner: public(12),
                amount: Amount(30),
            },
            Payment {
                owner: public(11),
                amount: Amount(47),
            },
        ],
        None,
        None,
        1,
        0,
        &[11],
    );
    advance(
        &mut f.proxima,
        &f.trust,
        &f.evidence,
        vec![Command::Spend(Box::new(pay))],
    );
    f.audit();
    finalize(&mut f.proxima, &f.trust, &mut f.evidence);
    let onward = intent(
        &f.proxima,
        &f.trust,
        coins(&f.proxima, 12),
        vec![],
        Some(f.andromeda.region),
        Some(Payment {
            owner: public(12),
            amount: Amount(29),
        }),
        1,
        1,
        &[12],
    );
    let second = onward.intent.id().unwrap();
    advance(
        &mut f.proxima,
        &f.trust,
        &f.evidence,
        vec![Command::Spend(Box::new(onward))],
    );
    f.audit();
    let sid = finalize(&mut f.proxima, &f.trust, &mut f.evidence);
    advance(
        &mut f.andromeda,
        &f.trust,
        &f.evidence,
        vec![Command::Import {
            snapshot: sid,
            export: second,
        }],
    );
    f.audit();
    for _ in 0..2 {
        advance(&mut f.andromeda, &f.trust, &f.evidence, vec![]);
    }
    finalize(&mut f.andromeda, &f.trust, &mut f.evidence);
    let back = intent(
        &f.andromeda,
        &f.trust,
        coins(&f.andromeda, 12),
        vec![],
        Some(f.earth.region),
        Some(Payment {
            owner: public(13),
            amount: Amount(27),
        }),
        1,
        1,
        &[12],
    );
    let third = back.intent.id().unwrap();
    advance(
        &mut f.andromeda,
        &f.trust,
        &f.evidence,
        vec![Command::Spend(Box::new(back))],
    );
    let sid = finalize(&mut f.andromeda, &f.trust, &mut f.evidence);
    f.audit();
    advance(
        &mut f.earth,
        &f.trust,
        &f.evidence,
        vec![Command::Import {
            snapshot: sid,
            export: third,
        }],
    );
    f.audit();
    assert!(f.earth.ledger.imports.contains_key(&third));
    assert!(f.earth.ledger.exports.contains_key(&first));
    assert_ne!(first, third);
    assert_eq!(
        conservation(&[f.earth, f.proxima, f.andromeda]).unwrap().0,
        Amount(300)
    );
}
#[test]
fn immature_or_unfinalized_onward_exports_are_rejected() {
    let mut f = Fixture::new();
    f.imported();
    let input = *f
        .proxima
        .ledger
        .coins
        .iter()
        .find(|(_, c)| c.payment.owner == public(11))
        .unwrap()
        .0;
    let export = intent(
        &f.proxima,
        &f.trust,
        vec![input],
        vec![],
        Some(f.andromeda.region),
        Some(Payment {
            owner: public(11),
            amount: Amount(78),
        }),
        0,
        0,
        &[11],
    );
    let root = f.proxima.ledger.root().unwrap();
    assert!(f
        .proxima
        .template(
            vec![Command::Spend(Box::new(export.clone()))],
            public(10),
            &f.trust,
            &f.evidence
        )
        .is_err());
    for _ in 0..2 {
        advance(&mut f.proxima, &f.trust, &f.evidence, vec![]);
    }
    assert!(f
        .proxima
        .template(
            vec![Command::Spend(Box::new(export))],
            public(10),
            &f.trust,
            &f.evidence
        )
        .is_err());
    assert_eq!(root, f.proxima.ledger.root().unwrap());
}
#[test]
fn wrong_destination_replay_and_incomplete_evidence_fail_atomically() {
    let mut f = Fixture::new();
    let (sid, eid) = f.imported();
    let replay = Command::Import {
        snapshot: sid,
        export: eid,
    };
    let root = f.proxima.ledger.root().unwrap();
    assert!(f
        .proxima
        .template(vec![replay.clone()], public(10), &f.trust, &f.evidence)
        .is_err());
    assert!(f
        .andromeda
        .template(vec![replay.clone()], public(10), &f.trust, &f.evidence)
        .is_err());
    let empty = VerifiedEvidence::default();
    assert!(f
        .andromeda
        .template(vec![replay], public(10), &f.trust, &empty)
        .is_err());
    assert_eq!(root, f.proxima.ledger.root().unwrap());
}
#[test]
fn source_certificate_forgery_fork_and_rollback_rejected() {
    let mut f = Fixture::new();
    let (sid, _) = f.export_earth();
    let s = f.evidence.snapshot(sid).unwrap().clone();
    let mut forged = s.clone();
    forged.approvals[0].signature = "00".into();
    assert!(VerifiedEvidence::default().add(forged, &f.trust).is_err());
    let mut missing = s;
    missing.statement.previous = None;
    assert!(f.evidence.add(missing, &f.trust).is_err());
    let initial = f
        .evidence
        .snapshots
        .values()
        .min_by_key(|(s, _)| s.statement.height)
        .unwrap()
        .0
        .clone();
    let old = initial.statement.id().unwrap();
    assert!(f.earth.install(old, &f.evidence).is_err());
}
#[test]
fn tampered_block_or_signature_never_changes_state() {
    let mut f = Fixture::new();
    let signed = intent(
        &f.earth,
        &f.trust,
        vec![coins(&f.earth, 10)[0]],
        vec![Payment {
            owner: public(11),
            amount: Amount(99),
        }],
        None,
        None,
        1,
        0,
        &[10],
    );
    let mut bad = signed.clone();
    bad.intent.outputs[0].amount = Amount(100);
    assert!(f
        .earth
        .template(
            vec![Command::Spend(Box::new(bad))],
            public(10),
            &f.trust,
            &f.evidence
        )
        .is_err());
    let mut block = f
        .earth
        .template(
            vec![Command::Spend(Box::new(signed))],
            public(10),
            &f.trust,
            &f.evidence,
        )
        .unwrap();
    block.header.state = Hash([9; 32]);
    mine(&mut block).unwrap();
    let root = f.earth.ledger.root().unwrap();
    assert!(f.earth.accept(block, &f.trust, &f.evidence).is_err());
    assert_eq!(root, f.earth.ledger.root().unwrap());
}
#[test]
fn split_merge_multiple_owners_and_fee_conserve() {
    let mut f = Fixture::new();
    let split = intent(
        &f.earth,
        &f.trust,
        vec![coins(&f.earth, 10)[0]],
        vec![
            Payment {
                owner: public(11),
                amount: Amount(40),
            },
            Payment {
                owner: public(12),
                amount: Amount(59),
            },
        ],
        None,
        None,
        1,
        0,
        &[10],
    );
    advance(
        &mut f.earth,
        &f.trust,
        &f.evidence,
        vec![Command::Spend(Box::new(split))],
    );
    let mut inputs = coins(&f.earth, 11);
    inputs.extend(coins(&f.earth, 12));
    let merge = intent(
        &f.earth,
        &f.trust,
        inputs,
        vec![Payment {
            owner: public(13),
            amount: Amount(97),
        }],
        None,
        None,
        2,
        0,
        &[11, 12],
    );
    let mut bad = merge.clone();
    bad.approvals.pop();
    assert!(f
        .earth
        .template(
            vec![Command::Spend(Box::new(bad))],
            public(10),
            &f.trust,
            &f.evidence
        )
        .is_err());
    advance(
        &mut f.earth,
        &f.trust,
        &f.evidence,
        vec![Command::Spend(Box::new(merge))],
    );
    f.audit();
}
#[test]
fn journal_lock_restart_tombstones_and_corruption() {
    let mut f = Fixture::new();
    let (sid, eid) = f.imported();
    let root = std::fs::canonicalize(std::env::temp_dir())
        .unwrap()
        .join(format!(
            "rld-regional-{}",
            rld_core::generate_identity().public_key
        ));
    let b = bootstrap();
    let pin = b.currency.id().unwrap();
    let mut store = Store::create(&root, b, f.proxima.region, &public(1), pin).unwrap();
    let mut reversed = f
        .evidence
        .snapshots
        .values()
        .map(|(s, _)| s.clone())
        .collect::<Vec<_>>();
    reversed.sort_by_key(|s| std::cmp::Reverse(s.statement.height));
    store
        .add_evidence(Evidence {
            snapshots: reversed,
        })
        .unwrap_err(); // Dependency order must be complete before consumption.
    let mut list = f
        .evidence
        .snapshots
        .values()
        .map(|(s, _)| s.clone())
        .collect::<Vec<_>>();
    list.sort_by_key(|s| s.statement.height);
    store.add_evidence(Evidence { snapshots: list }).unwrap();
    for block in &f.proxima.blocks {
        store.accept(block.clone()).unwrap();
    }
    let state = store.chain.ledger.root().unwrap();
    assert!(Store::open(&root, &public(1), pin).is_err());
    drop(store);
    let store = Store::open(&root, &public(1), pin).unwrap();
    assert_eq!(state, store.chain.ledger.root().unwrap());
    assert!(store
        .chain
        .template(
            vec![Command::Import {
                snapshot: sid,
                export: eid
            }],
            public(10),
            &store.trust,
            &store.evidence
        )
        .is_err());
    drop(store);
    std::fs::write(root.join("journal.json"), b"{}").unwrap();
    assert!(Store::open(&root, &public(1), pin).is_err());
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn duplicate_inputs_bad_amounts_wrong_currency_and_expiry_reject() {
    let f = Fixture::new();
    let signed = intent(
        &f.earth,
        &f.trust,
        vec![coins(&f.earth, 10)[0]],
        vec![Payment {
            owner: public(11),
            amount: Amount(99),
        }],
        None,
        None,
        1,
        0,
        &[10],
    );
    for case in 0..4 {
        let mut bad = signed.clone();
        match case {
            0 => bad.intent.inputs.push(bad.intent.inputs[0]),
            1 => bad.intent.outputs[0].amount = Amount(u128::MAX),
            2 => bad.intent.currency = Hash([9; 32]),
            _ => bad.intent.valid_through = 0,
        }
        bad.approvals[0].signature = signature(10, &bad.intent.bytes().unwrap());
        assert!(f
            .earth
            .template(
                vec![Command::Spend(Box::new(bad))],
                public(10),
                &f.trust,
                &f.evidence
            )
            .is_err());
    }
}
#[test]
fn a_later_invalid_command_rolls_back_the_entire_block() {
    let f = Fixture::new();
    let signed = intent(
        &f.earth,
        &f.trust,
        vec![coins(&f.earth, 10)[0]],
        vec![Payment {
            owner: public(11),
            amount: Amount(99),
        }],
        None,
        None,
        1,
        0,
        &[10],
    );
    let root = f.earth.ledger.root().unwrap();
    let command = Command::Spend(Box::new(signed));
    assert!(f
        .earth
        .template(
            vec![command.clone(), command],
            public(10),
            &f.trust,
            &f.evidence
        )
        .is_err());
    assert_eq!(root, f.earth.ledger.root().unwrap());
}
#[test]
fn zero_regional_issuance_and_no_time_or_receipt_refund() {
    let mut f = Fixture::new();
    let (_, export) = f.export_earth();
    let original = f.earth.ledger.exports[&export].clone();
    for _ in 0..12 {
        advance(&mut f.proxima, &f.trust, &f.evidence, vec![]);
        advance(&mut f.andromeda, &f.trust, &f.evidence, vec![]);
        f.audit();
    }
    assert_eq!(f.proxima.ledger.minted, Amount::ZERO);
    assert_eq!(f.andromeda.ledger.minted, Amount::ZERO);
    assert_eq!(original, f.earth.ledger.exports[&export]);
    assert_eq!(
        conservation(&[f.earth, f.proxima, f.andromeda]).unwrap().2,
        Amount(80)
    );
}
#[test]
fn signed_fork_below_finality_and_missing_checkpoint_dependency_fail() {
    let mut f = Fixture::new();
    let latest = f.earth.finalized.unwrap();
    let accepted = f.evidence.snapshot(latest).unwrap().clone();
    let mut fork = Chain::new(f.earth.region, &f.trust).unwrap();
    let mut block = fork
        .template(vec![], public(11), &f.trust, &VerifiedEvidence::default())
        .unwrap();
    mine(&mut block).unwrap();
    fork.accept(block, &f.trust, &VerifiedEvidence::default())
        .unwrap();
    let root = f.earth.ledger.root().unwrap();
    assert!(f
        .earth
        .accept(fork.blocks[0].clone(), &f.trust, &f.evidence)
        .is_err());
    let mut certificate = checkpoint(&fork, &f.trust);
    certificate.statement.previous = Some(latest);
    certificate.approvals = keys()
        .into_iter()
        .map(|seed| Approval {
            key: public(seed),
            signature: signature(seed, &certificate.statement.bytes().unwrap()),
        })
        .collect();
    assert!(f.evidence.add(certificate, &f.trust).is_err());
    assert_eq!(root, f.earth.ledger.root().unwrap());
    // Even correctly signed onward snapshots cannot bypass an absent source DAG.
    let (source, _) = f.export_earth();
    let snapshot = f.evidence.snapshot(source).unwrap().clone();
    assert!(VerifiedEvidence::default().add(snapshot, &f.trust).is_err());
    assert!(VerifiedEvidence::default().add(accepted, &f.trust).is_ok());
}
#[test]
fn disk_refusal_keeps_previous_journal_and_requires_restart() {
    let b = bootstrap();
    let pin = b.currency.id().unwrap();
    let trust = Trust::verify(&b, &public(1), pin).unwrap();
    let root = std::fs::canonicalize(std::env::temp_dir())
        .unwrap()
        .join(format!(
            "rld-disk-refusal-{}",
            rld_core::generate_identity().public_key
        ));
    let mut store =
        Store::create(&root, b, trust.named("earth").unwrap(), &public(1), pin).unwrap();
    let before = std::fs::read(root.join("journal.json")).unwrap();
    std::fs::write(root.join("journal.next"), b"operator-inspect-residue").unwrap();
    let mut block = store
        .chain
        .template(vec![], public(10), &store.trust, &store.evidence)
        .unwrap();
    mine(&mut block).unwrap();
    assert!(store.accept(block.clone()).is_err());
    assert_eq!(before, std::fs::read(root.join("journal.json")).unwrap());
    std::fs::remove_file(root.join("journal.next")).unwrap();
    assert!(store.accept(block.clone()).is_err());
    drop(store);
    let mut reopened = Store::open(&root, &public(1), pin).unwrap();
    reopened.accept(block).unwrap();
    drop(reopened);
    std::fs::remove_dir_all(root).unwrap();
}
#[test]
fn resource_bounds_reject_without_destroying_evidence() {
    let mut f = Fixture::new();
    let (snapshot, export) = f.export_earth();
    let before = f.proxima.ledger.root().unwrap();
    let commands = vec![Command::Import { snapshot, export }; MAX_COMMANDS + 1];
    assert!(f
        .proxima
        .template(commands, public(10), &f.trust, &f.evidence)
        .is_err());
    assert_eq!(before, f.proxima.ledger.root().unwrap());
    let s = f.evidence.snapshot(snapshot).unwrap().clone();
    let oversized = Evidence {
        snapshots: vec![s; MAX_SNAPSHOTS + 1],
    };
    assert!(VerifiedEvidence::verify(&oversized, &f.trust).is_err());
    let file = std::fs::canonicalize(std::env::temp_dir())
        .unwrap()
        .join(format!(
            "rld-oversize-{}",
            rld_core::generate_identity().public_key
        ));
    let opened = std::fs::File::create(&file).unwrap();
    opened.set_len(MAX_BYTES as u64 + 1).unwrap();
    assert!(storage::read_json::<Evidence>(&file).is_err());
    std::fs::remove_file(file).unwrap();
}
#[cfg(unix)]
#[test]
fn symlinked_store_and_evidence_are_rejected() {
    let dir = std::fs::canonicalize(std::env::temp_dir())
        .unwrap()
        .join(format!(
            "rld-symlink-{}",
            rld_core::generate_identity().public_key
        ));
    std::fs::create_dir(&dir).unwrap();
    std::fs::write(dir.join("real"), b"{}").unwrap();
    std::os::unix::fs::symlink(dir.join("real"), dir.join("link")).unwrap();
    assert!(storage::read_json::<Evidence>(&dir.join("link")).is_err());
    std::fs::remove_dir_all(dir).unwrap();
}
