# Divergences from Joern

Rust Joern targets Joern 4.0.150 / PyJoern 4.0.150.4. This log records each
intentional difference in observable output: when it was made, why, which
graphs it affects and how to restore the reference behavior. Add an entry, newest
first, in the change that introduces a divergence. Fixes that restore parity
belong in regression fixtures, not here.

## Bounded callable-object overload evidence

**Recorded:** 2026-10-25, research fork follow-up; no upstream PR or DecBench pin update.

**Joern:** CDT's nonclosure class-call branch can resolve `operator()` through
implicit conversions, promotions, defaults, CV/ref ranking and template rules.

**Rust Joern:** an explicitly declared own `operator()` proves the shared
callee/base/receiver shape independently of selecting an overload. A resolved
signature/result requires exact supported argument-type evidence and one unique
signature. Unsupported conversions, CV/ref argument constraints or ambiguous
selection retain `Class.<operator>():<unresolvedSignature>` with `ANY`, even
where CDT resolves a signature. The call and all executable operands remain.
Qualified/inherited/aliased callable lookup remains bounded separately.
The [own-field follow-up](eval/joern_field_callable_port_2026-10-25.md) extends
this evidence to unique ordinary fields; bases, unions, CV/alias fields and
ambiguous declarations keep the previous unresolved path. That path can differ
from CDT even for valid input; there is no implicit validity/eligibility claim.

**Why:** arity or a coincidentally named global function is not overload proof.
This is conservative missing type/binding information, not a syntax error or
permission to drop a call, shrink evaluation populations, or claim full parity.

**Affects:** CPG call identity/result types and dependent DDG summaries outside
the frozen supported controls. There is no runtime/JVM dependency and no option
that implements full CDT overload resolution; immutable consumers keep their
existing library pin. Joern's const-object untyped path is preserved rather
than treated as a new semantic policy.

## Invalid explicit-destructor call diagnostics

**Recorded:** 2026-10-25, fork research follow-up; no upstream PR or DecBench pin update.

**Joern:** the frozen declared control `p->~Object(tick())` still exports method
`f` and a recovered graph in 4.0.150. Clang rejects the call because a destructor
accepts no arguments. Reference recovery does not establish source validity.

**Rust Joern:** an explicit destructor-id is one member name with its receiver,
not a field named `~` followed by a separate constructor/function call. Recognized
destructor-ids require an empty call. Arguments or a missing call produce an
unsupported diagnostic; strict mode rejects it while permissive output retains
the diagnostic. Complete supported controls and the motivating real source have
original-reference CFG coverage, roles and topology regressions.

**Why:** neither a split callee nor permissive reference recovery should silently
qualify an unsupported destructor invocation. This is bounded call preservation,
not full C++ validation or hidden lifetime/exception modeling.

**Affects:** member-call CPG identity, receiver operands and strict acceptance of
these malformed calls. Other malformed forms keep their existing recovery.

**Reference behavior:** no option restores the split-name fallback or suppresses
this diagnostic. Consumers requiring old immutable behavior retain their pinned
library; DecBench's production pin and cache generations remain unchanged here.

## Operator-template recovery in incomplete pseudocode

**Recorded:** 2026-10-22, follow-up to [PR #3](https://github.com/Noelo-Lab/rust-joern/pull/3).

**Joern:** complete declared controls for `operator!=<>(a,b)` retain calls,
returns and comma/short-circuit loop structure. On incomplete ABI pseudocode,
the original CDT frontend may recover different problem-expression structure.

**Rust Joern:** recognize the operator-function-id and its template suffix
before expression recovery checks, preserving executable operands and returns.
This restores the declared controls, including one-node CFG degeneracy. It
does not attempt to reproduce every CDT recovery path on undeclared or
malformed types. In the fixed C++ qualification input audit, one previously
non-isomorphic large pseudocode CFG remains non-isomorphic after this fix;
its calls are no longer discarded into problem expressions. The input is not
qualified as complete valid C++, and this is not certified reference parity.

**Why:** discarding a call or enclosing return to make an incomplete input's
graph resemble reference recovery would conceal an expression-parser defect.
Caller validation and declaration/dialect evidence remain necessary.

**Affects:** CPG calls/returns, CFGs and dependent DDGs for operator-template
expressions previously recovered as problems. A template argument's scope
separator must not rename the callee to that argument's leaf type.

**Reference behavior:** no option restores the dropped-call recovery.
`joern_loop_conditions` controls the separate constant-true loop policy below;
it does not certify arbitrary pseudocode recovery. Existing DecBench pins and
metric profiles are unchanged by this frontend patch.

## Constant-true loop heads lower like `for (;;)`

**Introduced:** 2026-10-14, [PR #2](https://github.com/Noelo-Lab/rust-joern/pull/2).

**Joern:** `while (1)` and `while (true)` lower with a CFG condition node and an
exit edge to the loop's successor. `for (;;)` has neither.

**Rust Joern:** a `while` or `for` condition that is `true` or a nonzero integer
literal keeps its AST node and `CONDITION` edge, but has no CFG node or exit
edge. The loop takes the `for (;;)` lowering, including Joern's order-based
slots: a braceless body that fills the condition slot keeps its exit edge, as
in `for (;;) n++;`.

**Why:** decompilers emit `while (1)` (angr, IDA, r2dec), `while (true)` (Binary
Ninja, Ghidra, dewolf, Kuna) and `while ( 2 )` (IDA) where source mostly has `for (;;)`,
so identical control flow scored differently in DecBench GED. In every tenth
artifact of `full_run_address_2026-09-11`, 3,949 of 50,856 functions with such
loops changed; all matched a textual rewrite of their loop heads to `for (;;)`.

**Affects:** raw and normalized CFGs, and the reaching definitions and DDGs
derived from them. ASTs are unchanged. `do { } while (1)` is not affected.

**Reference behavior:** `joern_loop_conditions` in `Options` and Python, or
`--joern-loop-conditions` on the CLI. Original-reference parity tests,
`compare_pyjoern.py`, `compare_native_corpus.py` and `compare_ddg_pyjoern.py`
request it. DecBench and its shim use the default, so `compare_decbench.py`
reports these loops as differences, and DecBench's GED cache needs a new
`cache_version`.

## Original exporter stack overflows are not reproduced

**Recorded:** 2026-10-09 CFG parity evaluation.

**Joern:** original PyJoern returns no functions for three prepared inputs,
NuttX `lib_wcwidth.i` and Cleanflight/Crazyflie `arm_common_tables.i`. Its
recursive CFG DOT projection raises `StackOverflowError` after graph
construction.

**Rust Joern:** returns the graphs, which match an iterative recovery of the
original exporter. See [Original exporter failures](eval/cfg_parity.md#original-exporter-failures).

**Affects:** the five corpus cases that use those inputs.

**Reference behavior:** none; comparisons report the empty original exports as
differences.

## 2026-10-24: opt-in scalar constructor initialization (local prototype)

The experimental `cpp_constructor_initializers` CFG-only profile retains proved
explicit scalar member initializations in declaration order before the body.
Original Joern 4.0.150 can omit constructor initializer effects; an empty-body
CFG is therefore not the parity target for this opt-in profile. Ordinary options
remain unchanged and still diagnose unsupported initializer syntax. This has
not changed the DecBench parser pin or metrics. See
[the profile contract](cpp-constructor-initializers.md) for the admitted subset,
normal-completion-only scope and checkpointed corpus qualification driver.
