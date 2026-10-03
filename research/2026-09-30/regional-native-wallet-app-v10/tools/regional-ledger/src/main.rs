use clap::{Parser, Subcommand};
use rld_core::AdmissionHash32 as Hash;
use rld_regional_ledger_candidate::{
    storage::{read_json, Store},
    *,
};
use std::path::PathBuf;
#[derive(Parser)]
#[command(about = "Fixture-only generic regional ledger; no mainnet or remote HTTP")]
struct Args {
    #[arg(long)]
    dir: PathBuf,
    #[arg(long)]
    authority: String,
    #[arg(long)]
    currency: String,
    /// Normal startup enables relay; a contact file is optional when isolated.
    #[arg(long)]
    mesh_config: Option<PathBuf>,
    /// Normal startup includes a bounded TCP listener, loopback ephemeral by default.
    #[arg(long)]
    mesh_listen: Option<String>,
    /// Explicit ground-only plaintext adapter; never used as a TLS fallback.
    #[arg(long)]
    mesh_insecure_tcp: bool,
    /// Explicitly opt into local import block production, separate from relaying.
    #[arg(long)]
    miner: Option<String>,
    #[arg(long, default_value = "python3")]
    transport_python: PathBuf,
    #[arg(long, default_value_t = 1.0)]
    interval: f64,
    #[command(subcommand)]
    action: Option<Action>,
}
#[derive(Subcommand)]
enum Action {
    Init {
        #[arg(long)]
        bootstrap: PathBuf,
        #[arg(long)]
        region: String,
    },
    Status,
    WalletContext,
    WalletApp {
        #[arg(long)]
        wallet_dir: PathBuf,
        #[arg(long)]
        head_dir: PathBuf,
        #[arg(long)]
        owner: String,
        #[arg(long)]
        expected_wallet_head: Option<String>,
        #[arg(long)]
        key_file: Option<PathBuf>,
        #[arg(long, default_value_t = 0)]
        port: u16,
        #[arg(long)]
        miner: Option<String>,
    },
    WalletInit {
        #[arg(long)]
        owner: String,
        #[arg(long)]
        wallet_dir: PathBuf,
    },
    WalletView {
        #[arg(long)]
        wallet_dir: PathBuf,
        #[arg(long)]
        expected_wallet_head: String,
    },
    WalletRecover {
        #[arg(long)]
        wallet_dir: PathBuf,
        #[arg(long)]
        expected_wallet_head: String,
        #[arg(long)]
        intent: String,
    },
    WalletPrepare {
        #[arg(long)]
        file: PathBuf,
        #[arg(long)]
        wallet_dir: PathBuf,
        #[arg(long)]
        expected_wallet_head: String,
    },
    WalletSign {
        #[arg(long)]
        file: PathBuf,
        #[arg(long)]
        key_file: Option<PathBuf>,
        /// Return an exact retained command only; never read a key or first-sign.
        #[arg(long)]
        recover_only: bool,
        #[arg(long)]
        review: String,
        #[arg(long)]
        wallet_dir: PathBuf,
        #[arg(long)]
        expected_wallet_head: String,
    },
    WalletReceipt {
        #[arg(long)]
        file: PathBuf,
    },
    WalletCombine {
        #[arg(long)]
        file: PathBuf,
    },
    Mine {
        #[arg(long)]
        miner: String,
        #[arg(long)]
        commands: Option<PathBuf>,
    },
    Evidence {
        #[arg(long)]
        file: PathBuf,
    },
    Finalize {
        #[arg(long)]
        file: PathBuf,
    },
    Proof,
    Incident {
        #[arg(long)]
        file: PathBuf,
    },
    Incidents,
    RecoverIncident {
        #[arg(long)]
        file: PathBuf,
    },
    Statement,
    ContactExport {
        #[arg(long)]
        export: String,
    },
    ContactApply {
        #[arg(long)]
        file: PathBuf,
        #[arg(long)]
        miner: Option<String>,
    },
    ContactStatus,
    ContactOutgoing,
    ContactResume {
        #[arg(long)]
        message: String,
        #[arg(long)]
        miner: String,
    },
    ContactNode {
        #[arg(long)]
        mesh_config: Option<PathBuf>,
        #[arg(long)]
        mesh_listen: Option<String>,
        #[arg(long)]
        mesh_insecure_tcp: bool,
        #[arg(long)]
        miner: Option<String>,
        #[arg(long, default_value = "python3")]
        transport_python: PathBuf,
        #[arg(long, default_value_t = 1.0)]
        interval: f64,
    },
    ProposeEpoch {
        #[arg(long)]
        validators: PathBuf,
    },
    InstallEpoch {
        #[arg(long)]
        file: PathBuf,
    },
    SignerInit {
        #[arg(long)]
        signer_dir: PathBuf,
        #[arg(long)]
        key: String,
    },
    SignerStatus {
        #[arg(long)]
        signer_dir: PathBuf,
    },
    SignCheckpoint {
        #[arg(long)]
        signer_dir: PathBuf,
        #[arg(long)]
        key_file: PathBuf,
        #[arg(long)]
        expected_lock: String,
    },
    SignHandoff {
        #[arg(long)]
        signer_dir: PathBuf,
        #[arg(long)]
        key_file: PathBuf,
        #[arg(long)]
        expected_lock: String,
        #[arg(long)]
        file: PathBuf,
    },
}
fn require_local_interval(interval: f64) -> Result<()> {
    if interval.is_finite() && (0.1..=3600.0).contains(&interval) {
        Ok(())
    } else {
        Err("contact poll interval outside bound".into())
    }
}
fn run() -> Result<()> {
    let args = Args::parse();
    let pin = Hash::from_hex(&args.currency).map_err(|e| e.to_string())?;
    let action = args.action.unwrap_or(Action::ContactNode {
        mesh_config: args.mesh_config,
        mesh_listen: args.mesh_listen,
        mesh_insecure_tcp: args.mesh_insecure_tcp,
        miner: args.miner,
        transport_python: args.transport_python.clone(),
        interval: args.interval,
    });
    if let Action::ContactNode {
        ref mesh_config,
        ref mesh_listen,
        mesh_insecure_tcp,
        ref miner,
        ref transport_python,
        interval,
    } = action
    {
        require_local_interval(interval)?;
        if let Some(listen) = mesh_listen {
            let address: std::net::SocketAddr = listen
                .parse()
                .map_err(|_| "TCP listener must be literal IPv4:port")?;
            if !address.is_ipv4() {
                return Err("this contact adapter supports IPv4 listeners only".into());
            }
        }
        if let Some(miner) = miner {
            rld_core::validate_ed25519_public_key(miner)?;
        }
        let driver =
            PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../tools/regional_contact_node.py");
        let mut command = std::process::Command::new(transport_python);
        command.arg(driver).args([
            "--binary",
            std::env::current_exe()
                .map_err(|e| e.to_string())?
                .to_str()
                .ok_or("binary path is not UTF-8")?,
            "--ledger",
            args.dir.to_str().ok_or("ledger path is not UTF-8")?,
            "--authority",
            &args.authority,
            "--currency",
            &args.currency,
            "--interval",
            &interval.to_string(),
        ]);
        if let Some(config) = mesh_config {
            command.arg("--mesh-config").arg(config);
        }
        if let Some(listen) = mesh_listen {
            command.arg("--listen").arg(listen);
        }
        if mesh_insecure_tcp {
            command.arg("--insecure-tcp");
        }
        if let Some(miner) = miner {
            command.arg("--miner").arg(miner);
        }
        #[cfg(unix)]
        {
            use std::os::unix::process::CommandExt;
            return Err(command.exec().to_string());
        }
        #[cfg(not(unix))]
        {
            let status = command.status().map_err(|e| e.to_string())?;
            return if status.success() {
                Ok(())
            } else {
                Err("native contact node companion stopped; inspect its explicit diagnostic".into())
            };
        }
    }
    if let Action::WalletApp {
        ref wallet_dir,
        ref head_dir,
        ref owner,
        ref expected_wallet_head,
        ref key_file,
        port,
        ref miner,
    } = action
    {
        rld_core::validate_ed25519_public_key(owner)?;
        let driver =
            PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../tools/regional_wallet_app.py");
        let mut command = std::process::Command::new(&args.transport_python);
        command
            .arg(driver)
            .arg("--binary")
            .arg(std::env::current_exe().map_err(|e| e.to_string())?)
            .arg("--ledger")
            .arg(&args.dir)
            .arg("--authority")
            .arg(&args.authority)
            .arg("--currency")
            .arg(&args.currency)
            .arg("--wallet-dir")
            .arg(wallet_dir)
            .arg("--head-dir")
            .arg(head_dir)
            .arg("--owner")
            .arg(owner)
            .arg("--port")
            .arg(port.to_string());
        if let Some(head) = expected_wallet_head {
            command.arg("--expected-wallet-head").arg(head);
        }
        if let Some(key) = key_file {
            command.arg("--key-file").arg(key);
        }
        if let Some(miner) = miner {
            command.arg("--miner").arg(miner);
        }
        #[cfg(unix)]
        {
            use std::os::unix::process::CommandExt;
            return Err(command.exec().to_string());
        }
        #[cfg(not(unix))]
        {
            return if command.status().map_err(|e| e.to_string())?.success() {
                Ok(())
            } else {
                Err("local wallet app stopped".into())
            };
        }
    }
    if let Action::Init { bootstrap, region } = action {
        let bootstrap: Bootstrap = read_json(&bootstrap)?;
        let trust = Trust::verify(&bootstrap, &args.authority, pin)?;
        let store = Store::create(
            &args.dir,
            bootstrap,
            trust.named(&region)?,
            &args.authority,
            pin,
        )?;
        println!(
            "{}",
            serde_json::json!({"region":store.chain.region,"height":0,"fixture_only":true,"live_rld":false})
        );
        return Ok(());
    }
    if let Action::RecoverIncident { ref file } = action {
        rld_regional_ledger_candidate::storage::recover_incident(
            &args.dir,
            &args.authority,
            pin,
            read_json(file)?,
        )?;
    }
    let mut store = Store::open(&args.dir, &args.authority, pin)?;
    match action {
        Action::WalletContext => println!(
            "{}",
            serde_json::json!({
                "currency":pin,"region":store.chain.region,"fixture_only":true,"live_rld":false,
                "regions":store.journal.bootstrap.admissions.iter().map(|a| Ok(serde_json::json!({"id":a.id()?,"name":a.region}))).collect::<Result<Vec<_>>>()?
            })
        ),
        Action::WalletApp { .. } => return Err("wallet app launcher was not dispatched".into()),
        Action::Init { .. } => unreachable!(),
        Action::WalletInit { owner, wallet_dir } => {
            let agent = wallet_agent::Agent::create(&wallet_dir, &store, owner)?;
            println!(
                "{}",
                serde_json::json!({"binding":agent.journal.binding,"wallet_head":agent.journal.head()?,"retain_head_separately":true})
            );
        }
        Action::WalletView {
            wallet_dir,
            expected_wallet_head,
        } => println!(
            "{}",
            serde_json::to_string(&wallet_agent::Agent::open(&wallet_dir, &store)?.view(
                &store,
                Hash::from_hex(&expected_wallet_head).map_err(|e| e.to_string())?
            )?)
            .map_err(|e| e.to_string())?
        ),
        Action::WalletRecover {
            wallet_dir,
            expected_wallet_head,
            intent,
        } => {
            let agent = wallet_agent::Agent::open(&wallet_dir, &store)?;
            println!(
                "{}",
                serde_json::to_string(&agent.recover(
                    &store,
                    Hash::from_hex(&intent).map_err(|e| e.to_string())?,
                    Hash::from_hex(&expected_wallet_head).map_err(|e| e.to_string())?
                )?)
                .map_err(|e| e.to_string())?
            );
        }
        Action::WalletPrepare {
            file,
            wallet_dir,
            expected_wallet_head,
        } => {
            let agent = wallet_agent::Agent::open(&wallet_dir, &store)?;
            let prepared = agent.prepare(
                &store,
                read_json(&file)?,
                Hash::from_hex(&expected_wallet_head).map_err(|e| e.to_string())?,
            )?;
            println!(
                "{}",
                serde_json::to_string(&prepared).map_err(|e| e.to_string())?
            );
        }
        Action::WalletSign {
            file,
            key_file,
            recover_only,
            review,
            wallet_dir,
            expected_wallet_head,
        } => {
            #[derive(serde::Deserialize)]
            #[serde(deny_unknown_fields)]
            struct Reviewed {
                draft: wallet::Draft,
                review_commitment: Hash,
                wallet_head: Hash,
            }
            let prepared: Reviewed = read_json(&file)?;
            let expected = Hash::from_hex(&review).map_err(|e| e.to_string())?;
            if expected != prepared.review_commitment {
                return Err("wallet separately reviewed commitment differs from file".into());
            }
            let wallet_head = Hash::from_hex(&expected_wallet_head).map_err(|e| e.to_string())?;
            if wallet_head != prepared.wallet_head {
                return Err("wallet head differs from reviewed file".into());
            }
            let mut agent = wallet_agent::Agent::open(&wallet_dir, &store)?;
            if recover_only
                && !agent
                    .journal
                    .records
                    .iter()
                    .any(|r| r.draft == prepared.draft && r.review_commitment == expected)
            {
                return Err("exact retained approval not found; recovery cannot first-sign".into());
            }
            if !recover_only && key_file.is_none() {
                return Err("new signing requires private key file".into());
            }
            let key_file = key_file.unwrap_or_else(|| PathBuf::from("/dev/null"));
            let signed = agent.sign(&store, prepared.draft, &key_file, expected, wallet_head)?;
            println!(
                "{}",
                serde_json::to_string(&signed).map_err(|e| e.to_string())?
            );
        }
        Action::WalletReceipt { file } => println!(
            "{}",
            serde_json::to_string(&wallet::receipt(&store, read_json(&file)?)?)
                .map_err(|e| e.to_string())?
        ),
        Action::WalletCombine { file } => println!(
            "{}",
            serde_json::to_string(&wallet::combine(&store, read_json(&file)?)?)
                .map_err(|e| e.to_string())?
        ),
        Action::Status => println!(
            "{}",
            serde_json::json!({"region":store.chain.region,"currency":pin,"height":store.chain.height(),"tip":store.chain.tip()?,"state":store.chain.ledger.root()?,"finality":store.chain.finalized,"validator_epoch":store.chain.epoch,"ledger":store.chain.ledger,"quarantined_regions":store.safety.regions,"incident_ids":store.conflicts.iter().map(|p|p.id()).collect::<Result<Vec<_>>>()?,"exposure":store.safety.exposure(&store.chain,&store.evidence)?,"fixture_only":true,"live_rld":false,"source_http_required":false,"consensus":"append-only PoW history with explicit unanimous checkpoint; no BFT view changes"})
        ),
        Action::Mine { miner, commands } => {
            let commands = commands
                .map(|p| read_json::<Vec<Command>>(&p))
                .transpose()?
                .unwrap_or_default();
            let mut block = store.template(commands, miner)?;
            mine(&mut block)?;
            store.accept(block.clone())?;
            println!(
                "{}",
                serde_json::to_string(&block).map_err(|e| e.to_string())?
            );
        }
        Action::Evidence { file } => {
            store.add_evidence(read_json(&file)?)?;
            println!(
                "{}",
                serde_json::json!({"verified_snapshots":store.journal.evidence.snapshots.len(),"ledger_changed":false})
            );
        }
        Action::Finalize { file } => {
            let sid = store.finalize(read_json(&file)?)?;
            println!("{}", serde_json::json!({"installed_checkpoint":sid}));
        }
        Action::Incident { file } => {
            let iid = store.observe_conflict(read_json(&file)?)?;
            println!(
                "{}",
                serde_json::json!({"durable_incident":iid,"quarantined_regions":store.safety.regions,"ledger_changed":false})
            );
        }
        Action::RecoverIncident { .. } => println!(
            "{}",
            serde_json::json!({"recovered_retained_incident":true,"quarantined_regions":store.safety.regions})
        ),
        Action::Incidents => println!(
            "{}",
            serde_json::to_string(&store.conflicts).map_err(|e| e.to_string())?
        ),
        Action::Proof => println!(
            "{}",
            serde_json::to_string(&store.journal.evidence).map_err(|e| e.to_string())?
        ),
        Action::ContactNode { .. } => unreachable!(),
        Action::ContactExport { export } => println!(
            "{}",
            String::from_utf8(
                store.contact_export(Hash::from_hex(&export).map_err(|e| e.to_string())?)?
            )
            .map_err(|e| e.to_string())?
        ),
        Action::ContactApply { file, miner } => {
            let bytes =
                rld_regional_ledger_candidate::storage::read_bytes(&file, contact::MAX_FRAME)?;
            println!(
                "{}",
                serde_json::to_string(&store.contact_apply(&bytes, miner)?)
                    .map_err(|e| e.to_string())?
            );
        }
        Action::ContactOutgoing => {
            let mut offers = vec![];
            if let Some(sid) = store.chain.finalized {
                for (eid, record) in &store.chain.ledger.exports {
                    if store.evidence.export(sid, *eid).is_ok() {
                        offers.push(serde_json::json!({"export":eid,"destination":record.destination,"snapshot":sid}));
                    }
                }
            }
            println!(
                "{}",
                serde_json::json!({"currency":pin,"region":store.chain.region,"offers":offers,"all_offers_require_native_contact_export_validation":true})
            );
        }
        Action::ContactStatus => {
            let contacts = store
                .journal
                .contact_records
                .keys()
                .map(|id| store.contact_status(*id))
                .collect::<Result<Vec<_>>>()?;
            println!(
                "{}",
                serde_json::json!({"currency":pin,"region":store.chain.region,"local_height":store.chain.height(),"contacts":contacts,"source_http_required":false})
            );
        }
        Action::ContactResume { message, miner } => println!(
            "{}",
            serde_json::to_string(
                &store
                    .contact_fulfill(Hash::from_hex(&message).map_err(|e| e.to_string())?, miner)?
            )
            .map_err(|e| e.to_string())?
        ),
        Action::Statement => println!(
            "{}",
            serde_json::to_string(&store.snapshot_request()?).map_err(|e| e.to_string())?
        ),
        Action::ProposeEpoch { validators } => println!(
            "{}",
            serde_json::to_string(&store.epoch_request(read_json(&validators)?)?)
                .map_err(|e| e.to_string())?
        ),
        Action::InstallEpoch { file } => {
            let eid = store.install_epoch(read_json(&file)?)?;
            println!(
                "{}",
                serde_json::json!({"installed_validator_epoch":eid,"ledger_changed":false})
            );
        }
        Action::SignerInit { signer_dir, key } => {
            let agent = signer::Agent::create(&signer_dir, &store, key)?;
            println!(
                "{}",
                serde_json::json!({"binding":agent.journal.binding,"lock_head":agent.journal.head()?,"retain_head_separately":true})
            );
        }
        Action::SignerStatus { signer_dir } => {
            let agent = signer::Agent::open(&signer_dir, &store)?;
            println!(
                "{}",
                serde_json::json!({"binding":agent.journal.binding,"lock_head":agent.journal.head()?,"votes":agent.journal.records.len(),"local_status_is_not_an_external_rollback_anchor":true})
            );
        }
        Action::SignCheckpoint {
            signer_dir,
            key_file,
            expected_lock,
        } => {
            let expected = Hash::from_hex(&expected_lock).map_err(|e| e.to_string())?;
            let mut agent = signer::Agent::open(&signer_dir, &store)?;
            println!(
                "{}",
                serde_json::to_string(&agent.checkpoint(&store, &key_file, expected)?)
                    .map_err(|e| e.to_string())?
            );
        }
        Action::SignHandoff {
            signer_dir,
            key_file,
            expected_lock,
            file,
        } => {
            let expected = Hash::from_hex(&expected_lock).map_err(|e| e.to_string())?;
            let mut agent = signer::Agent::open(&signer_dir, &store)?;
            println!(
                "{}",
                serde_json::to_string(&agent.handoff(
                    &store,
                    read_json(&file)?,
                    &key_file,
                    expected
                )?)
                .map_err(|e| e.to_string())?
            );
        }
    }
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("regional candidate rejected: {error}");
        std::process::exit(1);
    }
}
