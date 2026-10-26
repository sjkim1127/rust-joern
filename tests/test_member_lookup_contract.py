"""Original Joern evidence for bounded lookup and grouped lambda identities."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "member_lookup_contract", ROOT / "scripts/joern_port/call_contract.py"
)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class MemberLookupContractTests(unittest.TestCase):
    def check_original(self, name, methods, calls):
        import rust_joern

        base = ROOT / "tests/fixtures/joern-member-lookup"
        source = base / (name + ".cpp")
        ref = json.loads((base / (name + "-original.json")).read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), ref["source_sha256"]
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / "tests/fixtures/ddg-lambdas/capture.sc").read_bytes()
            ).hexdigest(),
            ref["capture_sha256"],
        )
        self.assertTrue(ref["call_types"])
        self.assertTrue(ref["operand_positions"])
        self.assertEqual(len(ref["methods"]), methods)
        self.assertEqual(sum(len(m["calls"]) for m in ref["methods"]), calls)
        raw = rust_joern.parse_code(
            source.read_text(), filename=source.name, preprocessed=True, strict=True
        ).raw
        self.assertEqual(contract.compare(ref, raw), [])

    def test_inherited_alias_and_cv_field_calls_match_original(self):
        self.check_original("lookup", 23, 21)

    def test_plain_grouped_and_invoked_lambda_method_and_reference_names(self):
        self.check_original("lambdas", 8, 4)

    def test_grouped_lambda_definitions_and_reference_targets_stay_coupled(self):
        import rust_joern

        base = ROOT / "tests/fixtures/joern-member-lookup"
        source = base / "lambdas.cpp"
        expected = json.loads((base / "lambda-bindings-original.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), expected["source_sha256"]
        )
        raw = rust_joern.parse_code(
            source.read_text(), filename=source.name, preprocessed=True, strict=True
        ).raw
        actual = [
            {
                "owner": m["fullname"],
                "code": n["code"],
                "line": n["line"],
                "column": n["column"],
                "target": n["method_full_name"],
            }
            for m in raw["functions"]
            for n in m["cpg"]["nodes"]
            if n["kind"] == "METHOD_REF"
        ]
        actual.sort(key=lambda x: (x["owner"], x["line"], x["column"]))
        self.assertEqual(len(actual), 4)
        self.assertEqual(actual, expected["references"])
        methods = {m["fullname"] for m in raw["functions"]}
        self.assertTrue(all(r["target"] in methods for r in actual))

    def test_volatile_field_uses_the_original_untyped_call_contract(self):
        self.check_original("volatile", 2, 1)

    def test_reference_owners_are_immutable(self):
        ref = json.loads(
            (
                ROOT / "tests/reference/joern-4.0.150/member-lookup-rules.json"
            ).read_text()
        )
        self.assertEqual(ref["commit"], "958fdd3d976197a783f8ade1254b43e977648f28")
        self.assertEqual(len(ref["functions"]), 4)
        for f in ref["functions"]:
            self.assertEqual(
                hashlib.sha256(f["scala"].encode()).hexdigest(), f["fragment_sha256"]
            )


if __name__ == "__main__":
    unittest.main()
