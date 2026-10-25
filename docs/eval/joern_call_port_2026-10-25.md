# Call AST port qualification — 2026-10-25

Status: bounded C/C++ call-operand port, **not complete CDT equivalence or a
DecBench score improvement**. Baseline is `397ce6d6b9af9cf7ecf1c381827907ffe66260a7`.

## Implementation and source ownership

Seven exact original function bodies across c2cpg's expression creator,
its call-AST helper and x2cpg's argument-index helper are preserved in
`tests/reference/joern-4.0.150/call-rules.json`. The source commit is
`958fdd3d976197a783f8ade1254b43e977648f28` (Joern v4.0.150, Apache-2.0).
The original source and installed JVM constants/jars were reverified live.

`src/joern_calls.rs` directly translates operand placement into typed call
layouts consumed by the canonical builder:

- Named calls have no receiver/base AST.
- Pointer and closure calls evaluate one receiver, without argument zero.
- Resolved nonvirtual members have a base at argument zero; explicit virtual
  declaration evidence additionally attaches a receiver to that same root.
- Unresolved members and unresolved expression callees use one shared
  base/receiver AST. Explicit arguments start at index one.
- Unresolved source calls receive the original unresolved namespace/signature
  identity with syntactic arity. Generated intrinsics retain canonical IDs.

Roots come from direct AST edges, rather than the first allocated node ID.
Ambiguous/missing receiver roots produce a diagnostic. Receiver effects are
lowered once before explicit arguments; short-circuit bypass remains intact.

The parser exports its existing explicit declaration/type-name evidence to
borrowed `CallBindings`; raw guessed parameter spellings are not treated as
known types. Incomplete member lookup on a known owner/carrier, including
qualified members, inheritance and ambiguous overloads, retains the previous
base-only path and absent binding. Lack of Rust support is not asserted to be
CDT's `IProblemType`. This is a bounded binding adapter, not a port of CDT's
semantic engine or a complete implementation of generic `createCallAst`.

## Independent original evidence

Unchanged installed PyJoern 4.0.150.4 / Joern v4.0.150 captured raw CPGs in
isolated original CLI processes. Source bytes are not sanitized. The frozen
contracts retain source, raw-log, capture-script and projector hashes.

| View | Population | Result |
| --- | --- | --- |
| C++ raw call contract | 18 methods, including prototypes/lambda; 25 calls | All checked properties match; baseline differed on 7 methods |
| C raw call contract | 5 methods / 7 calls | All checked properties match before and after |
| Original PyJoern normalized C++ CFG view | 16 exported functions | 16 match; no missing/extra functions or diagnostics |
| Original PyJoern normalized C CFG view | 5 exported functions | 5 match; no missing/extra functions or diagnostics |

The raw and normalized method counts are different views: PyJoern applies its
export-name/filter policy. The projection compares call identity/location,
argument edge indices, receiver identity, shared-root identity and the
multiset of direct AST children. It rejects ambiguous populations and same-
spelled cloned receiver roots. It does not claim full node type, signature,
dispatch/order-property, DDG or execution equivalence. The controls include
deliberately unresolved decompiler-like text; they are not new corpus programs
or a claim that every input is valid compilable C++.

## Full prepared-input regression audit

The frozen 1,225-input pool contains overlapping prepared source/output
captures, all replayed in C++ mode. It is **not 1,225 binaries or independent
scored functions**. Fresh default and Joern-loop captures preserve each input,
library/wrapper/driver hashes, diagnostics and full analysis output.

Final counts and exact release-library identity are recorded in local
`workspace/joern-call-port-2026-10-25/SUMMARY.json` and its `AUDIT-SUBMIT-*.json`
files. The checked-in compact result table below is filled from those audits.

| Final capture | Parsing/population | Observed full-analysis delta |
| --- | --- | --- |
| Real prepared pool, default | 1,171 parsed / 27 rejected / 27 no methods, unchanged | 862 inputs changed: 6,273 previously absent call identities and 190 shared-root receiver edges |
| Same pool, Joern-loop profile | Same 1,225 inputs and statuses | Same delta counts; independently captured/audited |
| Upstream source controls | 297 parsed / 6 rejected / 78 no methods, unchanged | 11 C++ inputs changed: 14 identities and 2 receiver edges |
| C-mode upstream controls | All 319 full analyses unchanged | No observed C regression in this control population |
| All three audits | Zero unexplained deltas | Normalized CFGs, nodes/text, other edges and diagnostics preserved |

The counts are occurrences in overlapping captures, not unique program facts;
the default and loop profiles must not be summed into a larger corpus.
Candidate release-library SHA256:
`dfa51eeafb204eb207077c0df164b075e730914daccb12182aadc784f29daca6`.
All final frozen runtimes match that exact library. Two-process C/C++ control
replays are byte-identical (`DETERMINISM.json`); this is not a two-run audit of
every corpus input.

The delta audit validates all checkpoint/source hashes, then checks every
changed full analysis. Only previously absent unresolved call identities and
new receiver edges to an existing unique argument-zero AST root are allowed.
After accounting for those changes, full analyses must equal baseline,
including normalized CFGs, node identities/text, other edges and diagnostics.
Both default and compatibility profiles are audited independently.

An earlier candidate incorrectly overwrote synthetic `new` identities; the
full-input audit caught it. That candidate was rejected. The fix preserves the
canonical intrinsic owner and has scalar/array/object allocation regressions.
Preliminary captures/failures are retained locally, not presented as final.

## Checks and limits

- Rust: 248 tests passed; debug library, release CLI/library, Clippy with
  warnings denied, and formatting passed.
- Python: 182 run / 177 passed / 5 existing skips. Original call-contract,
  source-fragment identity and ambiguity/multiplicity guards are included.
- Original source/JVM verification, direct-port source snapshot check,
  deterministic operator generation and scoped Black/Ruff checks passed.

Remaining binding work includes inherited virtual/override evidence,
qualified lookup, member function-pointer/callable-class/operator overload
resolution and richer
callee return-type facts. Existing limitations retain their boundary; they
are not reported as newly resolved. Type/dispatch/signature serialization and
full-program execution parity were not added or measured.

DecBench's source, pinned Rust-Joern dependency, metrics, caches, population
and published inputs are unchanged. No re-score, new ranking or upstream PR
is claimed. This patch is submitted only to the existing research fork.
