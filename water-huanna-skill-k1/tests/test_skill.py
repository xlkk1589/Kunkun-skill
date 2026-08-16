#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "water_huanna.py"
SPEC = importlib.util.spec_from_file_location("water_huanna", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class WaterHuannaTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = ROOT / "tests" / "fixtures"

    def test_catalog_has_159_independent_profiles(self):
        catalog = MODULE.load_catalog()
        self.assertEqual(len(catalog), 159)
        self.assertEqual([item["id"] for item in catalog], list(range(1, 160)))
        self.assertEqual(len(list((ROOT / "references" / "styles").glob("*.json"))), 159)
        for item in catalog:
            self.assertTrue(item["required_roles"])
            self.assertIn("renderer_hint", item)
            self.assertIn("fidelity_risks", item)

    def test_audited_category_exceptions(self):
        catalog = {item["id"]: item for item in MODULE.load_catalog()}
        self.assertEqual(catalog[76]["family"], "swimmer")
        self.assertEqual(catalog[79]["family"], "forest")
        self.assertEqual(catalog[130]["family"], "spatial_transcriptomics")
        self.assertFalse(catalog[76]["source_category_audited"])

    def test_recommend_grouped_distribution(self):
        result = MODULE.recommend(
            self.fixtures / "grouped_values.csv",
            "比较三组数据的分布与离群值",
            10,
            {},
        )
        families = {item["family"] for item in result["recommendations"]}
        self.assertTrue(families & {"raincloud", "violin", "boxplot"})

    def test_forest_ready(self):
        result = MODULE.validate(self.fixtures / "forest.csv", 79, {}, "l1", None)
        self.assertEqual(result["decision"], "ready")

    def test_map_missing_crs_is_blocked(self):
        result = MODULE.validate(self.fixtures / "map_points_missing_crs.csv", 92, {}, "l1", None)
        self.assertEqual(result["decision"], "blocked")
        missing_roles = {item["role"] for item in result["data_validation"]["missing"]}
        self.assertIn("crs", missing_roles)
        missing_fidelity = {item["item"] for item in result["fidelity_missing"]}
        self.assertIn("boundary_source", missing_fidelity)

    def test_l3_requires_reproduction_environment(self):
        result = MODULE.validate(self.fixtures / "forest.csv", 79, {}, "l3", None)
        missing = {item["item"] for item in result["fidelity_missing"]}
        self.assertIn("original_code", missing)
        self.assertIn("random_seed", missing)
        self.assertEqual(result["decision"], "blocked")

    def test_basic_forest_render(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forest.png"
            result = MODULE.render_basic(self.fixtures / "forest.csv", 79, output, {})
            self.assertEqual(result["render_status"], "completed")
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
