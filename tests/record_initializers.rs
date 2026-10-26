//! c2cpg type initializer containers, not a C++ constructor/lifetime model.
use rust_joern::{
    analyze,
    graph::{Analysis, FunctionGraph, Options},
};

fn parse(source: &str, cpp: bool) -> Analysis {
    analyze(
        source,
        if cpp { "record.cpp" } else { "record.c" },
        &Options {
            strict: true,
            preprocessed: true,
            ..Options::default()
        },
    )
    .unwrap()
}
fn clinit<'a>(a: &'a Analysis, owner: &str) -> &'a FunctionGraph {
    let name = format!("{owner}.<clinit>");
    let methods: Vec<_> = a.functions.iter().filter(|f| f.fullname == name).collect();
    assert_eq!(methods.len(), 1);
    methods[0]
}
fn calls<'a>(f: &'a FunctionGraph, name: &str) -> Vec<&'a rust_joern::graph::Node> {
    f.cpg
        .nodes
        .iter()
        .filter(|n| n.kind == "CALL" && n.name.as_deref() == Some(name))
        .collect()
}
fn reaches(f: &FunctionGraph, from: u32, to: u32) -> bool {
    let mut todo = vec![from];
    let mut seen = std::collections::HashSet::new();
    while let Some(id) = todo.pop() {
        if id == to {
            return true;
        }
        if seen.insert(id) {
            todo.extend(
                f.cpg
                    .edges
                    .iter()
                    .filter(|e| e.kind == "CFG" && e.source == id)
                    .map(|e| e.target),
            );
        }
    }
    false
}

#[test]
fn record_array_modifiers_are_not_local_allocations_or_constructors() {
    let a = parse(
        "namespace N { struct H { int a[2]; int matrix[2][3]; }; }",
        true,
    );
    let f = clinit(&a, "N.H");
    let arrays = calls(f, "<operator>.arrayInitializer");
    assert_eq!(
        arrays.iter().map(|n| n.code.as_str()).collect::<Vec<_>>(),
        vec!["a[2]", "matrix[2][3]"]
    );
    assert_eq!(f.return_type, "ANY");
    assert_eq!(f.signature, "");
    assert!(
        f.cpg
            .nodes
            .iter()
            .all(|n| n.kind != "LOCAL" && n.kind != "METHOD_PARAMETER_IN")
    );
    assert!(calls(f, "<operator>.alloc").is_empty());
    assert!(reaches(f, arrays[0].id, arrays[1].id));
    for node in f.cpg.nodes.iter().filter(|n| n.kind == "BLOCK") {
        assert_eq!(node.code, "");
        assert_eq!(node.type_name.as_deref(), Some("ANY"));
    }
}

#[test]
fn explicit_initializer_precedes_array_only_fallback_and_is_evaluated_once() {
    let a = parse(
        "constexpr int bound() { return 2; } int seed(); struct H { int data[bound()] = {seed(), 2}; int after = seed(); };",
        true,
    );
    let f = clinit(&a, "H");
    assert_eq!(
        calls(f, "bound").len(),
        0,
        "c2cpg explicit initializer takes precedence"
    );
    let seeds = calls(f, "seed");
    assert_eq!(seeds.len(), 2);
    let arrays = calls(f, "<operator>.arrayInitializer");
    assert_eq!(arrays.len(), 1);
    assert_eq!(arrays[0].code, "{seed(), 2}");
    assert_eq!(calls(f, "<operator>.assignment").len(), 2);
    assert!(reaches(f, seeds[0].id, seeds[1].id));
    let lambdas = parse(
        "struct H { int a[([]() { return 2; })()] = {1, 2}; int b = ([]() { return 3; })(); };",
        true,
    );
    assert_eq!(
        lambdas
            .functions
            .iter()
            .filter(|m| m.name.starts_with("<lambda>"))
            .count(),
        1
    );
    assert!(
        lambdas
            .functions
            .iter()
            .any(|m| m.fullname == "<unresolvedNamespace>.<lambda>0")
    );
}

#[test]
fn scalar_brace_and_static_initializers_keep_declaration_order() {
    let a = parse(
        "int first(); int second(); int third(); struct H { int a = first(); int b{second()}; inline static int c = third(); };",
        true,
    );
    let f = clinit(&a, "H");
    assert!(reaches(
        f,
        calls(f, "first")[0].id,
        calls(f, "second")[0].id
    ));
    assert!(reaches(
        f,
        calls(f, "second")[0].id,
        calls(f, "third")[0].id
    ));
    assert_eq!(calls(f, "<operator>.assignment").len(), 3);
    assert!(f.cpg.nodes.iter().any(|n| n.kind == "MODIFIER"));
}

#[test]
fn nested_records_have_separate_containers_and_plain_records_have_none() {
    let a = parse(
        "struct Plain { int x; void body() {} }; namespace N { struct Outer { struct Inner { int x[2]; }; int y[3]; }; }",
        true,
    );
    let outer = clinit(&a, "N.Outer");
    let inner = clinit(&a, "N.Outer.Inner");
    assert_eq!(calls(outer, "<operator>.arrayInitializer")[0].code, "y[3]");
    assert_eq!(calls(inner, "<operator>.arrayInitializer")[0].code, "x[2]");
    assert!(a.functions.iter().all(|f| f.fullname != "Plain.<clinit>"));
    assert!(a.functions.iter().any(|f| f.name == "body"));
}

#[test]
fn existing_c_mode_record_projection_is_unchanged() {
    let a = parse(
        "struct H { int array[2]; }; int f(void) { return 1; }",
        false,
    );
    assert!(a.functions.iter().all(|f| f.name != "<clinit>"));
    assert!(a.functions.iter().any(|f| f.name == "f"));
}

#[test]
fn member_lambda_identity_uses_declaring_type_and_not_preceding_function() {
    let a = parse(
        "int before() { return 1; } namespace N { struct H { decltype(nullptr) empty; auto x = [](int a) -> int { return a; }; }; }",
        true,
    );
    let f = clinit(&a, "N.H");
    assert!(a.functions.iter().any(|m| m.fullname == "N.H.<lambda>0"));
    assert!(
        f.cpg
            .nodes
            .iter()
            .any(|n| n.kind == "METHOD_REF"
                && n.method_full_name.as_deref() == Some("N.H.<lambda>0"))
    );
    assert!(
        !a.functions
            .iter()
            .any(|m| m.fullname.starts_with("before.<lambda>"))
    );
}

#[test]
fn field_and_method_lambda_ids_follow_source_visitation_not_metadata_prescan() {
    let a = parse(
        "struct H { auto first = [](int x) -> int { return x; }; void body() { auto middle = [](int x) -> int { return x; }; } auto last = [](int x) -> int { return x; }; };",
        true,
    );
    let names: std::collections::HashSet<_> =
        a.functions.iter().map(|f| f.fullname.as_str()).collect();
    for expected in ["H.<lambda>0", "H.body:void().<lambda>1", "H.<lambda>2"] {
        assert!(names.contains(expected), "missing {expected}");
    }
}
