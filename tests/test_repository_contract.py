from __future__ import annotations

import json
import re
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_management_validation_baseline(self):
        data = json.loads(
            (ROOT / "outputs/management/management_export_validation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["sql_validation"], "PASS")
        self.assertEqual(data["reference_reconciliation"], "PASS")
        self.assertEqual(data["references"]["SalesRevenue"]["actual"], "19701685.50700000")
        self.assertEqual(data["references"]["UnitsSold"]["actual"], "11221960")
        self.assertEqual(data["references"]["Orders"]["actual"], "39519")
        self.assertEqual(data["references"]["SalesCustomers"]["actual"], "5852")
        self.assertEqual(data["references"]["CancellationValue"]["actual"], "719692.94000000")
        self.assertEqual(data["references"]["AnonymousSalesRevenue"]["actual"], "2576013.46000000")
        self.assertEqual(data["references"]["CanonicalTransactionRows"]["actual"], "1044848")

    def test_power_bi_structure_baseline(self):
        report = ROOT / "powerbi/OnlineRetailAnalytics.Report/definition"
        semantic = ROOT / "powerbi/OnlineRetailAnalytics.SemanticModel/definition"

        self.assertEqual(len(list((report / "pages").glob("*/page.json"))), 10)
        self.assertEqual(len(list((report / "pages").glob("*/visuals/*/visual.json"))), 136)
        self.assertEqual(len(list(semantic.rglob("*.tmdl"))), 15)

        measures = (semantic / "tables/_Measures.tmdl").read_text(encoding="utf-8")
        relationships = (semantic / "relationships.tmdl").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^\s*measure\s+", measures, re.MULTILINE)), 50)
        self.assertEqual(len(re.findall(r"^relationship\s+", relationships, re.MULTILINE)), 7)

    def test_all_pbir_json_is_valid(self):
        report = ROOT / "powerbi/OnlineRetailAnalytics.Report/definition"
        for path in report.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_authentic_screenshot_set(self):
        shots = sorted((ROOT / "screenshots").glob("[0-9][0-9]_*.png"))
        self.assertEqual(len(shots), 10)
        self.assertTrue(all(p.stat().st_size > 0 for p in shots))

    def test_excel_package_sheet_counts(self):
        expected = {
            "Online_Retail_Management_Analytics.xlsx": 14,
            "Online_Retail_Analytical_Detail.xlsx": 16,
        }
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for name, count in expected.items():
            path = ROOT / "outputs/management" / name
            self.assertTrue(zipfile.is_zipfile(path))
            with zipfile.ZipFile(path) as zf:
                root = ET.fromstring(zf.read("xl/workbook.xml"))
            self.assertEqual(len(root.findall(".//m:sheets/m:sheet", ns)), count)

    def test_raw_and_interim_data_are_not_published(self):
        for folder in ("raw", "interim", "processed"):
            path = ROOT / "data" / folder
            extras = [p.name for p in path.iterdir() if p.name != ".gitkeep"]
            self.assertEqual(extras, [])

    def test_transaction_classification_config(self):
        cfg = json.loads((ROOT / "config/item_classification.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["default_item_class"], "MERCHANDISE")
        self.assertEqual(cfg["exact_codes"]["ADJUST"], "ACCOUNTING_ADJUSTMENT")
        self.assertEqual(cfg["exact_codes"]["TEST001"], "TEST")
        self.assertIn("SHIPPING_SERVICE", cfg["non_merchandise_transaction_item_classes"])


if __name__ == "__main__":
    unittest.main()
