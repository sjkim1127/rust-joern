# Independent opt-in context and constructor validation

Base: `9f8cad170d6b6883fe08627fa524ecb28128380d` (release SHA-256
`407537b4402f7a374b7295d8b1edf093340096107ab1f7da8e73acb060d6ee33`).
Candidate release SHA-256:
`c305264cea566af51b577ce2552e7a6df86c1c5a3fbb56343927dbb53a375d02`.

With both new options absent, strict analysis of eight prepared Snappy/Ninja
TUs returned the same failures and exactly the same diagnostic multisets as
base. This is not evidence of successfully parsing those inputs. Separately,
full CLI responses were identical for twelve inputs: six produced output and
six were rejected by both. The inputs include eight C++ regression fixtures
and four Clang C11 preprocessed Zlib TUs. These are bounded checks; they do not
prove global default compatibility. Local full records are retained in
`workspace/constructor-default-replay.json` and
`workspace/default-graph-comparison.json`.

The opt-in initialization-order fixture compiles under Clang 22 C++11. Its
runtime control printed `123 7 8`: field initializers execute in declaration
order and then the body, despite reverse source-list order. The candidate's
synthetic CFG includes the same initializer-call order in tests; this is a
focused control, not execution parity for arbitrary programs. Unchanged
PyJoern 4.0.150.4 / Joern 4.0.150 exports the fixture constructor as a one-node
body-only CFG with `body()` and omits both initializer calls. The opt-in CFG
intentionally differs from that reference; see `docs/divergences.md`.

Two real Snappy source excerpts reject without type-name context and produce a
function when `CompressionOptions` is supplied. The supplied visibility has
not been proved for the exact enclosing source TU: these are diagnostic probes,
not qualified scoring evidence. The complete Snappy TUs remain unqualified.
No DecBench metric, backend pin or upstream benchmark population changed.
