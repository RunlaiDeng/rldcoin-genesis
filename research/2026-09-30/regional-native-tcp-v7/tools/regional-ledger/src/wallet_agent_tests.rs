use super::*;
use crate::{wallet::Request, wallet_agent::Agent};
use std::fs;

fn request() -> Request {
    Request {
        owner: public(10),
        inputs: None,
        outputs: vec![Payment {
            owner: public(14),
            amount: Amount(30),
        }],
        remote: None,
        fee: Amount(1),
        valid_for_blocks: 8,
    }
}
fn key(root: &std::path::Path) -> PathBuf {
    let p = root.join("owner.json");
    fs::write(
        &p,
        serde_json::to_vec(&serde_json::json!({"secret_key":hex::encode([10;32])})).unwrap(),
    )
    .unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&p, fs::Permissions::from_mode(0o600)).unwrap();
    }
    p
}
fn step(node: &mut Store, commands: Vec<Command>) {
    let mut block = node.template(commands, public(10)).unwrap();
    mine(&mut block).unwrap();
    node.accept(block).unwrap();
}
#[test]
fn pending_reservations_survive_restart_and_exact_response_loss_retry() {
    let f = Fixture::new();
    let (root, node) = stored_fixture(&f, &f.earth);
    let dir = root.join("wallet");
    let mut agent = Agent::create(&dir, &node, public(10)).unwrap();
    let old = agent.journal.head().unwrap();
    let prepared = agent.prepare(&node, request(), old).unwrap();
    let input = prepared.draft.intent.inputs[0];
    let signed = agent
        .sign(
            &node,
            prepared.draft.clone(),
            &key(&root),
            prepared.review_commitment,
            old,
        )
        .unwrap();
    assert!(!signed.recovered_exact_retry);
    let next = signed.wallet_head;
    drop(agent);
    let mut agent = Agent::open(&dir, &node).unwrap();
    assert!(agent.view(&node, old).is_err());
    let view = agent.view(&node, next).unwrap();
    assert_eq!(view.reserved_owned_outputs, Amount(100));
    assert_eq!(view.available, Amount(100));
    assert!(view.ledger.pending_signed_intents_tracked);
    let retry = agent
        .sign(
            &node,
            prepared.draft,
            &root.join("key-not-needed-for-retry"),
            prepared.review_commitment,
            old,
        )
        .unwrap();
    assert_eq!(retry.commands, signed.commands);
    assert_eq!(retry.wallet_head, next);
    assert!(retry.recovered_exact_retry);
    assert_eq!(agent.journal.records.len(), 1);
    let another = agent.prepare(&node, request(), next).unwrap();
    assert!(!another.draft.intent.inputs.contains(&input));
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn inclusion_releases_only_reservation_and_never_refunds_export() {
    let f = Fixture::new();
    let (root, mut node) = stored_fixture(&f, &f.earth);
    node.finalize(
        f.evidence
            .snapshot(f.earth.finalized.unwrap())
            .unwrap()
            .clone(),
    )
    .unwrap();
    let mut agent = Agent::create(&root.join("wallet"), &node, public(10)).unwrap();
    let head = agent.journal.head().unwrap();
    let mut remote = request();
    remote.outputs.clear();
    remote.remote = Some(wallet::Remote {
        destination: f.proxima.region,
        recipient: Payment {
            owner: public(11),
            amount: Amount(99),
        },
        destination_fee: Amount(1),
    });
    let prepared = agent.prepare(&node, remote, head).unwrap();
    let signed = agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    step(&mut node, signed.commands.clone());
    let view = agent.view(&node, signed.wallet_head).unwrap();
    assert_eq!(view.reserved_owned_outputs, Amount::ZERO);
    assert_eq!(view.signed[0].state, "INCLUDED_IN_LOCAL_LEDGER");
    assert_eq!(view.ledger.spendable, Amount(200));
    assert_eq!(
        node.chain.ledger.exports[&signed.intent_id]
            .recipient
            .amount,
        Amount(99)
    );
    let recovered = agent
        .recover(&node, signed.intent_id, signed.wallet_head)
        .unwrap();
    assert_eq!(recovered.commands, signed.commands);
    assert!(node.template(recovered.commands, public(10)).is_err());
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn only_native_expiry_frees_unincluded_inputs_not_receipt_or_wall_time() {
    let f = Fixture::new();
    let (root, mut node) = stored_fixture(&f, &f.earth);
    let mut agent = Agent::create(&root.join("wallet"), &node, public(10)).unwrap();
    let head = agent.journal.head().unwrap();
    let mut req = request();
    req.valid_for_blocks = 1;
    let prepared = agent.prepare(&node, req, head).unwrap();
    let input = prepared.draft.intent.inputs[0];
    let signed = agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    fs::write(
        root.join("untrusted-transport-receipt.json"),
        b"{\"delivered\":true}",
    )
    .unwrap();
    assert_eq!(
        agent.view(&node, signed.wallet_head).unwrap().signed[0].state,
        "SIGNED_PENDING_INCLUSION"
    );
    step(&mut node, vec![]); // Next candidate height is now strictly beyond expiry.
    assert!(node.template(signed.commands, public(10)).is_err());
    let view = agent.view(&node, signed.wallet_head).unwrap();
    assert_eq!(view.signed[0].state, "EXPIRED_BEFORE_INCLUSION");
    assert_eq!(view.reserved_owned_outputs, Amount::ZERO);
    assert_eq!(view.available, Amount(300));
    let mut req = request();
    req.inputs = Some(vec![input]);
    let prepared = agent.prepare(&node, req, signed.wallet_head).unwrap();
    assert!(prepared.draft.intent.inputs.contains(&input));
    agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            signed.wallet_head,
        )
        .unwrap();
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn separately_retained_head_rejects_old_wallet_backup() {
    let f = Fixture::new();
    let (root, node) = stored_fixture(&f, &f.earth);
    let dir = root.join("wallet");
    let mut agent = Agent::create(&dir, &node, public(10)).unwrap();
    let head = agent.journal.head().unwrap();
    let backup = fs::read(dir.join("wallet.json")).unwrap();
    let prepared = agent.prepare(&node, request(), head).unwrap();
    let signed = agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    drop(agent);
    fs::write(dir.join("wallet.json"), backup).unwrap();
    let agent = Agent::open(&dir, &node).unwrap();
    assert!(agent.prepare(&node, request(), signed.wallet_head).is_err());
    assert!(agent.view(&node, signed.wallet_head).is_err());
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn retained_wallet_rejects_node_backup_after_later_authorized_signing() {
    let f = Fixture::new();
    let (root, mut node) = stored_fixture(&f, &f.earth);
    let dir = root.join("wallet");
    let backup = fs::read(root.join("journal.json")).unwrap();
    let mut agent = Agent::create(&dir, &node, public(10)).unwrap();
    let head = agent.journal.head().unwrap();
    step(&mut node, vec![]);
    let prepared = agent.prepare(&node, request(), head).unwrap();
    agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    drop(agent);
    let pin = node.trust.currency().unwrap();
    drop(node);
    fs::write(root.join("journal.json"), backup).unwrap();
    let node = Store::open(&root, &public(1), pin).unwrap();
    assert!(Agent::open(&dir, &node).is_err());
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn write_failure_never_releases_signature_and_exact_interrupted_commit_recovers() {
    let f = Fixture::new();
    let (root, node) = stored_fixture(&f, &f.earth);
    let dir = root.join("wallet");
    let mut agent = Agent::create(&dir, &node, public(10)).unwrap();
    let head = agent.journal.head().unwrap();
    let previous = agent.journal.clone();
    let prepared = agent.prepare(&node, request(), head).unwrap();
    fs::write(dir.join("wallet.next"), b"partial").unwrap();
    assert!(agent
        .sign(
            &node,
            prepared.draft.clone(),
            &key(&root),
            prepared.review_commitment,
            head
        )
        .is_err());
    assert_eq!(agent.journal.head().unwrap(), head);
    assert!(agent.view(&node, head).is_err());
    drop(agent);
    assert!(Agent::open(&dir, &node).is_err());
    assert_eq!(fs::read(dir.join("wallet.next")).unwrap(), b"partial");
    fs::remove_file(dir.join("wallet.next")).unwrap(); // Fixture fault removed, never a normal cancellation path.
    let mut agent = Agent::open(&dir, &node).unwrap();
    let signed = agent
        .sign(
            &node,
            prepared.draft.clone(),
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    let proposed = agent.journal.clone();
    drop(agent);
    fs::write(
        dir.join("wallet.json"),
        serde_json::to_vec(&previous).unwrap(),
    )
    .unwrap();
    fs::write(
        dir.join("wallet.next"),
        serde_json::to_vec(&proposed).unwrap(),
    )
    .unwrap();
    let mut agent = Agent::open(&dir, &node).unwrap();
    assert_eq!(agent.journal.head().unwrap(), signed.wallet_head);
    assert!(!dir.join("wallet.next").exists());
    let retry = agent
        .sign(
            &node,
            prepared.draft,
            &root.join("missing-key"),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    assert_eq!(retry.commands, signed.commands);
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn wallet_lock_and_corruption_fail_closed_without_overwriting_retained_commands() {
    let f = Fixture::new();
    let (root, node) = stored_fixture(&f, &f.earth);
    let dir = root.join("wallet");
    let mut agent = Agent::create(&dir, &node, public(10)).unwrap();
    assert!(Agent::open(&dir, &node).is_err());
    let head = agent.journal.head().unwrap();
    let prepared = agent.prepare(&node, request(), head).unwrap();
    agent
        .sign(
            &node,
            prepared.draft,
            &key(&root),
            prepared.review_commitment,
            head,
        )
        .unwrap();
    let mut journal = agent.journal.clone();
    journal.records[0].previous_head = Hash([9; 32]);
    drop(agent);
    let bytes = serde_json::to_vec(&journal).unwrap();
    fs::write(dir.join("wallet.json"), &bytes).unwrap();
    assert!(Agent::open(&dir, &node).is_err());
    assert_eq!(fs::read(dir.join("wallet.json")).unwrap(), bytes);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn changed_wallet_head_and_explicit_reserved_inputs_cannot_sign_again() {
    let f = Fixture::new();
    let (root, node) = stored_fixture(&f, &f.earth);
    let mut agent = Agent::create(&root.join("wallet"), &node, public(10)).unwrap();
    let old = agent.journal.head().unwrap();
    let p = agent.prepare(&node, request(), old).unwrap();
    let p2 = agent.prepare(&node, request(), old).unwrap();
    let reserved = p.draft.intent.inputs.clone();
    let signed = agent
        .sign(&node, p.draft, &key(&root), p.review_commitment, old)
        .unwrap();
    let mut altered = p2.draft;
    altered.intent.outputs[0].amount = Amount(31);
    let review = id("wallet-reviewed-draft", &altered).unwrap();
    assert!(agent
        .sign(&node, altered, &key(&root), review, old)
        .is_err());
    let mut r = request();
    r.inputs = Some(reserved);
    assert!(agent.prepare(&node, r, signed.wallet_head).is_err());
    let mut other = request();
    other.owner = public(11);
    assert!(agent.prepare(&node, other, signed.wallet_head).is_err());
    drop(agent);
    drop(node);
    fs::remove_dir_all(root).unwrap();
}
