//! Declaration-evidence lookup, with ambiguous and unmodeled paths left open.
use rust_joern::{
    analyze,
    graph::{Analysis, FunctionGraph, Options},
};
fn parse(s: &str) -> Analysis {
    analyze(
        s,
        "lookup.cpp",
        &Options {
            strict: true,
            preprocessed: true,
            ..Options::default()
        },
    )
    .unwrap()
}
fn f(a: &Analysis) -> &FunctionGraph {
    a.functions.iter().find(|f| f.name == "f").unwrap()
}
fn named<'a>(f: &'a FunctionGraph, name: &str) -> &'a rust_joern::graph::Node {
    let ns: Vec<_> = f
        .cpg
        .nodes
        .iter()
        .filter(|n| n.kind == "CALL" && n.name.as_deref() == Some(name))
        .collect();
    assert_eq!(ns.len(), 1);
    ns[0]
}
fn target(f: &FunctionGraph, id: u32, kind: &str, label: Option<&str>) -> Option<u32> {
    let es: Vec<_> = f
        .cpg
        .edges
        .iter()
        .filter(|e| e.source == id && e.kind == kind && e.label.as_deref() == label)
        .collect();
    assert!(es.len() <= 1);
    es.first().map(|e| e.target)
}

#[test]
fn scoped_aliases_are_frozen_before_unrelated_namespace_and_local_aliases() {
    let a = parse(
        "struct C { int operator()(int); }; struct Other { long operator()(long); }; namespace N { using A=C; } namespace M { using A=Other; } void g() { using A=Other; } namespace N { struct H { A call; }; } int f(N::H& h) { return h.call(1); }",
    );
    assert_eq!(
        named(f(&a), "<operator>()").method_full_name.as_deref(),
        Some("C.<operator>():int(int)")
    );
}
#[test]
fn typedef_alias_chain_keeps_effective_cv_for_untyped_field_fallback() {
    let a = parse(
        "struct C { int operator()(int) const; }; typedef const C Const; using Next=Const; struct H { Next call; }; int f(H& h) { return h.call(1); }",
    );
    let f = f(&a);
    let n = named(f, "call");
    assert_eq!(
        n.method_full_name.as_deref(),
        Some("<unresolvedNamespace>.call:<unresolvedSignature>(1)")
    );
    assert_eq!(
        target(f, n.id, "ARGUMENT", Some("0")),
        target(f, n.id, "RECEIVER", None)
    );
    assert!(target(f, n.id, "RECEIVER", None).is_some());
}
#[test]
fn mutable_field_clears_inherited_owner_cv_and_keeps_whole_receiver() {
    let a = parse(
        "struct C { int operator()(int); }; struct H { mutable C call; }; int f(const H& h) { return h.call(1); }",
    );
    let f = f(&a);
    let n = named(f, "<operator>()");
    assert_eq!(
        n.method_full_name.as_deref(),
        Some("C.<operator>():int(int)")
    );
    let id = target(f, n.id, "RECEIVER", None).unwrap();
    assert_eq!(target(f, n.id, "ARGUMENT", Some("0")), Some(id));
    assert_eq!(f.cpg.nodes[id as usize].code, "h.call");
}
#[test]
fn public_base_chain_resolves_field_and_ordinary_method_receiver_identity() {
    for (source, name, expected) in [
        (
            "struct C { int operator()(int); }; struct B { C call; }; struct D:B {}; struct E:D {}; int f(E& e) { return e.call(1); }",
            "<operator>()",
            "C.<operator>():int(int)",
        ),
        (
            "struct B { int get(int); }; struct D:B {}; int f(D& d) { return d.get(1); }",
            "get",
            "D.get:int(int)",
        ),
        (
            "struct B { int operator()(int); }; struct D:B {}; int f(D& d) { return d(1); }",
            "<operator>()",
            "D.<operator>():int(int)",
        ),
    ] {
        let a = parse(source);
        assert_eq!(
            named(f(&a), name).method_full_name.as_deref(),
            Some(expected)
        );
    }
}
#[test]
fn nearer_field_or_method_hides_a_base_field() {
    let a = parse(
        "struct C { int operator()(int); }; struct B { C call; }; struct D:B { int call(int); }; int f(D& d) { return d.call(1); }",
    );
    assert_eq!(
        named(f(&a), "call").method_full_name.as_deref(),
        Some("D.call:int(int)")
    );
    let a = parse(
        "struct C { int operator()(int); }; struct B { C call; }; struct D:B { int call; }; int f(D& d) { return d.call(1); }",
    );
    assert!(
        !f(&a)
            .cpg
            .nodes
            .iter()
            .any(|n| n.method_full_name.as_deref() == Some("C.<operator>():int(int)"))
    );
}
#[test]
fn complex_inheritance_and_alias_cycles_never_guess_a_callable_target() {
    for declarations in [
        "struct B { C call; }; class H:B {};",
        "struct B { C call; }; struct H:protected B {};",
        "struct B { C call; }; struct H:virtual B {};",
        "struct B { C call; }; struct Other { C call; }; struct H:B,Other {};",
        "using A=B; using B=A; struct H { A call; };",
        "using A=C; using A=Other; struct H { A call; };",
        "struct H { using A=C; A call; };",
    ] {
        let a = parse(&format!(
            "struct C {{ int operator()(int); }}; {declarations} int f(H& h) {{ return h.call(1); }}"
        ));
        assert!(
            !f(&a)
                .cpg
                .nodes
                .iter()
                .any(|n| n.method_full_name.as_deref() == Some("C.<operator>():int(int)")),
            "unexpected proof: {declarations}"
        );
    }
}
#[test]
fn bare_alias_variables_stay_on_original_untyped_contract() {
    for spelling in ["A", "::A"] {
        let a = parse(&format!(
            "struct C {{ int operator()(int); }}; using A=C; int f({spelling}& a) {{ return a(1); }}"
        ));
        assert_eq!(
            named(f(&a), "a").method_full_name.as_deref(),
            Some("<unresolvedNamespace>.a:<unresolvedSignature>(1)")
        );
    }
}
#[test]
fn grouped_lambda_method_and_reference_identities_change_together() {
    let a = parse("int f() { auto a=([](int x)->int { return x; }); return a(1); }");
    let name = "<unresolvedNamespace>.<lambda>0";
    assert!(a.functions.iter().any(|f| f.fullname == name));
    assert!(
        f(&a)
            .cpg
            .nodes
            .iter()
            .any(|n| n.kind == "METHOD_REF" && n.method_full_name.as_deref() == Some(name))
    );
}

