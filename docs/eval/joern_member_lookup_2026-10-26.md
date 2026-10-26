# Member lookup and grouped lambda identities — 2026-10-26

Baseline: `74415de90f2f3e4646582d3afea2b8c1a449ddb9`. Reference:
Joern 4.0.150 / PyJoern 4.0.150.4, source revision
`958fdd3d976197a783f8ade1254b43e977648f28`. This is bounded C++ frontend
support, not complete CDT lookup or a benchmark ranking/quality claim.

## Canonical evidence and lookup

`TypeAlias` retains the existing display/ABI spelling and separate immutable
field evidence, including effective CV qualification. Qualified declaration
keys and the legacy name index share that owner. Field targets are frozen in
the declaring lexical scope; namespaces and local alias declarations do not
rebind previously declared fields. Lookup checks aliases and nominal records
at each lexical depth before moving outward. Unknown imports, conflicting
aliases and unproved targets abstain instead of borrowing a same-named type.
The existing ABI/display alias path is preserved, including its unsupported
cases; this is not a general type-system rewrite.

Ordinary records retain a proved single public, non-virtual base. A visited
set bounds field/method traversal; nearer fields and methods stop base lookup.
Callable fields and inherited `operator()` can use that chain. Ordinary
inherited method calls require exact supported argument evidence and a
non-static/non-virtual declaration. A typed resolved-call view keeps the
original declaration distinct from c2cpg's receiver-based CALL identity:
`D.method:int(int)` may refer to a declaration on `B`. This does not assert
whole-program callgraph or interprocedural DDG equivalence.

Read-only receiver evidence carries CV independently of cleaned type spelling.
Owner CV propagates to ordinary fields; `mutable` suppresses that inherited
qualification. Explicit field/alias CV remains. Original c2cpg's qualified
field path is preserved: a const/volatile class field can remain an untyped
named field call with one base/receiver, rather than being incorrectly forced
through the nonqualified class-call branch. Bare typedef/using variables
remain on the original untyped path; a field's alias evidence is not a reason
to normalize every variable into an underlying class.

No proof query lowers an expression. Existing shared-callee AST construction
retains receiver/index/argument occurrences without duplication.

## Parenthesized lambda naming

FullNameProvider resolves an IASTUnaryExpression parent from its operand code;
its lambda sanitizer uses `<unresolvedNamespace>` when that parent spelling
contains a lambda. Direct bracketed-primary lambda operands now update their
canonical METHOD/binding identity and Closure reference target together,
before subsequent binding use. Nested capture parent references are updated
with the same identity. This restores the previous compiler-valid grouped
lambda probe instead of applying a string rewrite in graph serialization.

The source rule is bounded to the demonstrated grouped-primary case. This is
not a complete port of every unary/cast/template-dependent lambda naming rule.
Four exact upstream bodies across two owners are frozen in
`tests/reference/joern-4.0.150/member-lookup-rules.json`.

## Measured original-reference controls

All three checked-in sources in `tests/fixtures/joern-member-lookup/` pass
Clang C++20 syntax checking. Complete call contracts cover **33 METHOD
identities / 26 non-intrinsic CALLs**: lookup 23/21, lambdas 8/4, volatile 2/1.
They include result types, occurrence positions, argument/receiver roles and
AST ownership. Four lambda METHOD_REF targets also match an independently
frozen original reference and name actual native methods.

On identical final lookup bytes the baseline had **16 differing caller-method
contracts**; the candidate has none. Lambda naming accounted for three missing
and three extra METHOD identities in the baseline (three renamed methods,
not six independent closures); the candidate has none. Frozen original logs
and baseline/candidate JSON are retained separately.

Independent public CFG projection matches **24/24 functions** for lookup and
lambda controls (21 + 3); the volatile control matches **1/1**, for **25/25** total. Public
projection has its existing duplicate-name/export rules and blacklist, so this
count is distinct from the raw method population. Matching calls/CFGs does not
certify every operand type, all CPG properties, DDG or execution semantics.

## Fresh regressions and limits

| Check | Result |
| --- | --- |
| 1,225 overlapping prepared source/output inputs, default | 1,171 parsed / 27 rejected / 27 no methods; zero changed full analyses, zero parsing loss |
| Same pool, Joern-loop profile | Same statuses; zero changed full analyses, zero parsing loss |
| 381 imported upstream source controls | 299 parsed / 6 rejected / 76 no methods; zero changed full analyses, zero parsing loss |
| C-mode source controls | All 319 complete analyses unchanged |
| Rust | 278 passed; debug/release builds, Clippy with warnings denied, formatting passed |
| Python | 196 run / 191 passed / 5 existing skips; scoped Black/Ruff passed |

The final frozen native library SHA256 is
`feff19defde9125ae7f21f07cb400bc388889e5dfab5b251db879c20c2856a1f`. All three release
controls match their original call contracts and independently replay twice
with byte-identical output; hashes are also recorded in `SUMMARY.json`. These populations are overlapping prepared captures and
source-only upstream controls, not thousands of independent binaries. No
changed real-corpus output was observed, so this is regression evidence and
bounded new support, **not a measured DecBench score improvement**.

Remaining exclusions include multiple/virtual/private/protected inheritance,
base aliases, qualified-member/ADL/template lookup, class-local type aliases,
scoped import reasoning, arbitrary CV pointer/pointee distinctions, static
callable fields, function-pointer fields/conversions, complete member-function
CV/ref overload ranking, and general inherited virtual/static method binding.
Unproved inheritance edges and field/alias targets retain the prior unresolved
behavior. Access checking, source validity and evaluator eligibility
remain separate; some negative Rust controls deliberately contain invalid C++.
Two former refusal-only tests now exercise private/virtual bases because the
public ordinary cases are positively certified by original-reference controls.

DecBench's parser pin, adapters, metrics, caches, denominators and scores remain
unchanged. No upstream PR or maintainer message accompanies this research-fork
checkpoint.

## Reproduction and artifacts

Generated evidence: `workspace/joern-member-lookup-2026-10-26/`. It retains
original raw captures, complete baseline differences, focused references,
CFG captures, fresh immutable `final-*` runtimes/full analyses,
`compare-final-*`, and build/test logs. Preliminary captures remain separate.

```sh
cargo build --lib
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo build --release
cargo fmt --all --check
PYTHONPATH=python:DECBENCH RUST_JOERN_LIBRARY=target/debug/librust_joern.dylib \
  PYTHON -m unittest discover -s tests -p 'test_*.py'
PYTHON scripts/joern_port/capture_call_rules.py --source PINNED_JOERN_SOURCE \
  --lookup --output tests/reference/joern-4.0.150/member-lookup-rules.json --check
PYTHON scripts/qualify_corpus.py --inputs FROZEN_INPUTS \
  --library target/release/librust_joern.dylib --output NEW_RUN --jobs 2
PYTHON scripts/compare_qualification.py --baseline BASELINE_RUN \
  --candidate NEW_RUN --output NEW_COMPARISON_DIRECTORY
```

Use separate fresh runs for `--joern-loop-conditions` and the upstream source
manifest. Original captures use the unchanged CLI in an isolated directory
with `PYTHONPATH` removed; source/capture/projector/raw-log hashes stay with
each reference.
