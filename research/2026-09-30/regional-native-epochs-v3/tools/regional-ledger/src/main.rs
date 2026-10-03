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
    #[command(subcommand)]
    action: Action,
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
fn run() -> Result<()> {
    let args = Args::parse();
    let pin = Hash::from_hex(&args.currency).map_err(|e| e.to_string())?;
    if let Action::Init { bootstrap, region } = args.action {
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
    if let Action::RecoverIncident { ref file } = args.action {
        rld_regional_ledger_candidate::storage::recover_incident(
            &args.dir,
            &args.authority,
            pin,
            read_json(file)?,
        )?;
    }
    let mut store = Store::open(&args.dir, &args.authority, pin)?;
    match args.action {
        Action::Init { .. } => unreachable!(),
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
