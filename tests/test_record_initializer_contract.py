"""Type initializer CPG contracts; unchanged original Joern is the oracle."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "record_initializer_contract", ROOT / "scripts/joern_port/call_contract.py"
)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class RecordInitializerContractTests(unittest.TestCase):
    def test_all_methods_and_intrinsic_calls_match_original(self):
        import rust_joern

        base = ROOT / "tests/fixtures/joern-record-initializers"
        source = base / "initializers.cpp"
        ref = json.loads((base / "original.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), ref["source_sha256"]
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / "tests/fixtures/ddg-lambdas/capture.sc").read_bytes()
            ).hexdigest(),
            ref["capture_sha256"],
        )
        self.assertTrue(ref["include_intrinsics"])
        self.assertTrue(ref["call_types"])
        self.assertTrue(ref["operand_positions"])
        self.assertEqual(len(ref["methods"]), 7)
        self.assertEqual(sum(len(m["calls"]) for m in ref["methods"]), 14)
        raw = rust_joern.parse_code(
            source.read_text(), filename=source.name, preprocessed=True, strict=True
        ).raw
        self.assertEqual(contract.compare(ref, raw), [])
        self.assertEqual(sum(f["name"] == "<clinit>" for f in raw["functions"]), 4)

    def test_member_lambdas_keep_complete_original_method_population(self):
        import rust_joern

        for name, method_count in [
            ("member-lambda", 2),
            ("nested-member-lambda", 2),
            ("ordered-lambdas", 5),
        ]:
            with self.subTest(name=name):
                root = ROOT / "tests/fixtures/joern-record-initializers" / name
                source = root / "test.cpp"
                ref = json.loads((root / "reference.json").read_text())
                self.assertEqual(
                    hashlib.sha256(source.read_bytes()).hexdigest(),
                    ref["source_sha256"],
                )
                self.assertEqual(len(ref["methods"]), method_count)
                raw = rust_joern.parse_code(
                    source.read_text(),
                    filename=source.name,
                    preprocessed=True,
                    strict=True,
                ).raw
                self.assertEqual(contract.compare(ref, raw), [])

    def test_fixed_array_callable_control_now_keeps_original_clinit_population(self):
        import rust_joern

        root = ROOT / "tests/fixtures/joern-record-initializers/fixed-array-fields"
        source = root / "fields.cpp"
        ref = json.loads((root / "reference.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), ref["source_sha256"]
        )
        self.assertEqual(len(ref["methods"]), 12)
        raw = rust_joern.parse_code(
            source.read_text(), filename=source.name, preprocessed=True, strict=True
        ).raw
        self.assertEqual(contract.compare(ref, raw), [])

    def test_raw_container_cfg_topology_and_node_kind_code_match_original(self):
        import networkx as nx
        import rust_joern

        base = ROOT / "tests/fixtures/joern-record-initializers"
        source = base / "initializers.cpp"
        ref = json.loads((base / "original-container-cfg.json").read_text())
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), ref["source_sha256"]
        )
        self.assertEqual(ref["full_original_method_population"], 7)
        raw = rust_joern.parse_code(
            source.read_text(), filename=source.name, preprocessed=True, strict=True
        ).raw
        actual = {m["fullname"]: m for m in raw["functions"] if m["name"] == "<clinit>"}
        self.assertEqual(set(actual), set(ref["methods"]))
        self.assertEqual(len(actual), 4)
        for name, expected in ref["methods"].items():
            with self.subTest(method=name):
                old = nx.DiGraph()
                old.add_nodes_from(
                    (n["id"], {"label": (n["kind"], n["code"])})
                    for n in expected["nodes"]
                )
                old.add_edges_from(expected["edges"])
                cpg = actual[name]["cpg"]
                edges = [
                    (e["source"], e["target"])
                    for e in cpg["edges"]
                    if e["kind"] == "CFG"
                ]
                ids = {
                    n["id"]
                    for n in cpg["nodes"]
                    if n["kind"] in ("METHOD", "METHOD_RETURN")
                }
                ids.update(i for edge in edges for i in edge)
                new = nx.DiGraph()
                new.add_nodes_from(
                    (n["id"], {"label": (n["kind"], n["code"])})
                    for n in cpg["nodes"]
                    if n["id"] in ids
                )
                new.add_edges_from(edges)
                self.assertTrue(
                    nx.is_isomorphic(
                        old,
                        new,
                        node_match=nx.algorithms.isomorphism.categorical_node_match(
                            "label", None
                        ),
                    )
                )

    def test_direct_source_owners_are_pinned(self):
        ref = json.loads(
            (ROOT / "tests/reference/joern-4.0.150/record-init-rules.json").read_text()
        )
        self.assertEqual(ref["commit"], "958fdd3d976197a783f8ade1254b43e977648f28")
        self.assertEqual(len(ref["functions"]), 3)
        self.assertEqual(len({f["owner"] for f in ref["functions"]}), 2)
        for f in ref["functions"]:
            self.assertEqual(
                hashlib.sha256(f["scala"].encode()).hexdigest(), f["fragment_sha256"]
            )


if __name__ == "__main__":
    unittest.main()
