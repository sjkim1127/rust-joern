use rust_joern::{analyze, graph::Options};

#[test]
fn provided_type_name_is_explicitly_acknowledged() {
    let source = "int consume(); int f(){ return consume(Options{}); }";
    let mut options = Options {
        language: Some("cpp".into()),
        strict: true,
        ..Options::default()
    };
    assert!(analyze(source, "input.cpp", &options).is_err());
    options.cpp_type_names = vec!["Options".into()];
    let result = analyze(source, "input.cpp", &options).unwrap();
    assert_eq!(result.cpp_type_names, vec!["Options"]);
    assert!(result.functions.iter().any(|f| f.name == "f"));
}

#[test]
fn value_binding_does_not_become_a_supplied_type() {
    let options = Options {
        language: Some("cpp".into()),
        strict: true,
        cpp_type_names: vec!["Options".into()],
        ..Options::default()
    };
    assert!(
        analyze(
            "int f(int Options){ return Options{}; }",
            "input.cpp",
            &options
        )
        .is_err()
    );
}
