#[test]
fn exact_trust_set_is_required_before_reusing_a_verified_prefix() {
    let mut fixture = Fixture::new();
    advance(
        &mut fixture.earth,
        &fixture.trust,
        &fixture.evidence,
        vec![],
    );
    let next = checkpoint(&fixture.earth, &fixture.trust);
    let mut package = bootstrap();
    package.admissions.retain(|a| a.region != "andromeda");
    let reduced = Trust::verify(&package, &public(1), package.currency.id().unwrap()).unwrap();
    // Same currency and exact Earth admission, but another admitted trust set.
    assert_eq!(
        reduced.currency().unwrap(),
        fixture.trust.currency().unwrap()
    );
    assert_eq!(reduced.named("earth").unwrap(), fixture.earth.region);
    let before = fixture.evidence.snapshots.clone();
    assert!(fixture.evidence.add(next.clone(), &reduced).is_err());
    assert_eq!(fixture.evidence.snapshots, before);
    fixture.evidence.add(next, &fixture.trust).unwrap();
}
