# Qualified special-member recovery in isolated input

Default C++ parsing can retain an explicit `Owner::Owner()` or `Owner::~Owner()`
body when its class declaration is absent. The owner and special-member leaf
must agree exactly; unresolved template owners, ordinary methods with missing
return specifiers and mismatched destructor names are not newly admitted.

This restores Joern 4.0.150 recovery behavior on isolated real-source slices.
It does not establish that a slice is valid standalone C++. For example, Clang
rejects a destructor definition for an undeclared class even when the reference
frontend recovers its explicit body. The parser and benchmark must distinguish
recovery, declaration completeness and source validity.

Recovery does not insert a class binding, fields, implicit `this`, hidden
initializations or destructor cleanup. Explicit body expressions keep the
existing parser/CFG behavior. Qualified constructors with initializer lists
still report unsupported effects without a complete admitted scalar-member
plan. The opt-in constructor profile continues to reject an unknown owner's
implicit initialization. References, subobjects, virtual operations, exceptions,
unwinding and complete lifetime behavior are not qualified by this change.

Regression fixtures retain unmodified source slices from the frozen C++ corpus,
input hashes and captures from unchanged PyJoern in an isolated interpreter.
Comparison covers function presence, directed CFG topology, entry/exit roles
and degeneracy; it is not full CPG/DDG equality or execution equivalence.
DecBench's production parser pin, metrics and default score populations are not
changed by updating this Rust-Joern research branch.
