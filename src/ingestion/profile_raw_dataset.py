"""Reproduce the immutable Online Retail II discovery baseline.

This script profiles the two raw workbook sheets and creates only an in-memory
canonical view. It does not clean, deduplicate, classify, or export row data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKBOOK = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "discovery_baseline.json"
SHEETS = ("Year 2009-2010", "Year 2010-2011")
EXPECTED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]
CUTOFF = pd.Timestamp("2010-12-01")

EXPECTED: dict[str, Any] = {
    "sheet_2009_2010_rows": 525_461,
    "sheet_2010_2011_rows": 541_910,
    "raw_total_rows": 1_067_371,
    "structural_overlap_rows": 22_523,
    "overlap_distinct_invoices": 1_088,
    "canonical_rows": 1_044_848,
    "date_min": "2009-12-01T07:45:00",
    "date_max": "2011-12-09T12:50:00",
    "distinct_invoices": 53_628,
    "distinct_stock_codes": 5_305,
    "trimmed_distinct_stock_codes": 5_304,
    "distinct_descriptions": 5_698,
    "trimmed_distinct_descriptions": 5_655,
    "distinct_customer_ids": 5_942,
    "countries": 43,
    "missing_customer_id": 235_287,
    "missing_description": 4_275,
    "positive_quantity_rows": 1_022_291,
    "negative_quantity_rows": 22_557,
    "zero_quantity_rows": 0,
    "c_prefixed_invoice_rows": 19_165,
    "distinct_c_invoices": 8_292,
    "negative_quantity_without_c_rows": 3_393,
    "positive_price_rows": 1_038_819,
    "zero_price_rows": 6_024,
    "negative_price_rows": 5,
    "exact_repeated_row_occurrences": 11_812,
    "rows_in_exact_duplicate_groups": 22_813,
    "exact_duplicate_groups": 11_001,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar(value: Any) -> Any:
    """Convert pandas/numpy scalar values to JSON-safe Python values."""
    return value.item() if hasattr(value, "item") else value


def validation(actual: Any, expected: Any) -> dict[str, Any]:
    return {
        "actual": scalar(actual),
        "expected": expected,
        "status": "PASS" if scalar(actual) == expected else "FAIL",
    }


def normalized_rows(frame: pd.DataFrame) -> pd.Series:
    """Stable hashes used only to compare exact rows across sheets."""
    return pd.util.hash_pandas_object(frame[EXPECTED_COLUMNS], index=False)


def profile(workbook: Path) -> dict[str, Any]:
    if not workbook.is_file():
        raise FileNotFoundError(f"Raw workbook not found: {workbook}")

    excel = pd.ExcelFile(workbook, engine="openpyxl")
    sheet_names = excel.sheet_names
    if sheet_names != list(SHEETS):
        raise ValueError(f"Unexpected sheets: {sheet_names!r}; expected {list(SHEETS)!r}")

    frames: dict[str, pd.DataFrame] = {}
    column_checks: dict[str, dict[str, Any]] = {}
    for sheet in SHEETS:
        frame = pd.read_excel(excel, sheet_name=sheet, engine="openpyxl")
        frames[sheet] = frame
        column_checks[sheet] = {
            "actual": list(frame.columns),
            "expected": EXPECTED_COLUMNS,
            "status": "PASS" if list(frame.columns) == EXPECTED_COLUMNS else "FAIL",
        }

    first = frames[SHEETS[0]]
    second = frames[SHEETS[1]]
    if any(check["status"] == "FAIL" for check in column_checks.values()):
        raise ValueError("Column validation failed; refusing to calculate misleading metrics")

    first_overlap = first.loc[first["InvoiceDate"] >= CUTOFF]
    second_overlap = second.loc[second["InvoiceDate"] < pd.Timestamp("2010-12-10")]

    # Count the multiset intersection, so repeated identical source rows are
    # compared without turning this into a general duplicate-removal rule.
    first_counts = normalized_rows(first_overlap).value_counts()
    second_counts = normalized_rows(second_overlap).value_counts()
    shared_hashes = first_counts.index.intersection(second_counts.index)
    exact_cross_sheet_overlap = int(
        sum(min(int(first_counts[key]), int(second_counts[key])) for key in shared_hashes)
    )

    canonical = pd.concat(
        [first.loc[first["InvoiceDate"] < CUTOFF], second],
        ignore_index=True,
    )
    invoice_text = canonical["Invoice"].astype("string")
    c_mask = invoice_text.str.startswith("C", na=False)

    metrics: dict[str, Any] = {
        "sheet_2009_2010_rows": len(first),
        "sheet_2010_2011_rows": len(second),
        "raw_total_rows": len(first) + len(second),
        "structural_overlap_rows": len(first_overlap),
        "exact_cross_sheet_overlap_rows": exact_cross_sheet_overlap,
        "overlap_distinct_invoices": first_overlap["Invoice"].nunique(dropna=True),
        "canonical_rows": len(canonical),
        "date_min": canonical["InvoiceDate"].min().isoformat(),
        "date_max": canonical["InvoiceDate"].max().isoformat(),
        "distinct_invoices": canonical["Invoice"].nunique(dropna=True),
        "distinct_stock_codes": canonical["StockCode"].nunique(dropna=True),
        "trimmed_distinct_stock_codes": (
            canonical["StockCode"].astype("string").str.strip().nunique(dropna=True)
        ),
        "distinct_descriptions": canonical["Description"].nunique(dropna=True),
        "trimmed_distinct_descriptions": (
            canonical["Description"].astype("string").str.strip().nunique(dropna=True)
        ),
        "distinct_customer_ids": canonical["Customer ID"].nunique(dropna=True),
        "countries": canonical["Country"].nunique(dropna=True),
        "missing_customer_id": canonical["Customer ID"].isna().sum(),
        "missing_description": canonical["Description"].isna().sum(),
        "positive_quantity_rows": canonical["Quantity"].gt(0).sum(),
        "negative_quantity_rows": canonical["Quantity"].lt(0).sum(),
        "zero_quantity_rows": canonical["Quantity"].eq(0).sum(),
        "c_prefixed_invoice_rows": c_mask.sum(),
        "distinct_c_invoices": canonical.loc[c_mask, "Invoice"].nunique(dropna=True),
        "negative_quantity_without_c_rows": (canonical["Quantity"].lt(0) & ~c_mask).sum(),
        "positive_price_rows": canonical["Price"].gt(0).sum(),
        "zero_price_rows": canonical["Price"].eq(0).sum(),
        "negative_price_rows": canonical["Price"].lt(0).sum(),
        "exact_repeated_row_occurrences": canonical.duplicated(keep="first").sum(),
        "rows_in_exact_duplicate_groups": canonical.duplicated(keep=False).sum(),
        "exact_duplicate_groups": (
            canonical.groupby(EXPECTED_COLUMNS, dropna=False).size().gt(1).sum()
        ),
    }
    metrics = {key: scalar(value) for key, value in metrics.items()}

    validations = {
        key: validation(metrics[key], expected)
        for key, expected in EXPECTED.items()
    }
    validations["exact_cross_sheet_overlap_rows"] = validation(
        metrics["exact_cross_sheet_overlap_rows"], EXPECTED["structural_overlap_rows"]
    )
    validations["columns"] = {
        "actual": column_checks,
        "expected": "Exact expected columns on both sheets",
        "status": "PASS",
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(workbook.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "filename": workbook.name,
            "size_bytes": workbook.stat().st_size,
            "sha256": sha256(workbook),
            "sheet_names": sheet_names,
        },
        "canonical_rule": {
            SHEETS[0]: "InvoiceDate < 2010-12-01",
            SHEETS[1]: "all rows",
            "other_duplicate_removal": False,
        },
        "metrics": metrics,
        "validations": validations,
        "overall_status": (
            "PASS"
            if all(item["status"] == "PASS" for item in validations.values())
            else "FAIL"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = profile(args.workbook.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"Overall: {result['overall_status']}")
    print(f"Workbook SHA-256: {result['source']['sha256']}")
    print(f"Canonical rows: {result['metrics']['canonical_rows']:,}")
    failures = [
        key for key, item in result["validations"].items() if item["status"] != "PASS"
    ]
    print(f"Non-passing validations: {', '.join(failures) if failures else 'none'}")
    print(f"Output: {args.output.resolve()}")
    return 0 if result["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
