# Record initializer containers

These are source/CPG compatibility controls for Joern 4.0.150 / PyJoern
4.0.150.4, not C++ execution or benchmark-quality goldens.

- `initializers.cpp`: Clang accepts the complete C++20 control. Complete original
  population: 7 methods, 14 calls including intrinsic operators, four `<clinit>`
  containers. `original.json` freezes call identity/result types, operand roles,
  occurrence positions and direct AST ownership. `original-container-cfg.json`
  independently freezes every raw container CFG for kind/code-labeled directed
  topology comparison. `<clinit>` is not discarded from these contracts.
- `fixed-array-fields/`: the previous field-callable control's exact fixed-array
  bytes, including its previously missing `<clinit>`. All 12 original methods
  and 12 non-intrinsic calls are now compared. This does not claim all field
  operand type attributes are equal.
- `member-lambda/` and `nested-member-lambda/`: unchanged source bodies from the
  pinned upstream `AstCreationPassTests.scala` at lines 162 and 204. Origins and
  source hashes are retained in `upstream-origins.json`. Both methods and both
  calls in each complete original capture are compared. These use `auto` as a
  non-static member type: they are CDT recovery controls, not compiler-valid C++.

- `ordered-lambdas/`: source-only recovery control with field/member-function/field
  lambdas interleaved. All 5 methods and 6 calls preserve original visitation
  identities. Like the upstream member-lambda cases, its non-static `auto`
  members do not establish compiler validity.

All references come from unchanged original CLI captures, never Rust output.
Source/script/raw-log hashes are retained. The existing capture script is
`tests/fixtures/ddg-lambdas/capture.sc`; invoke it from an isolated original
working directory with `PYTHONPATH` removed and absolute paths. Project its
complete captures with:

```sh
python scripts/joern_port/call_contract.py --call-types --operand-positions \
  --include-intrinsics --log ORIGINAL_LOG --source SOURCE --output original.json
```

The fixed-array callable control retains the earlier non-intrinsic profile.
The raw CFG snapshot selects all original `<clinit>` methods before comparison,
retaining their complete CFG node/edge populations; arbitrary node IDs are
compared by labeled graph isomorphism. These checks do not certify full CPG
attributes, DDG, constructor timing, implicit cleanup or exception unwinding.

See the [port report](../../../docs/eval/joern_record_init_port_2026-10-25.md)
for real prepared-output controls, full regressions, exclusions and reproduction.
