# Callable-object port — 2026-10-25

Baseline: `745da8f2402373a6b0d665328ddc5053b9580a26`. Reference: pinned
Joern v4.0.150 / PyJoern 4.0.150.4, source commit
`958fdd3d976197a783f8ade1254b43e977648f28`.

## Scope and canonical owners

The nonclosure `ICPPClassType` branch of `astForCppCallExpression` is now
consumed for declared own callable objects on the supported shapes. Certification
currently covers the untemplated controls below. Direct, grouped,
dereferenced and indexed object bindings share one callee AST as argument zero
and receiver. The proof query reads immutable binding facts; it does not
execute/lower an expression to infer its type.

The object owner and overload selection are separate facts. A known object can
have `Class.<operator>():<unresolvedSignature>` / `ANY` if argument evidence is
incomplete. Signature/result selection requires one unique supported exact
signature; arity alone is insufficient. Nested scalar-call arguments use
bounded declaration evidence. CV-erased arguments, string decay, reference
ranking, defaults and conversions do not receive guessed resolved signatures.

Parser METHOD identity for `operator()` now follows FullNameProvider's removal
of the binding's `operator ` prefix: `Class.():signature`. Internal source lookup
retains its distinct `binding_name`. Explicit member invocation uses c2cpg's
`Class.operator ():signature` and `operator ()` call name. This is the
`operator()` slice, not a complete port of every overloaded-operator identity.

Parameter/local CV evidence is transported separately from c2cpg's cleaned
display types. Joern's const-object untyped path is preserved. Ref-qualified
selection remains conservative. Reference-owner trailing whitespace is
normalized at existing lookup; a nearer value/capture binding cannot resolve
to a coincidentally named outer function.

Five exact original source bodies across two owners are frozen under
`tests/reference/joern-4.0.150/callable-rules.json`. The source/JVM remain
development references; runtime dependencies and public JSON keys are unchanged.

## Independent oracle and checks

`tests/fixtures/joern-callables/original.json` was generated from unchanged
original CLI CPG output, never native output. All source/log/capture/projector
hashes are retained. It checks **26 METHOD identities and 25 call occurrences**:
names/fullnames, result types, argument and receiver occurrence locations,
shared AST identity and direct child ownership. Same-spelled `tick()` operands
cannot swap argument positions undetected. Public normalized CFG comparison
also matches **19/19 exported functions**, with no missing/extra functions.

The valid source prefix passes Apple Clang 17 C++20 syntax checking. The final
two rows deliberately contain an unknown type. This is not execution parity,
whole-file C++ validity, full operand-type equality or complete DDG parity.
The [fixture guide](../../tests/fixtures/joern-callables/README.md) reproduces
original capture and defines supported/unsupported scope.

| Final replay | Result |
| --- | --- |
| Frozen 1,225 prepared inputs, default | 1,171 parsed / 27 rejected / 27 no methods; zero complete-analysis changes or parsing losses |
| Same pool, Joern-loop profile | Same statuses and zero complete-analysis changes, independently captured |
| 381 upstream source controls | Same 297 parsed / 6 rejected / 78 no methods; one C++ METHOD identity correction |
| C-mode controls | All 319 full analyses unchanged |
| Rust | 256 tests passed; library/release build, Clippy with warnings denied and formatting passed |
| Python | 185 run / 180 passed / 5 existing skips; scoped Black/Ruff passed |

All frozen final runtimes match release library SHA256
`9ba7ac9c7c60e80ff83c6c7ddf1425f59e1325471482bc967f58ba1542cfd661`.
Two independent CLI replays of the callable control are byte-identical.
The baseline had 16 common caller-method contract mismatches plus eight
misnamed METHOD identities (eight missing/eight extra comparison records,
not sixteen additional methods); the final scoped comparison has zero.

The 1,225-input pool contains overlapping prepared source/output captures,
not independent binaries/scored functions. No newly supported caller was observed changing output there, so unchanged
output is regression evidence, not a corpus quality/score improvement. The upstream controls are
source-only tests, not 381 benchmark programs or translated Scala assertions.

The one upstream change is the declaration identity in CallTests.scala at
line 358: `NNN.Callable.operator():void(int)` becomes
`NNN.Callable.():void(int)`. All other full-analysis bytes are unchanged after
accounting for that field. An independent original capture confirms the new
METHOD identity. The same example's field-held callable `a.foo(1)` remains an
explicit, pre-existing gap; it is not claimed fixed by changing its METHOD ID.

## Limits and next owner

The [divergence ledger](../divergences.md) records conservative callable
signature selection where CDT can resolve a conversion/default/ref ranking.
Field-held/captured callables, inherited operators, general aliases, ADL,
SFINAE, template instantiation and full CV/ref overload ranking remain bounded.
Next is canonical record/member type evidence for field-held callables; a
display-name substitution would not fix that owner.

Full local evidence is under `workspace/joern-callable-port-2026-10-25/`.
DecBench's pin, source, scoring/cache policy and published populations are
unchanged. No new ranking, full C++ completion rate or upstream PR is claimed.
