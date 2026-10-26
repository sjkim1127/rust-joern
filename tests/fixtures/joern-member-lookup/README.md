# Bounded member lookup and grouped lambdas

These complete sources pass Apple Clang's C++20 syntax-only check. They are
source controls, not benchmark binaries or execution-equivalence evidence.
References come from unchanged Joern 4.0.150 / PyJoern 4.0.150.4 in an isolated
working directory, using `tests/fixtures/ddg-lambdas/capture.sc` with
`PYTHONPATH` removed. Source/script/raw-log hashes are retained.

- `lookup.cpp`: 23 methods / 21 non-intrinsic calls. Cases cover public single
  inheritance and a multi-level chain, inherited callable objects, own-name
  hiding, exact inherited method signatures and receiver identities, typedef /
  using alias chains, namespace and local alias isolation, const ownership,
  const aliases and mutable fields. Bare alias variables remain untyped as in
  original c2cpg. Effectful indexing and arguments check distinct occurrences
  and one shared callee/base/receiver root.
- `lambdas.cpp`: 8 methods / 4 non-intrinsic calls. Plain, grouped and immediately
  invoked closures distinguish declared versus unresolved namespace identities.
  The explicitly initialized array does not create an unused bound-lambda
  method. Four METHOD_REF targets are separately frozen in
  `lambda-bindings-original.json` and checked against actual method identities.
- `volatile.cpp`: 2 methods / 1 call, preserving original c2cpg's untyped
  volatile field call path.

All METHOD identities and call occurrences are compared; no failing method is
filtered. Contracts check CALL result types, name/fullname, positions, argument
indices, receiver identity and direct AST ownership. This does not certify all
operand types, dispatch/access attributes, full CPG/DDG or C++ runtime behavior.
The volatile control has its own reference; existing default projector profiles
are unchanged.

```sh
python scripts/joern_port/call_contract.py --call-types --operand-positions \
  --log ORIGINAL_LOG --source SOURCE --output REFERENCE_JSON
```

The [report](../../../docs/eval/joern_member_lookup_2026-10-26.md) records the
bounded algorithm, intentional abstentions, independent CFG checks and fresh
full-input regression replays. The source-rule profile is
`capture_call_rules.py --lookup` on pinned upstream source.
