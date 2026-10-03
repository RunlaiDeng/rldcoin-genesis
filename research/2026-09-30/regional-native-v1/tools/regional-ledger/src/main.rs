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
    Statement,
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
    let mut store = Store::open(&args.dir, &args.authority, pin)?;
    match args.action {
        Action::Init { .. } => unreachable!(),
        Action::Status => println!(
            "{}",
            serde_json::json!({"region":store.chain.region,"currency":pin,"height":store.chain.height(),"tip":store.chain.tip()?,"state":store.chain.ledger.root()?,"finality":store.chain.finalized,"ledger":store.chain.ledger,"fixture_only":true,"live_rld":false,"source_http_required":false,"consensus":"append-only PoW history with explicit unanimous checkpoint; no BFT view changes"})
        ),
        Action::Mine { miner, commands } => {
            let commands = commands
                .map(|p| read_json::<Vec<Command>>(&p))
                .transpose()?
                .unwrap_or_default();
            let mut block = store
                .chain
                .template(commands, miner, &store.trust, &store.evidence)?;
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
        Action::Proof => println!(
            "{}",
            serde_json::to_string(&store.journal.evidence).map_err(|e| e.to_string())?
        ),
        Action::Statement => println!(
            "{}",
            serde_json::json!({"statement":store.chain.statement(&store.trust)?,"blocks":store.chain.blocks})
        ),
    }
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("regional candidate rejected: {error}");
        std::process::exit(1);
    }
}