#[test]
fn nearer_record_type_hides_outer_alias_and_imports_do_not_borrow_outer_aliases() {
    let a = parse(
        "struct C { int operator()(int); }; using A=C; namespace N { struct A { long operator()(long); }; struct H { A call; }; } long f(N::H& h, long x) { return h.call(x); }",
    );
    assert_eq!(
        named(f(&a), "<operator>()").method_full_name.as_deref(),
        Some("N.A.<operator>():long int(long int)")
    );
    let a = parse(
        "struct C { int operator()(int); }; struct Other { long operator()(long); }; using A=C; namespace M { using A=Other; } namespace N { using M::A; struct H { A call; }; } int f(N::H& h) { return h.call(1); }",
    );
    assert!(
        !f(&a)
            .cpg
            .nodes
            .iter()
            .any(|n| n.method_full_name.as_deref() == Some("C.<operator>():int(int)"))
    );
}

#[test]
fn inherited_field_proof_does_not_duplicate_receiver_or_argument_evaluation() {
    let a = parse(
        "struct C { int operator()(int); }; struct B { C call; }; struct D:B {}; int tick(); int f(D* d) { return d[tick()].call(tick()); }",
    );
    let f = f(&a);
    let n = named(f, "<operator>()");
    let receiver = target(f, n.id, "RECEIVER", None).unwrap();
    assert_eq!(target(f, n.id, "ARGUMENT", Some("0")), Some(receiver));
    let ticks: Vec<_> = f
        .cpg
        .nodes
        .iter()
        .filter(|n| n.kind == "CALL" && n.name.as_deref() == Some("tick"))
        .collect();
    assert_eq!(ticks.len(), 2);
    let argument = target(f, n.id, "ARGUMENT", Some("1")).unwrap();
    assert_eq!(f.cpg.nodes[argument as usize].name.as_deref(), Some("tick"));
    assert_eq!(
        f.cpg
            .edges
            .iter()
            .filter(|e| e.source == n.id && e.target == receiver && e.kind == "AST")
            .count(),
        1
    );
    let mut todo = vec![receiver];
    let mut visited = std::collections::HashSet::new();
    while let Some(id) = todo.pop() {
        if visited.insert(id) {
            todo.extend(
                f.cpg
                    .edges
                    .iter()
                    .filter(|e| e.kind == "CFG" && e.source == id)
                    .map(|e| e.target),
            );
        }
    }
    assert!(visited.contains(&argument));
}
