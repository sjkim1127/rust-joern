#!/usr/bin/env python3
"""Checkpoint parser qualification on frozen prepared bytes; never score or sanitize them."""

from __future__ import annotations

import argparse
from collections import Counter
import contextlib
from concurrent.futures import ThreadPoolExecutor
import fcntl
import gzip
import hashlib
import importlib.metadata
import platform
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any


def encoded(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def worker(request: Path) -> None:
    job = json.loads(request.read_bytes())
    os.environ["RUST_JOERN_LIBRARY"] = job["library"]
    sys.path.insert(0, job["python_path"])
    import rust_joern

    row = job["row"]
    options = {}
    if job["compat"]:
        options["joern_loop_conditions"] = True
    if job["constructors"]:
        options["cpp_constructor_initializers"] = True
    raw = rust_joern.parse_code(
        row["text"],
        filename=row["filename"],
        language=row["language"],
        preprocessed=True,
        strict=False,
        **options,
    ).raw
    payload = encoded(raw)
    atomic(Path(job["analysis"]), gzip.compress(payload, mtime=0))
    errors = [d for d in raw["diagnostics"] if d["severity"] == "error"]
    print(
        json.dumps(
            {
                "status": (
                    "parse_rejected"
                    if errors
                    else "parsed" if raw["functions"] else "no_methods"
                ),
                "analysis_sha256": sha(payload),
                "errors": errors,
                "methods_emitted": len(raw["functions"]),
                "qualified_methods": 0 if errors else len(raw["functions"]),
                "output_validity": "not_assessed",
                "elapsed": None,
            }
        ),
        flush=True,
    )


def execute(job: dict[str, Any], checkpoint: Path, timeout: float) -> dict[str, Any]:
    analysis = checkpoint.with_suffix(".analysis.json.gz")
    analysis.unlink(missing_ok=True)
    job = {**job, "analysis": str(analysis)}
    request = checkpoint.with_suffix(".request.json")
    atomic(request, encoded(job))
    started = time.monotonic()
    process = subprocess.Popen(
        [sys.executable, job["driver"], "--worker", str(request)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        env={**os.environ, "RAYON_NUM_THREADS": "1"},
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        if process.returncode:
            result = {
                "status": (
                    "worker_crash" if process.returncode < 0 else "evaluator_error"
                ),
                "returncode": process.returncode,
            }
        else:
            try:
                result = json.loads(stdout)
            except (ValueError, UnicodeDecodeError):
                result = {
                    "status": "evaluator_error",
                    "reason": "invalid worker response",
                }
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        result = {"status": "timeout"}
    except BaseException:
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    atomic(checkpoint.with_suffix(".stderr.log"), stderr)
    result.update(
        {
            "request_sha256": job["request_sha256"],
            "elapsed": time.monotonic() - started,
            "stderr_sha256": sha(stderr),
        }
    )
    if analysis.exists():
        result["compressed_analysis_sha256"] = sha(analysis.read_bytes())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--library", type=Path)
    parser.add_argument(
        "--python-path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "python",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--max-new", type=int, help="Bound new work; leave remaining requests pending"
    )
    parser.add_argument("--joern-loop-conditions", action="store_true")
    parser.add_argument("--constructor-initializers", action="store_true")
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    if not all((args.inputs, args.library, args.output)):
        parser.error("--inputs, --library and --output are required")
    if (
        args.jobs < 1
        or not math.isfinite(args.timeout)
        or args.timeout <= 0
        or (args.max_new is not None and args.max_new < 0)
    ):
        parser.error("jobs/timeout must be positive and max-new nonnegative")
    rows = json.loads(args.inputs.read_bytes())["rows"]
    for row in rows:
        if sha(row["text"].encode()) != row["sha256"]:
            raise ValueError("prepared source SHA mismatch")
        if row["language"] not in ("c", "cpp", "c++"):
            raise ValueError("explicit input language required")
        if args.constructor_initializers and row["language"] == "c":
            raise ValueError("constructor profile only accepts a C++ input pool")
    library = args.library.resolve(strict=True)
    wrapper = args.python_path.resolve(strict=True)
    library_bytes = library.read_bytes()
    wrapper_bytes = (wrapper / "rust_joern" / "__init__.py").read_bytes()
    driver_bytes = Path(__file__).read_bytes()
    dependencies = {}
    for name in ("networkx", "orjson"):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    contract = {
        "schema": "parser-qualification-v1",
        "inputs_sha256": sha(args.inputs.read_bytes()),
        "requested": len(rows),
        "library_sha256": sha(library_bytes),
        "wrapper_sha256": sha(wrapper_bytes),
        "driver_sha256": sha(driver_bytes),
        "dependencies": dependencies,
        "platform": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "timeout": args.timeout,
        "compat": args.joern_loop_conditions,
        "constructors": args.constructor_initializers,
        "preprocessed": True,
        "data_flow": False,
        "rayon_num_threads": 1,
        "official_score": False,
    }
    args.output.mkdir(parents=True, exist_ok=args.resume)
    with (args.output / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        contract_path = args.output / "contract.json"
        if (
            contract_path.exists()
            and json.loads(contract_path.read_bytes()) != contract
        ):
            raise ValueError("resume contract changed; use a new output directory")
        atomic(contract_path, encoded(contract))
        runtime = args.output.resolve() / "runtime"
        for path, data in (
            (runtime / library.name, library_bytes),
            (runtime / "python" / "rust_joern" / "__init__.py", wrapper_bytes),
            (runtime / "qualify_corpus.py", driver_bytes),
        ):
            if path.exists() and path.read_bytes() != data:
                raise ValueError("frozen runtime changed")
            if not path.exists():
                atomic(path, data)
        library = runtime / library.name
        wrapper = runtime / "python"
        checkpoints = args.output.resolve() / "checkpoints"
        checkpoints.mkdir(exist_ok=True)
        records: dict[int, dict[str, Any]] = {}
        pending = []
        for index, row in enumerate(rows):
            request_hash = sha(encoded({"contract": contract, "row": row}))
            path = checkpoints / f"{index:08d}.json"
            if path.exists():
                envelope = json.loads(path.read_bytes())
                record = envelope["record"]
                if (
                    sha(encoded(record)) != envelope["sha256"]
                    or record["request_sha256"] != request_hash
                ):
                    raise ValueError("checkpoint/request bytes changed")
                for suffix, field in (
                    (".analysis.json.gz", "compressed_analysis_sha256"),
                    (".stderr.log", "stderr_sha256"),
                ):
                    if (
                        field in record
                        and sha(path.with_suffix(suffix).read_bytes()) != record[field]
                    ):
                        raise ValueError("checkpoint evidence changed")
                records[index] = record
            else:
                pending.append((index, row, request_hash, path))
        selected = pending if args.max_new is None else pending[: args.max_new]

        def run(
            item: tuple[int, dict[str, Any], str, Path],
        ) -> tuple[int, dict[str, Any]]:
            index, row, request_hash, path = item
            result = execute(
                {
                    "row": row,
                    "driver": str(runtime / "qualify_corpus.py"),
                    "library": str(library),
                    "python_path": str(wrapper),
                    "compat": args.joern_loop_conditions,
                    "constructors": args.constructor_initializers,
                    "request_sha256": request_hash,
                },
                path,
                args.timeout,
            )
            atomic(path, encoded({"record": result, "sha256": sha(encoded(result))}))
            return index, result

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            for offset in range(0, len(selected), args.jobs):
                for index, record in pool.map(
                    run, selected[offset : offset + args.jobs]
                ):
                    records[index] = record
                    if len(records) % 100 == 0:
                        print(
                            json.dumps(
                                {"completed": len(records), "requested": len(rows)}
                            ),
                            flush=True,
                        )
        summary_rows = [
            {
                "index": index,
                "source_sha256": row["sha256"],
                "filename": row["filename"],
                "origins": row.get("origins", []),
                **records.get(index, {"status": "pending"}),
            }
            for index, row in enumerate(rows)
        ]
        summary = {
            "contract": contract,
            "requested": len(rows),
            "completed": len(records),
            "reused": len(records) - len(selected),
            "new": len(selected),
            "statuses": dict(Counter(row["status"] for row in summary_rows)),
            "rows": summary_rows,
        }
        atomic(args.output / "summary.json", encoded(summary))
        print(
            json.dumps(
                {
                    key: summary[key]
                    for key in ("requested", "completed", "reused", "new", "statuses")
                }
            ),
            flush=True,
        )

        if any(
            summary["statuses"].get(status, 0)
            for status in ("evaluator_error", "worker_crash", "timeout")
        ):
            raise SystemExit(1)
        if summary["statuses"].get("pending", 0):
            raise SystemExit(2)


if __name__ == "__main__":
    main()
