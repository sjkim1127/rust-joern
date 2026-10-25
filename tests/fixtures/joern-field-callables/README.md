# Field-held callable controls

`fields.cpp` is a source-only control, not a benchmark binary. Apple Clang 17
accepts it in C++20 syntax-only mode. Its independent `original.json` comes
from unchanged Joern 4.0.150 / PyJoern 4.0.150.4, using
`tests/fixtures/ddg-lambdas/capture.sc`. Source, raw capture, capture script and
projection hashes are retained in that file. No native output generated the
reference.

The complete original population has 11 METHODs and 12 non-intrinsic CALLs.
Checks cover method identity, call identity/result type/location, argument
indices and occurrence locations, receiver identity, shared argument-zero /
receiver roots, and direct AST ownership. Cases cover namespaced own fields,
`a.field`, `a->field`, nested fields, dereferenced pointer fields, indexed
pointer fields, side-effecting owner indices, scalar field arguments and an
ordinary method control. Pointer fields are indexed here deliberately; native
fixed-size arrays also have mechanical tests but encounter the pre-existing
original `<clinit>` population gap described in the report.

Capture in a separate original working directory, using absolute paths:

```sh
env -u PYTHONPATH ORIGINAL_JOERN --script ROOT/tests/fixtures/ddg-lambdas/capture.sc \
  --param target_dir=ROOT/tests/fixtures/joern-field-callables/fields.cpp > fields.log 2>&1
python scripts/joern_port/call_contract.py --call-types --operand-positions \
  --log fields.log --source tests/fixtures/joern-field-callables/fields.cpp \
  --output tests/fixtures/joern-field-callables/original.json
```

This does not assert all operand types, dispatch properties, full CPG/DDG,
C++ lifetime/exception semantics or execution equivalence. Negative Rust tests
include intentionally invalid declarations and unmodeled but valid C++; parser
acceptance must not be used as a validity verdict. See the
[measured port report](../../../docs/eval/joern_field_callable_port_2026-10-25.md).
