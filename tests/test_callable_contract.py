"""Original C++ callable-object contracts; no candidate-generated goldens."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "callable_contract", ROOT / "scripts/joern_port/call_contract.py"
)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class CallableContractTests(unittest.TestCase):
    def test_declared_callable_objects_match_original_calls_and_result_types(self):
        import rust_joern

        base = ROOT / "tests/fixtures/joern-callables"
        source = base / "callables.cpp"
        reference = json.loads((base / "original.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), reference["source_sha256"]
        )
        self.assertTrue(reference["call_types"])
        self.assertTrue(reference["operand_positions"])
        self.assertEqual(len(reference["methods"]), 26)
        self.assertEqual(sum(len(m["calls"]) for m in reference["methods"]), 25)
        analysis = rust_joern.parse_code(
            source.read_text(), filename=source.name, strict=True, preprocessed=True
        ).raw
        self.assertEqual(contract.compare(reference, analysis), [])

    def test_identically_spelled_argument_occurrences_cannot_swap_positions(self):
        method = {
            "fullname": "f",
            "start_line": 1,
            "cpg": {
                "nodes": [
                    {
                        "id": 0,
                        "kind": "CALL",
                        "name": "f",
                        "code": "f(tick(),tick())",
                        "line": 1,
                        "column": 1,
                    },
                    {
                        "id": 1,
                        "kind": "CALL",
                        "name": "tick",
                        "code": "tick()",
                        "line": 1,
                        "column": 3,
                    },
                    {
                        "id": 2,
                        "kind": "CALL",
                        "name": "tick",
                        "code": "tick()",
                        "line": 1,
                        "column": 10,
                    },
                ],
                "edges": [
                    {"source": 0, "target": 1, "kind": "AST"},
                    {"source": 0, "target": 2, "kind": "AST"},
                    {"source": 0, "target": 1, "kind": "ARGUMENT", "label": "1"},
                    {"source": 0, "target": 2, "kind": "ARGUMENT", "label": "2"},
                ],
            },
        }
        wrong = copy.deepcopy(method)
        wrong["cpg"]["edges"][2]["target"] = 2
        wrong["cpg"]["edges"][3]["target"] = 1
        self.assertNotEqual(
            contract.project(method, operand_positions=True),
            contract.project(wrong, operand_positions=True),
        )

    def test_source_owner_fragments_are_pinned(self):
        manifest = json.loads(
            (ROOT / "tests/reference/joern-4.0.150/callable-rules.json").read_text()
        )
        self.assertEqual(manifest["commit"], "958fdd3d976197a783f8ade1254b43e977648f28")
        self.assertEqual(len(manifest["functions"]), 5)
        for function in manifest["functions"]:
            self.assertEqual(
                hashlib.sha256(function["scala"].encode()).hexdigest(),
                function["fragment_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
