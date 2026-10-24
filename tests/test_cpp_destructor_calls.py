"""Reference CFGs for explicit destructor calls; controls are not corpus samples."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

import rust_joern

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/cpp-destructor-calls"
SPEC = importlib.util.spec_from_file_location(
    "destructor_comparison", ROOT / "scripts/compare_pyjoern.py"
)
COMPARISON = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARISON)


class CppDestructorCallTests(unittest.TestCase):
    def test_frozen_original_cfgs_and_corpus_receiver_identity(self):
        for case in json.loads((FIXTURES / "provenance.json").read_text())["captures"]:
            with self.subTest(source=case["source"]):
                source = FIXTURES / case["source"]
                reference_bytes = source.with_name(
                    source.name + ".pyjoern.json"
                ).read_bytes()
                reference = json.loads(reference_bytes)
                self.assertEqual(
                    hashlib.sha256(source.read_bytes()).hexdigest(),
                    case["source_sha256"],
                )
                self.assertEqual(
                    hashlib.sha256(reference_bytes).hexdigest(),
                    case["reference_sha256"],
                )
                self.assertEqual(
                    reference["generator"], "pyjoern 4.0.150.4 / Joern v4.0.150"
                )
                self.assertEqual(reference["prepared_sha256"], case["source_sha256"])
                analysis = rust_joern.parse_code(
                    source.read_bytes(),
                    filename=source,
                    language="c++",
                    preprocessed=True,
                    strict=True,
                    joern_loop_conditions=True,
                )
                actual = COMPARISON.candidate_functions(analysis.raw)
                self.assertEqual(set(actual), set(reference["functions"]))
                for row in COMPARISON.compare(reference["functions"], actual):
                    self.assertEqual(row["status"], "match", row)
                if case["kind"].startswith("unchanged real"):
                    method = next(
                        f for f in analysis.raw["functions"] if f["name"] == "Reset"
                    )
                    calls = [n for n in method["cpg"]["nodes"] if n["kind"] == "CALL"]
                    destructors = [
                        n for n in calls if n.get("name") == "~WorkingMemory"
                    ]
                    self.assertEqual(len(destructors), 1)
                    self.assertFalse(
                        any(n.get("name") == "WorkingMemory" for n in calls)
                    )
                    destructor = destructors[0]
                    self.assertEqual(
                        destructor["code"], "working_memory_->~WorkingMemory()"
                    )
                    argument = next(
                        e
                        for e in method["cpg"]["edges"]
                        if e["kind"] == "ARGUMENT"
                        and e["source"] == destructor["id"]
                        and e.get("label") == "0"
                    )
                    receiver = next(
                        n
                        for n in method["cpg"]["nodes"]
                        if n["id"] == argument["target"]
                    )
                    self.assertEqual(receiver["code"], "working_memory_")

    def test_invalid_destructor_arguments_are_not_qualified_by_recovery(self):
        for case in json.loads((FIXTURES / "provenance.json").read_text())[
            "rejected_controls"
        ]:
            source = FIXTURES / case["source"]
            raw_reference = source.with_name(source.name + ".pyjoern.json").read_bytes()
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).hexdigest(), case["source_sha256"]
            )
            self.assertEqual(
                hashlib.sha256(raw_reference).hexdigest(), case["reference_sha256"]
            )
            reference = json.loads(raw_reference)
            self.assertEqual(
                reference["generator"], "pyjoern 4.0.150.4 / Joern v4.0.150"
            )
            self.assertEqual(reference["prepared_sha256"], case["source_sha256"])
            self.assertIn("f", reference["functions"])
            permissive = rust_joern.parse_code(
                source.read_bytes(),
                filename=source,
                language="c++",
                preprocessed=True,
                strict=False,
            )
            self.assertTrue(
                any(
                    d["severity"] == "error" and "destructor-id" in d["message"]
                    for d in permissive.raw["diagnostics"]
                )
            )
            with self.assertRaisesRegex(RuntimeError, "destructor-id"):
                rust_joern.parse_code(
                    source.read_bytes(),
                    filename=source,
                    language="c++",
                    preprocessed=True,
                    strict=True,
                )


if __name__ == "__main__":
    unittest.main()
