#!/usr/bin/env python3
"""Compare complete parser captures and group failures; parsing gains are not quality scores."""

from __future__ import annotations

import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
from typing import Any

from qualify_corpus import atomic, encoded, sha


def load(root: Path) -> dict[str, Any]:
    summary = json.loads((root / "summary.json").read_bytes())
    contract = json.loads((root / "contract.json").read_bytes())
    if summary["contract"] != contract or summary["completed"] != summary["requested"]:
        raise ValueError("incomplete or incompatible parser capture")
    if summary["requested"] != len(summary["rows"]):
        raise ValueError("requested population disagrees with rows")
    for index, row in enumerate(summary["rows"]):
        path = root / "checkpoints" / f"{index:08d}.json"
        envelope = json.loads(path.read_bytes())
        record = envelope["record"]
        request = json.loads(path.with_suffix(".request.json").read_bytes())
        source = request["row"]
        if (
            row["index"] != index
            or sha(encoded(record)) != envelope["sha256"]
            or any(row.get(key) != value for key, value in record.items())
            or sha(encoded({"contract": contract, "row": source}))
            != record["request_sha256"]
            or sha(source["text"].encode()) != row["source_sha256"]
            or source["filename"] != row["filename"]
            or source.get("origins", []) != row["origins"]
        ):
            raise ValueError("parser checkpoint/source evidence changed")
        if "compressed_analysis_sha256" in record:
            data = path.with_suffix(".analysis.json.gz").read_bytes()
            if sha(data) != record["compressed_analysis_sha256"]:
                raise ValueError("compressed parser analysis changed")
            if (
                "analysis_sha256" in record
                and sha(gzip.decompress(data)) != record["analysis_sha256"]
            ):
                raise ValueError("raw parser analysis changed")
        if sha(path.with_suffix(".stderr.log").read_bytes()) != record["stderr_sha256"]:
            raise ValueError("parser stderr evidence changed")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before, after = load(args.baseline), load(args.candidate)
    if (
        before["requested"] != after["requested"]
        or before["contract"]["inputs_sha256"] != after["contract"]["inputs_sha256"]
    ):
        raise ValueError("parser populations differ")
    changes, gains, losses = [], [], []
    queue: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for old, new in zip(before["rows"], after["rows"]):
        for key in ("index", "filename", "source_sha256", "origins"):
            if old[key] != new[key]:
                raise ValueError("parser request identity differs")
        unit = {
            key: new[key] for key in ("index", "filename", "source_sha256", "origins")
        }
        if old["status"] != "parsed" and new["status"] == "parsed":
            gains.append(unit)
        if old["status"] == "parsed" and new["status"] != "parsed":
            losses.append(unit)
        if (
            old.get("analysis_sha256") != new.get("analysis_sha256")
            or old["status"] != new["status"]
        ):
            changes.append(
                {
                    **unit,
                    "before_status": old["status"],
                    "after_status": new["status"],
                    "before_analysis_sha256": old.get("analysis_sha256"),
                    "after_analysis_sha256": new.get("analysis_sha256"),
                }
            )
        if new["status"] != "parsed":
            reasons = sorted({error["message"] for error in new.get("errors", [])}) or [
                new["status"]
            ]
            for reason in reasons:
                queue[reason].append({**unit, "status": new["status"]})
    result = {
        "profile": "parser-qualification-difference-v1",
        "official_score": False,
        "requested": after["requested"],
        "baseline_contract": before["contract"],
        "candidate_contract": after["contract"],
        "newly_parsed": gains,
        "lost_parsing": losses,
        "changed_full_analyses": changes,
        "baseline": str(args.baseline.resolve()),
        "candidate": str(args.candidate.resolve()),
        "semantic_parity": "not measured",
        "producer_validity": "not inferred",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    atomic(args.output / "comparison.json", encoded(result))
    atomic(
        args.output / "queue.json",
        encoded(
            {
                "ownership": "requires investigation",
                "groups": dict(sorted(queue.items())),
            }
        ),
    )
    print(
        json.dumps(
            {
                "requested": result["requested"],
                "newly_parsed": len(gains),
                "lost_parsing": len(losses),
                "changed_analyses": len(changes),
                "failure_groups": len(queue),
            }
        )
    )
    if losses:
        raise SystemExit(1)
    if any(
        after["statuses"].get(status, 0)
        for status in ("evaluator_error", "worker_crash", "timeout")
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
