# Field-held callable evidence — 2026-10-25

Baseline: `b11a55e13557db75764a593a5f74228c7baa2a4d`. Reference:
Joern 4.0.150 / PyJoern 4.0.150.4, source commit
`958fdd3d976197a783f8ade1254b43e977648f28`. This is a bounded frontend port,
not a benchmark score improvement or a claim of complete CDT support.

## Missing connection and implementation

Pinned upstream `CallTests.scala:358` (imported source row 251) declares
`A.foo` as `NNN::Callable` and calls `a.foo(1)`. The baseline retained that
field declaration inside the parser but the builder could not query it:
`foo` had no resolved method identity and only `a` was argument zero.
Original Joern instead uses the whole `a.foo` expression, once, as both
argument zero and receiver, with `NNN.Callable.<operator>():void(int)`.
The same prepared upstream source now matches the independent original CPG
contract (2 METHODs / 1 call). No function/address/sample special case exists.

`RecordFields` / `RecordField` are the parser's canonical declaration facts.
The legacy implicit-field tuples are derived from them, preserving existing
constructor and implicit-field behavior. `TranslationUnit` and borrowed
`CallBindings` transport those facts to the builder. Field types use the
existing lexical class resolver and binding type normalization, separately
from display types and explicit CV evidence. Dotted graph type names and
qualified source owners map to the same declared class identity.

A read-only member query proves the owner, ordinary record, unique own field,
qualification and declared binding type. It composes with bounded pointer,
reference, dereference and index queries. Callable signature selection still
needs one supported exact signature; owner evidence alone never guesses an
overload. Scalar field arguments use the same facts, without materializing
expressions to infer their types. The existing `CallableObject` call layout
lowers the whole callee once and shares its AST root between the two roles.
No public JSON keys, runtime dependency or DecBench integration changed.

This new query abstains on bases, unions, record-local type declarations,
templates, repeated record definitions, duplicate matching fields, CV fields
or CV owners, alias field types, qualified-member lookup and missing owner
facts. General overload resolution, access checking, aliases, ADL, virtual
lookup, factory-return field chains and implicit member callable identifiers
are not certified. Unsupported calls retain the prior unresolved path;
abstention here is not an oracle population exclusion.

## Independent evidence

The final source control and complete original reference are checked in under
`tests/fixtures/joern-field-callables/`. Unchanged original CLI output was
captured in an isolated working directory with `PYTHONPATH` removed.
All **11 METHOD identities and 12 CALL occurrences** match the scoped call
contract, including result types, occurrence positions, argument roles and
AST ownership. The frozen baseline had **7 caller-method mismatches** on
those same bytes. Normalized public CFGs independently match **10/10 functions**;
raw METHOD and public CFG populations are intentionally stated separately.
Clang's C++20 syntax-only check passes the entire final control.

A broader preliminary probe retained real fixed-size array declarations.
Original Joern additionally synthesizes `N.Holder.<clinit>` containing an
`arrayInitializer` for `array[2]`; native Rust-Joern still lacks that method.
Its full population was **not filtered** to claim parity. The final bounded
control uses indexed pointer fields and the preliminary raw logs/differences
remain under the workspace. CV/scalar-invalid call fallbacks also retain
known original-vs-native differences. Fixed-size array composition and CV /
ambiguity exclusions have mechanical Rust tests, not whole-file parity claims.

## Regression checks

| Population/check | Result |
| --- | --- |
| 1,225 frozen prepared source/output captures, default profile | 1,171 parsed / 27 rejected / 27 no methods; no changed full analyses or lost parsing |
| Same 1,225, Joern-loop profile | Same statuses; no changed full analyses or lost parsing |
| 381 imported upstream source controls | 297 parsed / 6 rejected / 78 no methods; only row 251's caller changes, matching original |
| 319 upstream C-mode controls | Complete analyses unchanged |
| Rust | 261 passed; library/release build, Clippy with warnings denied and formatting passed |
| Python | 186 run / 181 passed / 5 existing skips; scoped Black/Ruff passed |
| Reference source/JVM verification | Pinned source hashes and 128 JVM operator constants verified |

These are overlapping source/output captures, not 1,225 independent binaries
or scored functions. No benchmark output changed in that pool. Failed parsing
and absent methods remain visible; neither parser success nor call-contract
parity certifies valid producer output or execution semantics. DecBench's pin,
metrics, caches, denominators and rankings are unchanged.

All three frozen runtimes match release library SHA256
`30c207ffc5296c975ebfdccf11e59b2a5f347ebafb262ac3da6e7574674943fc`. Two independent final CLI
replays of the focused control are byte-identical.

## Reproduction/artifacts

Generated evidence: `workspace/joern-field-callable-port-2026-10-25/`.
It contains isolated original captures, baseline/candidate focused JSON,
raw full analyses and immutable runtimes for each fresh qualification run,
comparison JSON, CFG references and build/test logs. Each qualification
summary records source/runtime/wrapper/driver identities. Baseline runtimes
remain in `workspace/joern-callable-port-2026-10-25/submit-*`.

```sh
cargo build --lib
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo build --release
cargo fmt --all --check
PYTHONPATH=python:DECBENCH RUST_JOERN_LIBRARY=target/debug/librust_joern.dylib \
  PYTHON -m unittest discover -s tests -p 'test_*.py'
PYTHON scripts/qualify_corpus.py --inputs FROZEN_INPUTS \
  --library target/release/librust_joern.dylib --output NEW_RUN --jobs 2
PYTHON scripts/compare_qualification.py --baseline BASELINE_RUN \
  --candidate NEW_RUN --output NEW_COMPARISON_DIRECTORY
```

Use separate fresh runs with `--joern-loop-conditions` for that profile. The
upstream source controls use their own frozen INPUTS manifest. No upstream PR
or external maintainer message accompanies this research-fork checkpoint.
