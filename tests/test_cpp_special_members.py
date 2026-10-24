"""Original-Joern recovery parity for incomplete real C++ method slices."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

import rust_joern

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/cpp-special-members"
SPEC = importlib.util.spec_from_file_location(
    "special_member_comparison", ROOT / "scripts/compare_pyjoern.py"
)
COMPARISON = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARISON)


class CppSpecialMemberRecoveryTests(unittest.TestCase):
    def test_real_isolated_bodies_match_original_recovery(self):
        captures = json.loads((FIXTURES / "provenance.json").read_text())["captures"]
        for capture in captures:
            with self.subTest(source=capture["source"]):
                source = FIXTURES / capture["source"]
                reference_bytes = source.with_name(
                    source.name + ".pyjoern.json"
                ).read_bytes()
                reference = json.loads(reference_bytes)
                self.assertEqual(
                    hashlib.sha256(source.read_bytes()).hexdigest(),
                    capture["source_sha256"],
                )
                self.assertEqual(
                    hashlib.sha256(reference_bytes).hexdigest(),
                    capture["reference_sha256"],
                )
                self.assertEqual(reference["source_sha256"], capture["source_sha256"])
                self.assertEqual(reference["prepared_sha256"], capture["source_sha256"])
                self.assertEqual(
                    reference["generator"], "pyjoern 4.0.150.4 / Joern v4.0.150"
                )
                parsed = rust_joern.parse_code(
                    source.read_bytes(),
                    filename=source,
                    strict=True,
                    preprocessed=True,
                    joern_loop_conditions=True,
                )
                actual = COMPARISON.candidate_functions(parsed.raw)
                self.assertEqual(set(actual), set(reference["functions"]))
                for row in COMPARISON.compare(reference["functions"], actual):
                    self.assertEqual(row["status"], "match", row)
                for method in parsed.raw["functions"]:
                    self.assertFalse(
                        any(n.get("name") == "this" for n in method["cpg"]["nodes"])
                    )


if __name__ == "__main__":
    unittest.main()
