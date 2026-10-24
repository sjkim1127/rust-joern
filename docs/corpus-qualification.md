# Checkpointed parser corpus qualification

`scripts/qualify_corpus.py` consumes a frozen JSON object with a `rows` array.
Each row has `filename`, `language` (`c`, `cpp` or `c++`), `text`, and the SHA256
of its UTF-8 `text` as `sha256`. Optional `origins` is retained verbatim. Rows
remain distinct requests even when their bytes are equal. Source preparation,
ownership and producer-validity checks belong to the caller; this driver never
supplies oracle declarations to producer code or fixes invalid output.

```sh
python scripts/qualify_corpus.py --inputs prepared.json \
  --library /absolute/path/librust_joern.so --output workspace/parse-v1 \
  --jobs 4 --timeout 60 --max-new 100
python scripts/qualify_corpus.py --inputs prepared.json \
  --library /absolute/path/librust_joern.so --output workspace/parse-v1 \
  --jobs 4 --timeout 60 --resume
```

The Unix-hosted driver isolates every input in a subprocess, bounds the number
of submitted tasks and kills the process group on timeout. The library, wrapper
and worker script are frozen into the output directory. A contract includes
source manifest, backend, wrapper, driver, Python/platform/dependency versions,
options and timeout. Resume refuses changed contracts or damaged checkpoint
bytes. Per-input atomic envelopes bind outcomes and compressed full analyses
by hash; a crash before the envelope is committed leaves the input pending.
Completed rejected/timeout/error inputs are reused, never silently retried or
removed. A new experiment uses a new directory. Parser graphs are retained even
when diagnostics reject the input, but `qualified_methods` is zero for it.

`summary.json` includes every request as parsed, parse_rejected, no_methods,
timeout, worker_crash, evaluator_error or pending. `methods_emitted` includes
prototypes and is not a source-definition coverage count. Acceptance does not
mean producer validity, CFG correctness, a GED denominator or an official score.
`--joern-loop-conditions` and `--constructor-initializers` are separate opt-ins;
the latter accepts a C++ pool only and requires the experimental frontend
profile. With both options off, the driver also supports older `parse_code`
wrappers; it does not send disabled, version-specific keywords. There is no hardcoded 250-function cap.

This is a parser-qualification lane, not a replacement for whole-binary
producer discovery, type evaluation, graph correspondence, recompilation or
execution validation. Those stages retain their own independent evidence and
populations. Full-run memory, exceptionally large single functions and native
resource containment beyond process/time limits remain separate work.

Exit 0 means the requested parser report completed without worker failure; it
does not mean the inputs are valid or CFGs correct. Exit 1 retains the complete
report but flags timeout, worker crash or evaluator error. Exit 2 means pending
requests remain after a bounded pass. Contract/evidence errors abort with a
nonzero exit instead of becoming oracle exclusions.

For a completed before/after loop, run `scripts/compare_qualification.py
--baseline BASELINE_RUN --candidate CANDIDATE_RUN --output NEW_DIFF_DIRECTORY`.
It rechecks every atomic outcome, source request and compressed/full analysis,
requires the same complete requested population, and writes `comparison.json`
and an investigation `queue.json`. The queue retains origin references and
errors without deciding whether a rejected source is invalid producer output,
a parser gap or missing context. Exit 1 flags lost parsing and exit 2 flags
remaining evaluator/worker/timeout failures. All graph changes still require
semantic review; graph hash equality and newly accepted syntax are not scores.
