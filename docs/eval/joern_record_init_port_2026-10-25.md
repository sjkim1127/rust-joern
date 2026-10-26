# Record `<clinit>` port — 2026-10-25

Baseline: `9d3cb4da29eb9f1a7037632638fdcf68939772fe`. Reference: unchanged
Joern 4.0.150 / PyJoern 4.0.150.4, source revision
`958fdd3d976197a783f8ade1254b43e977648f28`.

## Owner contract and implementation

The preceding field-callable audit found an entire missing method in the
fixed-array source control. c2cpg's `astsForDeclaration` emits an initializer
AST for a declarator with an explicit initializer; otherwise array modifiers
produce an `arrayInitializer` call, even without a runtime initializer.
`astsForCompositeType` partitions member-root calls into a `<clinit>` method;
x2cpg's `staticInitMethodAst` defines its empty code/signature, ANY return,
source location, body container and static modifier. Three exact upstream
function bodies across two owners are frozen and hashed in
`tests/reference/joern-4.0.150/record-init-rules.json`.

The parser's canonical `RecordFields` now retains these initializer expressions
in declaration order. It emits a typed synthetic Function after the record's
members/nested types; the builder preserves the container's location and
metadata while using normal expression/CFG lowering for its contents.
Multidimensional bounds, explicit scalar/list/braced values, ordinary static
initializers and nested records retain separate source roots. Explicit values
take precedence over array-modifier-only ASTs, avoiding duplicate bound ASTs.
Static declarations remain in canonical record evidence, with explicit static
status; the legacy implicit-instance-field view and callable lookup exclude
them. There is no competing instance-field fact map.

Executable initializers are parsed on declaration visitation, separately from
the metadata pre-scan. This preserves counter identities when fields and member
function lambdas are interleaved. A 5-method/6-call original recovery control
certifies that case. Bounds are parsed only if the array-only fallback is
selected, so explicit initialization cannot create orphan bound-lambda methods.

A member initializer lambda uses its declaring type as the fullname owner,
rather than the preceding method/global context. Its parameter/type bindings
are restored after parsing the record. The added `<clinit>` and lambda method
bodies are retained as separate raw methods.

This is c2cpg AST/CFG compatibility: `<clinit>` must not be interpreted as an
implementation of standard C++ constructor execution, static initialization
order, implicit cleanup or exception semantics. In particular, array-modifier
ASTs are source representations, not proof of runtime evaluation. General
alias/CV/inherited callable lookup remains conservative and out of this patch.
C-mode record behavior and namespace-level initialization are not broadened.
Complex template/dependent, anonymous/nested declarator and lifetime cases
remain outside the certified ordinary-record subset.

## Independent controls and bounds

The complete compiler-valid `initializers.cpp` control matches **7 method
identities and 14 CALLs including intrinsic operators**, with result types,
argument/receiver indices and positions and direct AST ownership checked.
All **four raw container CFGs** additionally match by directed isomorphism
with node-kind/code labels (12/15/4/4 nodes). This tests topology and content,
not only counts. Public normalized CFGs match **3/3 exported functions**;
that public wrapper deliberately blacklists `<clinit>`, so this number is
separate from the raw container comparison.

The prior exact fixed-array callable source now matches its complete **12
methods / 12 non-intrinsic calls**; no missing `<clinit>` record is filtered.
Two exact imported class-lambda controls each match **2 methods / 2 calls**
including intrinsics. The latter use compiler-invalid non-static `auto`
members and establish recovery compatibility only. Original public PyJoern
exports no CFGs for either; those empty-reference comparisons remain recorded
as unavailable, **not passing topology evidence**.

Three frozen real prepared decompiler outputs (input indices 954, 180 and 80)
were independently captured with unchanged original Joern. All three added
containers match their complete call contracts. One full-file call contract
also matches; two retain existing FIELD_IDENTIFIER display-NAME differences
outside the containers. Their full raw logs and full-file differences are
retained, not discarded to claim whole-file parity. These controls do not
establish valid C++ output, execution parity or a benchmark score increase.

A supplemental compiler-valid bound-lambda probe retains an original-vs-native
fullname difference for a parenthesized lambda initializer: original CDT uses
`<unresolvedNamespace>`, while the native declared owner is `H`. Its full raw
capture/differences remain under `deferred-bounds-control`; it is not counted
as parity. The no-orphan bound-lambda invariant has a mechanical test.

## Frozen replays and tests

| Population | Measured result |
| --- | --- |
| 1,225 prepared source/output captures, default | 1,171 parsed / 27 rejected / 27 no methods; 82 changed raw analyses, adding 214 `<clinit>` methods; all existing FunctionGraph payloads unchanged |
| Same 1,225, Joern-loop profile | Same statuses/additions; all existing FunctionGraph payloads unchanged |
| Public projection for those 1,225 | Additions are exclusively blacklisted `<clinit>` methods; existing public methods/graphs are preserved |
| 381 imported upstream source controls | 299 parsed / 6 rejected / 76 no methods; only two class-lambda controls gain methods (previously no methods); both independently checked against original |
| Existing methods across all three replays | No removed or changed existing FunctionGraph payload; zero lost parsing |
| 319 upstream C-mode controls | Complete analyses unchanged |
| Rust | 268 passed; debug/release build, Clippy with warnings denied and workspace formatting passed |
| Python | 191 run / 186 passed / 5 existing skips; scoped Black/Ruff passed |

Frozen native library SHA256:
`bd109d1952f2219da650cf4c0a2e47e91fe4ec9c879efafa0fa7a35afd696fb3`.
The controls above certify bounded properties. The 214 added containers are
not all individually original-certified; complete matching of the focused
controls and preservation of existing functions must not be reported as full
CPG/DDG parity across the entire pool. These are overlapping prepared source
and output captures, not independent benchmark binaries.

Two historical Rust tests compared public PyJoern snapshots against every raw
native method. They now apply the public wrapper's existing `<` blacklist;
raw container coverage is independently checked without that filter. No
production wrapper blacklist, metric, denominator or cache policy changed.

DecBench's pin, metrics, scores and rankings are unchanged. No upstream PR or
maintainer message accompanies this research-fork checkpoint.

## Reproduction and artifacts

Generated evidence is in `workspace/joern-record-init-port-2026-10-25/`:
complete original captures, focused comparisons, raw container CFG comparison,
`corpus-container-checks.json`, fresh `complete-*` qualification directories,
`compare-complete-*`, `function-preservation-complete.json` and build/test logs.
Each frozen run records native/wrapper/driver/source hashes. Preliminary
runs and public empty-reference results remain available separately.

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
PYTHON scripts/joern_port/capture_call_rules.py --source PINNED_JOERN_SOURCE \
  --record-init --output tests/reference/joern-4.0.150/record-init-rules.json --check
```

Use separate fresh qualification directories for `--joern-loop-conditions`
and the upstream source-only manifest. Existing-method preservation is a
multiset comparison of complete serialized FunctionGraph payloads, so repeated
method identities cannot be collapsed into an accidental last-write-wins map.

Follow-up, 2026-10-26: the [grouped-lambda identity port](joern_member_lookup_2026-10-26.md)
subsequently aligns the previously recorded parenthesized lambda owner with
original FullNameProvider behavior. The limitation above describes the earlier
checkpoint; broader unary/lambda naming remains unported.
