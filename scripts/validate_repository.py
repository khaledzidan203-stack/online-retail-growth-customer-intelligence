from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


PROTECTED_CORE = {
    "config/item_classification.json": "a93ceba895ff6b84bd532098d41d471d9eae6ae7",
    "src/cleaning/build_canonical_transactions.py": "cf070ef8fa9665e6b37c9dcd04904513ff2736c9",
    "src/exports/management_export.py": "2cc78afcebea9276a96efa3f361bba10dab94342",
    "sql/analytics/040_create_fact_transaction.sql": "e5f74f7368ae7a43ff1226c3f35a9a95b75a2225",
    "sql/analytics/250_create_customer_analytics.sql": "ffa575148b8bdfdad701f8c7d7f3f8b9ec5ab75e",
    "powerbi/OnlineRetailAnalytics.pbip": "390135d5cbb6edabb4033b04dd94275e95c9cf3b",
    "powerbi/OnlineRetailAnalytics.SemanticModel/definition/relationships.tmdl": "782c6d5ced955bc4270ac25bdf134d862103a346",
    "powerbi/OnlineRetailAnalytics.SemanticModel/definition/tables/_Measures.tmdl": "b4e86a2e23f0c0785c5da5ea8d2ea3a32c26d5e1",
    "outputs/management/Online_Retail_Management_Analytics.xlsx": "73e04679590efe919cedc25ee5159122d720a249",
    "outputs/management/Online_Retail_Analytical_Detail.xlsx": "12cc0b208ed878bec2f2b4198c6a178756238e08",
    "outputs/management/management_export_validation.json": "f9e4c5609dd58334616ea69bf8e9d22062723a34",
    "screenshots/02_executive_overview.png": "9e0c61cef004b1452a3a1b7d2be019d965f5f52a",
}

REQUIRED = [
    "README.md",
    "PROJECT_NOTES.md",
    "docs/README.md",
    "docs/PROJECT_INDEX.md",
    "docs/CASE_STUDY.md",
    "docs/TECHNICAL_WALKTHROUGH.md",
    "docs/PROJECT_EVIDENCE_MAP.md",
    "docs/FINAL_RELEASE_VALIDATION.md",
    "docs/ENVIRONMENT_BASELINE.md",
    "docs/PROJECT_INVENTORY.md",
    "docs/assets/README.md",
    "docs/validation.md",
    "powerbi/OnlineRetailAnalytics.pbip",
    "outputs/management/management_export_validation.json",
    "screenshots/02_executive_overview.png",
]


def validate_required_files() -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            fail(f"Missing required artifact: {rel}")
    if (ROOT / "docs" / "PORTFOLIO_INVENTORY.md").exists():
        fail("Old portfolio inventory file must be removed.")


def validate_protected_core() -> None:
    for rel, expected in PROTECTED_CORE.items():
        path = ROOT / rel
        if not path.is_file():
            fail(f"Missing protected artifact: {rel}")
            continue
        actual = git_blob_sha(path)
        if actual != expected:
            fail(f"Protected analytical artifact changed: {rel}")


def validate_management_evidence() -> None:
    path = ROOT / "outputs" / "management" / "management_export_validation.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("status") != "PASS":
        fail("Management validation status is not PASS.")
    if data.get("sql_validation") != "PASS":
        fail("Retained SQL validation status is not PASS.")
    if data.get("reference_reconciliation") != "PASS":
        fail("Retained reference reconciliation status is not PASS.")

    expected = {
        "SalesRevenue": ("19701685.50700000", "19701685.507"),
        "UnitsSold": ("11221960", "11221960"),
        "Orders": ("39519", "39519"),
        "SalesCustomers": ("5852", "5852"),
        "CancellationValue": ("719692.94000000", "719692.94"),
        "CancellationValueRate": ("0.03524213323149723028097017079", "0.035242"),
        "AnonymousSalesRevenue": ("2576013.46000000", "2576013.46"),
        "OperationalAdjustmentRows": ("3392", "3392"),
        "CanonicalTransactionRows": ("1044848", "1044848"),
    }
    refs = data.get("references", {})
    for key, (actual, reference) in expected.items():
        item = refs.get(key)
        if not item:
            fail(f"Missing retained reference: {key}")
            continue
        if item.get("actual") != actual or item.get("reference") != reference:
            fail(f"Retained reference changed for {key}: {item}")

    workbooks = data.get("workbooks", {})
    expected_books = {
        "Online_Retail_Management_Analytics.xlsx": (14, 82847),
        "Online_Retail_Analytical_Detail.xlsx": (16, 433816),
    }
    for name, (sheets, cells) in expected_books.items():
        item = workbooks.get(name)
        if not item:
            fail(f"Missing workbook validation evidence: {name}")
            continue
        if item.get("sheets") != sheets:
            fail(f"Workbook sheet baseline changed for {name}")
        if item.get("validated_cells") != cells:
            fail(f"Workbook validated-cell baseline changed for {name}")


