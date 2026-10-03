//! Public deterministic seeds only. Exercises separate native CLI processes.
use ed25519_dalek::SigningKey;
use rld_core::{sign_bytes, AdmissionHash32 as Hash, Amount};
use rld_regional_ledger_candidate::{
    storage::{read_json, Journal},
    *,
};
use serde_json::{json, Value};
use std::{
    fs,
    path::{Path, PathBuf},
    process::Command as Process,
};
fn public(seed: u8) -> String {
    hex::encode(
        SigningKey::from_bytes(&[seed; 32])
            .verifying_key()
            .to_bytes(),
    )
}
fn signature(seed: u8, bytes: &[u8]) -> Result<String> {
    sign_bytes(&hex::encode([seed; 32]), bytes)
}
fn seeds(region: &str) -> Vec<u8> {
    let first = match region {
        "earth" => 2,
        "proxima" => 22,
        "andromeda" => 42,
        _ => panic!("fixture region"),
    };
    let mut seeds = (first..first + 4).collect::<Vec<_>>();
    seeds.sort_by_key(|s| public(*s));
    seeds
}
fn save<T: serde::Serialize>(path: &Path, value: &T) -> Result<()> {
    fs::write(path, serde_json::to_vec(value).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())
}
struct Campaign {
    root: PathBuf,
    binary: PathBuf,
    bootstrap: Bootstrap,
    pin: Hash,
    checks: Vec<Value>,
    calls: usize,
}
impl Campaign {
    fn cli(&mut self, region: &str, args: &[String], success: bool) -> Result<Value> {
        let output = Process::new(&self.binary)
            .arg("--dir")
            .arg(self.root.join(region))
            .arg("--authority")
            .arg(public(1))
            .arg("--currency")
            .arg(self.pin.to_hex())
            .args(args)
            .output()
            .map_err(|e| e.to_string())?;
        self.calls += 1;
        if output.status.success() != success {
            return Err(format!(
                "CLI {region} {args:?}: {}",
                String::from_utf8_lossy(&output.stderr)
            ));
        }
        if success {
            serde_json::from_slice(&output.stdout).map_err(|e| e.to_string())
        } else {
            Ok(json!({"rejected":true,"reason":String::from_utf8_lossy(&output.stderr).trim()}))
        }
    }
    fn chain(&self, region: &str) -> Result<Chain> {
        let journal: Journal = read_json(&self.root.join(region).join("journal.json"))?;
        Ok(journal.replay(&public(1), self.pin)?.2)
    }
    fn audit(&mut self, phase: &str) -> Result<()> {
        let chains = [
            self.chain("earth")?,
            self.chain("proxima")?,
            self.chain("andromeda")?,
        ];
        let (issued, liquid, pending) = conservation(&chains)?;
        self.checks.push(json!({"phase":phase,"issued":issued,"liquid_including_immature_and_fees":liquid,"pending_exports":pending,"conserved":true}));
        Ok(())
    }
    fn mine(&mut self, region: &str, commands: Vec<Command>) -> Result<()> {
        let path = self.root.join("commands.json");
        save(&path, &commands)?;
        self.cli(
            region,
            &[
                "mine".into(),
                "--miner".into(),
                public(10),
                "--commands".into(),
                path.display().to_string(),
            ],
            true,
        )?;
        self.audit(&format!("{region}:block"))
    }
    fn certify(&mut self, region: &str) -> Result<Hash> {
        let value = self.cli(region, &["statement".into()], true)?;
        let statement: Statement =
            serde_json::from_value(value["statement"].clone()).map_err(|e| e.to_string())?;
        let blocks: Vec<Block> =
            serde_json::from_value(value["blocks"].clone()).map_err(|e| e.to_string())?;
        let approvals = seeds(region)
            .into_iter()
            .map(|seed| {
                Ok(Approval {
                    key: public(seed),
                    signature: signature(seed, &statement.bytes()?)?,
                })
            })
            .collect::<Result<Vec<_>>>()?;
        let sid = statement.id()?;
        let path = self.root.join("checkpoint.json");
        save(
            &path,
            &Snapshot {
                statement,
                approvals,
                blocks,
            },
        )?;
        self.cli(
            region,
            &[
                "finalize".into(),
                "--file".into(),
                path.display().to_string(),
            ],
            true,
        )?;
        self.audit(&format!("{region}:checkpoint"))?;
        Ok(sid)
    }
    fn carry(&mut self, from: &str, to: &str) -> Result<()> {
        let proof = self.cli(from, &["proof".into()], true)?;
        let path = self.root.join("contact-evidence.json");
        save(&path, &proof)?;
        self.cli(
            to,
            &[
                "evidence".into(),
                "--file".into(),
                path.display().to_string(),
            ],
            true,
        )?;
        self.audit(&format!("contact:{from}->{to}"))
    }
    fn spend(
        &self,
        region: &str,
        owners: &[u8],
        outputs: Vec<(u8, u128)>,
        remote: Option<(&str, u8, u128, u128)>,
        fee: u128,
    ) -> Result<SignedIntent> {
        let chain = self.chain(region)?;
        let trust = Trust::verify(&self.bootstrap, &public(1), self.pin)?;
        let mut inputs = chain
            .ledger
            .coins
            .iter()
            .filter(|(_, c)| {
                owners.iter().any(|o| public(*o) == c.payment.owner)
                    && c.mature <= chain.height() + 1
            })
            .map(|(id, _)| *id)
            .collect::<Vec<_>>();
        inputs.sort();
        let intent = Intent {
            currency: self.pin,
            region: chain.region,
            inputs,
            outputs: outputs
                .into_iter()
                .map(|(owner, amount)| Payment {
                    owner: public(owner),
                    amount: Amount(amount),
                })
                .collect(),
            fee: Amount(fee),
            destination: remote.map(|(r, _, _, _)| trust.named(r)).transpose()?,
            remote: remote.map(|(_, o, a, _)| Payment {
                owner: public(o),
                amount: Amount(a),
            }),
            destination_fee: Amount(remote.map(|(_, _, _, fee)| fee).unwrap_or(0)),
            valid_through: 100,
        };
        let mut approvals = owners
            .iter()
            .map(|seed| {
                Ok(Approval {
                    key: public(*seed),
                    signature: signature(*seed, &intent.bytes()?)?,
                })
            })
            .collect::<Result<Vec<_>>>()?;
        approvals.sort_by(|a, b| a.key.cmp(&b.key));
        Ok(SignedIntent { intent, approvals })
    }
    fn reject(&mut self, region: &str, commands: Vec<Command>, label: &str) -> Result<()> {
        let before = self.chain(region)?.ledger.root()?;
        let path = self.root.join("attack.json");
        save(&path, &commands)?;
        let result = self.cli(
            region,
            &[
                "mine".into(),
                "--miner".into(),
                public(10),
                "--commands".into(),
                path.display().to_string(),
            ],
            false,
        )?;
        if self.chain(region)?.ledger.root()? != before {
            return Err("rejection mutated ledger".into());
        }
        self.checks
            .push(json!({"attack":label,"result":result,"unchanged_state":true}));
        Ok(())
    }
}
fn run() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let root = PathBuf::from(
        args.next()
            .ok_or("new absolute output directory required")?,
    );
    if args.next().is_some() || !root.is_absolute() || root.exists() {
        return Err("only a NEW absolute fixture directory is accepted".into());
    }
    let binary = std::env::current_exe()
        .map_err(|e| e.to_string())?
        .with_file_name("rld-regional-ledger-candidate");
    if !binary.is_file() {
        return Err("build all candidate binaries first".into());
    }
    let mut currency = Currency {
        format: "RLD-REGIONAL-FIXTURE-V1".into(),
        fixture_only: true,
        implementation: implementation()?,
        origin: "earth".into(),
        authority: public(1),
        cap: Amount(300),
        block_reward: Amount(100),
        maturity: 2,
        signature: String::new(),
    };
    currency.signature = signature(1, &currency.bytes()?)?;
    let pin = currency.id()?;
    let admissions = ["earth", "proxima", "andromeda"]
        .into_iter()
        .map(|region| {
            let mut admission = Admission {
                currency: pin,
                region: region.into(),
                rules: "RLD-REGIONAL-FIXTURE-V1".into(),
                validators: seeds(region).into_iter().map(public).collect(),
                signature: String::new(),
            };
            admission.signature = signature(1, &admission.bytes()?)?;
            Ok(admission)
        })
        .collect::<Result<Vec<_>>>()?;
    let bootstrap = Bootstrap {
        currency,
        admissions,
    };
    fs::create_dir(&root).map_err(|e| e.to_string())?;
    save(&root.join("bootstrap.json"), &bootstrap)?;
    let mut c = Campaign {
        root: root.clone(),
        binary,
        bootstrap,
        pin,
        checks: vec![],
        calls: 0,
    };
    for region in ["earth", "proxima", "andromeda"] {
        c.cli(
            region,
            &[
                "init".into(),
                "--bootstrap".into(),
                root.join("bootstrap.json").display().to_string(),
                "--region".into(),
                region.into(),
            ],
            true,
        )?;
    }
    for _ in 0..4 {
        c.mine("earth", vec![])?;
    }
    c.certify("earth")?;
    // Two separate source coins, two destinations; an original debit never
    // becomes spendable merely because a receipt or timeout is observed.
    let mut outbound = c.spend(
        "earth",
        &[10],
        vec![(10, 19)],
        Some(("proxima", 11, 80, 2)),
        1,
    )?;
    let original = c.chain("earth")?;
    let mature = original
        .ledger
        .coins
        .iter()
        .filter(|(_, coin)| coin.mature <= 5)
        .map(|(id, _)| *id)
        .collect::<Vec<_>>();
    outbound.intent.inputs = vec![mature[0]];
    outbound.approvals[0].signature = signature(10, &outbound.intent.bytes()?)?;
    let first = outbound.intent.id()?;
    let mut direct = c.spend(
        "earth",
        &[10],
        vec![(10, 49)],
        Some(("andromeda", 12, 50, 2)),
        1,
    )?;
    direct.intent.inputs = vec![mature[1]];
    direct.approvals[0].signature = signature(10, &direct.intent.bytes()?)?;
    let second = direct.intent.id()?;
    c.mine(
        "earth",
        vec![
            Command::Spend(Box::new(outbound)),
            Command::Spend(Box::new(direct)),
        ],
    )?;
    let earth_sid = c.certify("earth")?;
    let earth_root = c.chain("earth")?.ledger.root()?;
    c.carry("earth", "proxima")?;
    c.reject(
        "proxima",
        vec![Command::Import {
            snapshot: earth_sid,
            export: second,
        }],
        "wrong destination",
    )?;
    c.mine(
        "proxima",
        vec![Command::Import {
            snapshot: earth_sid,
            export: first,
        }],
    )?;
    c.reject(
        "proxima",
        vec![Command::Import {
            snapshot: earth_sid,
            export: first,
        }],
        "duplicate import",
    )?;
    let mut premature = c.spend("proxima", &[11], vec![(12, 78)], None, 0)?;
    premature.intent.inputs = c
        .chain("proxima")?
        .ledger
        .coins
        .iter()
        .filter(|(_, coin)| coin.payment.owner == public(11))
        .map(|(id, _)| *id)
        .collect();
    premature.approvals[0].signature = signature(11, &premature.intent.bytes()?)?;
    c.reject(
        "proxima",
        vec![Command::Spend(Box::new(premature))],
        "immature payment",
    )?;
    for _ in 0..2 {
        c.mine("proxima", vec![])?;
    }
    let unfinalized = c.spend("proxima", &[11], vec![], Some(("andromeda", 12, 78, 0)), 0)?;
    c.reject(
        "proxima",
        vec![Command::Spend(Box::new(unfinalized))],
        "mature input lacking local finality",
    )?;
    c.certify("proxima")?;
    let payment = c.spend("proxima", &[11], vec![(12, 30), (11, 47)], None, 1)?;
    c.mine("proxima", vec![Command::Spend(Box::new(payment))])?;
    c.certify("proxima")?;
    let onward = c.spend("proxima", &[12], vec![], Some(("andromeda", 12, 29, 1)), 1)?;
    let onward_id = onward.intent.id()?;
    c.mine("proxima", vec![Command::Spend(Box::new(onward))])?;
    let proxima_sid = c.certify("proxima")?;
    c.carry("proxima", "andromeda")?;
    c.mine(
        "andromeda",
        vec![
            Command::Import {
                snapshot: earth_sid,
                export: second,
            },
            Command::Import {
                snapshot: proxima_sid,
                export: onward_id,
            },
        ],
    )?;
    for _ in 0..2 {
        c.mine("andromeda", vec![])?;
    }
    c.certify("andromeda")?;
    let merged = c.spend("andromeda", &[12], vec![(12, 30), (13, 45)], None, 1)?;
    c.mine("andromeda", vec![Command::Spend(Box::new(merged))])?;
    c.certify("andromeda")?;
    let returning = c.spend(
        "andromeda",
        &[12, 13],
        vec![],
        Some(("earth", 14, 74, 1)),
        1,
    )?;
    let returning_id = returning.intent.id()?;
    let mut forged = returning.clone();
    forged.approvals.pop();
    c.reject(
        "andromeda",
        vec![Command::Spend(Box::new(forged))],
        "missing second owner signature",
    )?;
    c.mine("andromeda", vec![Command::Spend(Box::new(returning))])?;
    let andromeda_sid = c.certify("andromeda")?;
    if c.chain("earth")?.ledger.root()? != earth_root {
        return Err("Earth changed during disconnected regional execution".into());
    }
    c.audit("Earth unused during remote payments and onward value; return pending")?;
    c.carry("andromeda", "proxima")?;
    c.carry("proxima", "earth")?;
    c.mine(
        "earth",
        vec![Command::Import {
            snapshot: andromeda_sid,
            export: returning_id,
        }],
    )?;
    c.reject(
        "earth",
        vec![Command::Import {
            snapshot: andromeda_sid,
            export: returning_id,
        }],
        "cyclic replay at origin",
    )?;
    let final_earth = c.chain("earth")?;
    if !final_earth.ledger.exports.contains_key(&first) || first == returning_id {
        return Err("return reused initial debit".into());
    }
    for region in ["earth", "proxima", "andromeda"] {
        c.cli(region, &["status".into()], true)?;
    }
    let report = json!({"format":"RLD-REGIONAL-NATIVE-FIXTURE-CAMPAIGN-V1","result":"PASS_BOUNDED_NATIVE_CLI_CAMPAIGN","currency":pin,"implementation":implementation()?,"native_cli_process_invocations":c.calls,"regions":3,"region_validator_keys_distinct":true,"owners":5,"checks":c.checks,"original_export":first,"direct_earth_to_andromeda_export":second,"onward_export":onward_id,"new_return_export":returning_id,"mainnet_authorized":false,"physical_route_verified":false,"independent_operators":false,"logical_years_or_physical_aging_tested":false,"live_rld":false,"source_http_used":false,"consensus_scope":"append-only mined histories and unanimous checkpoints; public fixture signer keys, no BFT view change or conflicting-certificate recovery","limits":{"blocks_per_region":MAX_BLOCKS,"snapshots":MAX_SNAPSHOTS,"journal_bytes":MAX_BYTES},"unimplemented":["native mesh automation and real contact adapter","fork selection and independent regional BFT qualification","conflicting certificate quarantine and dependency recovery","channels and reservations","validator epochs and cryptographic horizon","external rollback root and independent archives"]});
    save(&root.join("report.json"), &report)?;
    println!(
        "{}",
        serde_json::to_string_pretty(&report).map_err(|e| e.to_string())?
    );
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("fixture campaign failed: {error}");
        std::process::exit(1);
    }
}
