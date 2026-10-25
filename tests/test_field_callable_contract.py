"""Field-callable contracts captured from unchanged Joern, not native goldens."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "field_callable_contract", ROOT / "scripts/joern_port/call_contract.py"
)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class FieldCallableContractTests(unittest.TestCase):
    def test_field_callables_match_original_identity_types_and_shared_operands(self):
        import rust_joern

        base = ROOT / "tests/fixtures/joern-field-callables"
        source = base / "fields.cpp"
        reference = json.loads((base / "original.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), reference["source_sha256"]
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / "tests/fixtures/ddg-lambdas/capture.sc").read_bytes()
            ).hexdigest(),
            reference["capture_sha256"],
        )
        self.assertTrue(reference["call_types"])
        self.assertTrue(reference["operand_positions"])
        self.assertEqual(len(reference["methods"]), 11)
        self.assertEqual(sum(len(m["calls"]) for m in reference["methods"]), 12)
        self.assertIn("Joern v4.0.150", reference["generator"])
        analysis = rust_joern.parse_code(
            source.read_text(), filename=source.name, strict=True, preprocessed=True
        ).raw
        self.assertEqual(contract.compare(reference, analysis), [])


if __name__ == "__main__":
    unittest.main()
