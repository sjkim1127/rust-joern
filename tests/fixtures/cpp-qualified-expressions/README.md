# C++ qualified expression controls

Six header-free C++17 inputs cover template-qualified statement/return/nested
calls, an explicitly qualified member `operator[]`, and conditional/short-circuit
and loop/break control around those calls. They were accepted by Clang 20 and
22 using `-fsyntax-only`. They do not execute or require linking.

The `.pyjoern.json` files were captured with unchanged installed PyJoern
4.0.150.4 / Joern v4.0.150 in separate interpreters and temporary working
directories with `PYTHONPATH` removed. Original parse flags, source hashes and
reference hashes are recorded in `provenance.json`. The native candidate was
not used to generate expected graphs.

Comparison checks full selected function coverage (17 functions, including
prototypes), directed topology, entry/exit roles and degeneracy. Statement
attribute/effect validation is separate: the Rust integration tests verify
call identities, arguments, receiver evaluation and CFG ordering. Topology
agreement does not certify full expression semantics or C++ validity of
arbitrary producer output.
