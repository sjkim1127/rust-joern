# Original Joern callable-object controls

Source controls only, not collected benchmark programs. The ordinary portion
of `callables.cpp` passes Apple Clang 17 `-std=c++20 -fsyntax-only`; the final
two rows deliberately use an undeclared type to model incomplete pseudocode.
The whole file is not claimed to compile or execute.

Original: unchanged Joern v4.0.150 bundled with PyJoern 4.0.150.4. Capture in
an isolated directory, outside the replacement package's import path:

```sh
env -u PYTHONPATH /path/to/original/joern-cli/joern \
  --script /path/to/repo/tests/fixtures/ddg-lambdas/capture.sc \
  --param target_dir=/path/to/repo/tests/fixtures/joern-callables/callables.cpp \
  > original.log
python3 /path/to/repo/scripts/joern_port/call_contract.py \
  --call-types --operand-positions --log original.log \
  --source /path/to/repo/tests/fixtures/joern-callables/callables.cpp \
  --output /path/to/repo/tests/fixtures/joern-callables/original.json
```

The frozen reference checks 26 METHOD identities and 25 call occurrences,
including CALL result types, argument/receiver occurrence locations, shared
base/receiver identity and direct AST ownership. Same-spelled `tick()` calls
retain separate source positions and argument slots. It is independent of
candidate output. Raw original logs are retained in
`workspace/joern-callable-port-2026-10-25/original/`.

Coverage: direct/grouped/dereferenced/indexed/nested callable invocation,
namespaced and virtual functors, exact overloads, zero/multiple arguments,
explicit `operator()` calls, global-function shadowing, unresolved argument
types, and Joern's const-object untyped fallback.

The port preserves c2cpg's distinction between METHOD `Class.():signature`
and call `Class.<operator>():signature` (or explicit-member
`Class.operator ():signature`). Source lookup keeps its own binding key.
CV and ref-qualified overload selection, implicit conversions, defaults,
templates, field-held callables, inherited `operator()`, and general aliases
are not certified by these controls. See `docs/divergences.md` for the
conservative signature/result fallback. Operand types, dispatch properties,
complete DDG and program execution remain outside this contract.
