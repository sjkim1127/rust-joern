# Fifteen isolated C++ source failures versus original Joern — 2026-10-26

Native checkpoint: `564f696e658f4f40c002c6ef52cae23a18492886`, library
`feff19defde9125ae7f21f07cb400bc388889e5dfab5b251db879c20c2856a1f`.
Reference: unchanged PyJoern 4.0.150.4 / Joern 4.0.150, pinned source
`958fdd3d976197a783f8ade1254b43e977648f28`. Reference source/JVM hashes and
128 operator constants were verified again in this run.

## Population and exact-input comparison

A fresh strict native audit of 77 real prepared **original-source excerpts**
from the frozen 1,225-input pool found 62 with a primary function CFG, six
strict rejections and nine with no primary function. These are extracted
functions, not complete translation units or 77 independent programs. The
1,148 decompiler-output inputs are excluded from this source audit.

This follow-up captures all 15 failure records with **identical UTF-8 source
bytes and C++ mode**. No wrappers, headers, sanitization, type hints or repairs
are applied to the primary comparison. Every original parse runs in an
isolated temporary cwd/interpreter with `PYTHONPATH` removed, CFG-only flags,
60s timeout / 90s retry budget. All captures succeeded without timeout/error.
The 15 records contain 14 distinct byte sequences; 31 and 44 are duplicates
retained as separate requested records. Original work was deduplicated by
content hash, with both result records preserved.

| Original public pipeline result | Records | Input indices |
| --- | --- | --- |
| No exported function/CFG | 11 | 9, 10, 17, 30, 31, 34, 35, 44, 1196, 1209, 1223 |
| Function with only a degenerate entry/exit block | 2 | 2, 40 |
| Nondegenerate CFG shape, with unsupported statement labels | 2 | 16, 20 |

The first category concerns the actual original `parse_source` public/export
pipeline; it is not proof that the underlying CDT has no AST for every input.
No original output is silently counted as a complete/semantically validated
function.

- Record 2 is `BuildLog::LogEntry::LogEntry`: its member initializer list is
  present in source, but the original public CFG contains only start/end.
- Record 40 is `Sink::~Sink() = default;`, with no explicit executable body.
  A defaulted declaration is different from a lost nonempty function body;
  implicit destruction semantics need separate source/class qualification.
- Records 16/20 are Snappy wrappers containing `CompressionOptions{}`. Original
  CFGs have one nondegenerate block, entry and exit, but explicitly contain
  `UnsupportedStmt` labels for the braced initializer/construction. This is
  useful structural extraction, not proof of complete expression modeling.

Thus **the 15 native failures are not 15 demonstrated original-only correctly
handled functions**. The two APIs differ on acceptance/export, but that alone
cannot establish a global C++ support percentage or semantic-quality ranking.

## Separate diagnostic experiments

The following experiments change context or options and are **not** added to
the exact-input success rate, evaluator population, caches or scores.

### Enclosing-class diagnostic

For each of the 11 empty original results, enclose the unchanged member bytes
in a minimal named class inferred from the constructor/destructor spelling.
No field definitions, base classes, alias/type facts or fabricated prototype
stubs are supplied. These are syntax-context probes, not asserted compiler-valid TUs or
qualified oracle replacements or source submitted for scoring.

Original exports the named member in **11/11 records** (10 distinct inputs).
Ten yield degenerate CFGs. The remaining destructor, `~PosixJobserverPool`,
yields a two-node graph with unsupported labels **and no exit marker**; it is
not accepted as complete CFG evidence. A class wrapper alone therefore
restores recognition but does not establish correct field/call/CFG semantics.

With the same diagnostic wrappers, native parsing recognizes all 11 members.
Five destructor cases have no strict errors. Six constructor cases retain
explicit member-initializer CFG errors; permissive graphs are kept only as
diagnostic output, not counted as qualified success. Strict refusal avoids
silently presenting a body-only graph as complete constructor behavior.

### Type-name diagnostic

On the two unchanged Snappy inputs, supplying the existing optional
`cpp_type_names=("CompressionOptions",)` makes native strict parsing succeed
and emit each named function's one-block CFG. No source text was changed, but
the parse context was changed. The current experiment does **not** establish
that name's exact parent-TU visibility/provenance, nor complete expression
or execution parity. It remains diagnostic-only.

The [existing source-context contract](../cpp-source-context.md) requires names
proved by the exact TU and definition scope. Its previously recorded prototype
already covers these two definitions; this audit confirms that the empty-
context readiness test exercises a stricter/different profile. Source names
must never be injected into producer parsing, and name context supplies no
class layout or initializer/lifetime effects.

## Conclusion and next work

The immediate bottlenecks separate into source extraction/context transport,
explicit constructor-initializer/lifetime qualification, and remaining
standalone syntax/export differences. Obtain and fingerprint the real enclosing
TU/class declarations before treating member snippets as standalone sources.
Then reuse the existing type-name interface where proven, and the bounded
[constructor profile](../cpp-constructor-initializers.md) only where its field
and effect contracts are satisfied. Preserve empty/defaulted-body and missing
function distinctions. Do not suppress diagnostics or insert guessed class
wrappers into the scored pipeline to increase success counts.

No native production code, DecBench pin/adapter/metric, denominator, score,
public leaderboard or upstream PR changes in this audit.

## Artifacts and reproduction

`workspace/cpp-cfg-gap-audit-2026-10-26/` retains `MANIFEST.json`, all 15 input
files, original reference JSON with source/version/module/flags/attempt data,
`capture.log`, `RESULT.json`, native permissive captures, and reference hash
verification. `CONTEXT-DIAGNOSTIC.json`, its inputs/references, native class
context results and `TYPE-NAME-DIAGNOSTIC.json` are explicitly separate.
The initial fresh 77-input audit and strict three-program probes remain in
`workspace/cpp-cfg-readiness-2026-10-26/`.

```sh
PYTHON scripts/capture_pyjoern_corpus.py --manifest MANIFEST.json \
  --reference-python ORIGINAL_PYTHON --workers 2 --timeout 60 --retry-timeout 90
```

Use a fresh reference directory to repeat capture rather than reuse files.
The existing capture driver checks prepared hashes and isolates each original
parse; supplemental class-context diagnostics use a different manifest and
must never replace the primary files/results.