def workbook_sheet_count(path: Path) -> int:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("xl/workbook.xml"))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return len(root.findall(".//m:sheets/m:sheet", ns))


def validate_workbook_packages() -> None:
    expected = {
        "Online_Retail_Management_Analytics.xlsx": 14,
        "Online_Retail_Analytical_Detail.xlsx": 16,
    }
    for name, count in expected.items():
        path = ROOT / "outputs" / "management" / name
        if not zipfile.is_zipfile(path):
            fail(f"Workbook is not a valid XLSX ZIP package: {name}")
            continue
        actual = workbook_sheet_count(path)
        if actual != count:
            fail(f"Workbook sheet count changed for {name}: {actual} != {count}")


def validate_powerbi_structure() -> None:
    report = ROOT / "powerbi" / "OnlineRetailAnalytics.Report" / "definition"
    semantic = ROOT / "powerbi" / "OnlineRetailAnalytics.SemanticModel" / "definition"

    page_files = list((report / "pages").glob("*/page.json"))
    visual_files = list((report / "pages").glob("*/visuals/*/visual.json"))
    tmdl_files = list(semantic.rglob("*.tmdl"))

    if len(page_files) != 10:
        fail(f"Expected 10 Power BI pages, found {len(page_files)}")
    if len(visual_files) != 136:
        fail(f"Expected 136 Power BI visuals, found {len(visual_files)}")
    if len(tmdl_files) != 15:
        fail(f"Expected 15 TMDL files, found {len(tmdl_files)}")

    for path in list(report.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"Invalid PBIR JSON: {path.relative_to(ROOT)}: {exc}")

    measures_text = (
        semantic / "tables" / "_Measures.tmdl"
    ).read_text(encoding="utf-8")
    measure_count = len(re.findall(r"^\s*measure\s+", measures_text, re.MULTILINE))
    if measure_count != 50:
        fail(f"Expected 50 explicit DAX measures, found {measure_count}")

    rel_text = (semantic / "relationships.tmdl").read_text(encoding="utf-8")
    relationship_count = len(re.findall(r"^relationship\s+", rel_text, re.MULTILINE))
    if relationship_count != 7:
        fail(f"Expected 7 relationships, found {relationship_count}")


def validate_screenshots() -> None:
    shots = sorted((ROOT / "screenshots").glob("[0-9][0-9]_*.png"))
    if len(shots) != 10:
        fail(f"Expected 10 authentic report screenshots, found {len(shots)}")
    for shot in shots:
        if shot.stat().st_size <= 0:
            fail(f"Empty screenshot: {shot.name}")
        if shot.stat().st_size > 2 * 1024 * 1024:
            fail(f"Unexpectedly oversized screenshot: {shot.name}")


def validate_publication_boundary() -> None:
    for folder in ("raw", "interim", "processed"):
        path = ROOT / "data" / folder
        if path.exists():
            extras = [p for p in path.iterdir() if p.name != ".gitkeep"]
            if extras:
                fail(f"Local data leaked into data/{folder}: {[p.name for p in extras]}")

    forbidden_suffixes = {".mdf", ".ldf", ".bak", ".abf", ".parquet"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in forbidden_suffixes:
            fail(f"Forbidden local/runtime artifact: {path.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "Featured Portfolio",
        "Recruiter",
        "Target Roles",
        "Skills Demonstrated",
    ):
        if phrase in readme:
            fail(f"Recruitment-oriented README wording remains: {phrase}")

    if "screenshots/02_executive_overview.png" not in readme:
        fail("README authentic executive-overview screenshot link missing.")
    if "Historical / retained evidence" not in readme:
        fail("README does not distinguish retained evidence from fresh CI.")


def validate_public_text() -> None:
    patterns = {
        "private_key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
        "secret_assignment": re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[=:]\s*[\"\']?[A-Za-z0-9_\-]{12,}"
        ),
        "private_ipv4": re.compile(
            r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})\b"
        ),
    }
    text_ext = {".md", ".txt", ".py", ".sql", ".json", ".yml", ".yaml", ".tmdl", ".pbip", ".pbir"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in text_ext:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for label, pattern in patterns.items():
                if pattern.search(text):
                    fail(f"{label}: {path.relative_to(ROOT)}")


def main() -> None:
    validate_required_files()
    validate_protected_core()
    validate_management_evidence()
    validate_workbook_packages()
    validate_powerbi_structure()
    validate_screenshots()
    validate_publication_boundary()
    validate_public_text()

    if errors:
        print("REPOSITORY VALIDATION FAILED")
        for item in sorted(set(errors)):
            print("-", item)
        sys.exit(1)

    print("PASS | protected analytical core")
    print("PASS | retained management / SQL reconciliation evidence")
    print("PASS | Power BI source structure: 10 pages / 136 visuals / 50 measures / 7 relationships / 15 TMDL files")
    print("PASS | workbook package structure: 14 + 16 sheets")
    print("PASS | authentic screenshot set: 10")
    print("PASS | publication boundary and public-text scan")
    print("REPOSITORY VALIDATION PASS")


if __name__ == "__main__":
    main()
