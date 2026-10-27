# C++ pack-size expression: controlled parser and corpus audit

`sizeof...(identifier)` is a C++11 pack-size expression. It is not a normal
`sizeof(identifier)` expression and its operand has no runtime evaluation.
Previously strict parsing reported an unsupported `...` token. The parser
now recognizes exactly the parenthesized single-identifier spelling in C++
mode and preserves its entire source span and an identifier operand. The
builder uses the original Joern `<operator>.sizeOf` family; the operand remains
unevaluated and the operation's spelling remains visible in the node's code.
The parser reports `ANY` for inferred pack-size expression type because it has
no target ABI from which to choose `size_t`. This is syntax/CFG support, not
proof that the identifier denotes a valid pack; the parser is not a C++ type
checker. Pack expansion in calls and other unsupported forms remain separate.

## Original reference and fixture

Clang 22.1.8 accepts both type-pack and value-pack fixtures under C++11. For
`template<class... T> unsigned count() { return sizeof...(T); }`, unchanged
PyJoern 4.0.150.4 / Joern v4.0.150 produces one bounded one-node CFG, labels
its size operation `UnsupportedStmt`, and exports the function. The candidate
produces one bounded one-node CFG; the directed topology and entry/exit roles
match. This single fixture does not establish CPG label, DDG, effect, type or
semantic parity with Joern. See tests/cpp_sizeof_pack.rs.

## Exact-input replay

Baseline is clean source checkpoint `0d4e3b3`, executable SHA-256
`01c7c28a6a1957a0563774a19858502bb29795f5562b834a1d346c1ad85d517d`.
The final candidate executable SHA-256 is
`37c164842c8877d10a05b8bf8ace3aaeea01a7fc3195de2382f812122c982d0d`.
Both were run in strict C++ mode with `--preprocessed` on identical previously
prepared real translation units, with a 45-second per-process timeout. The
unchanged `sink` inputs act as controls. Counts are diagnostics, not functions
or benchmark score; the full diagnostic multiset was compared per input.

| Prepared input | SHA-256 | Baseline diagnostics | Candidate diagnostics | Added |
| --- | --- | ---: | ---: | ---: |
| Snappy Clang GNU++11 | `a8bbe3a7c73b3b4e7357feb7ef48227035be302a470232bb514ebc6ade852355` | 425 | 417 | 0 |
| Snappy Clang GNU++14 | `2e13eaaacc24cbfa4f10b4afa04a5b38f78bf5b908340d64e26d924a6ffd10b2` | 470 | 462 | 0 |
| Snappy Linux GCC GNU++11 | `d32de56d4b8e315ff7d7010db2c5eb55a5c2a88c0083d8df25238923ba194ace` | 432 | 418 | 0 |
| Snappy Windows MinGW GNU++11 | `8d5fe154aca5693eb20220f0ae857a785446fe24516df1fbfbf9e569d4557f5a` | 416 | 402 | 0 |
| Ninja Clang C++17 | `702c714a94f74856515a8c77a19ab6cef5b840b2b0e0c02f207586ba82a26a14` | 604 | 580 | 0 |
| Snappy sink Clang GNU++11 | `51960ff1da75919e951e80e840b8e7ebf7a95006d84e4026fd530f989600f1c9` | 2 | 2 | 0 |
| Snappy sink Linux GCC GNU++11 | `7fd6e23fe75250360a41a8ba935f8df9a6a6cd6d40b29b05fb31febd9317009a` | 2 | 2 | 0 |
| Snappy sink Windows MinGW GNU++11 | `bfd4c26e05a8eea005e07066fad6f3a0a089a5f0f765aaf21423e6a8540010a4` | 3 | 3 | 0 |

Every input remained a strict rejection: other unsupported constructs are not
suppressed. No whole-TU CFG success, cross-tool parity, benchmark score or
leaderboard improvement follows from these diagnostic reductions. Full local
records are in ignored `workspace/sizeof-pack-final-audit.json`; the dataset
preparation profiles are in `sjkim1127/joern-c-cpp-corpus`. No DecBench pin,
metric or upstream PR was changed.
