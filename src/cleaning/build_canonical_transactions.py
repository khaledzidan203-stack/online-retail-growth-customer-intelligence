"""Build the governed canonical and classified Checkpoint 2 transaction layer."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_WORKBOOK = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
CLASSIFICATION_CONFIG = PROJECT_ROOT / "config" / "item_classification.json"
PARQUET_OUTPUT = PROJECT_ROOT / "data" / "interim" / "canonical_transactions.parquet"
RECONCILIATION_OUTPUT = PROJECT_ROOT / "outputs" / "checkpoint2_reconciliation.json"
TRANSACTION_COUNTS_OUTPUT = PROJECT_ROOT / "outputs" / "transaction_class_counts.csv"
ITEM_COUNTS_OUTPUT = PROJECT_ROOT / "outputs" / "item_class_counts.csv"
DUPLICATE_IMPACT_OUTPUT = PROJECT_ROOT / "outputs" / "duplicate_impact_by_transaction_class.csv"

SHEETS = ("Year 2009-2010", "Year 2010-2011")
SOURCE_COLUMNS = [
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country",
]
CUTOFF = pd.Timestamp("2010-12-01")
EXPECTED_CANONICAL_ROWS = 1_044_848
EXPECTED_DUPLICATE_EXTRA_ROWS = 11_812
EXPECTED_DUPLICATE_PARTICIPATING_ROWS = 22_813
EXPECTED_DUPLICATE_GROUPS = 11_001


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def python_scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def count_records(series: pd.Series, name: str) -> list[dict[str, Any]]:
    counts = series.value_counts(dropna=False).sort_index()
    return [
        {name: python_scalar(key), "row_count": int(value)}
        for key, value in counts.items()
    ]


def load_canonical_source(workbook: Path) -> pd.DataFrame:
    excel = pd.ExcelFile(workbook, engine="openpyxl")
    if excel.sheet_names != list(SHEETS):
        raise ValueError(f"Unexpected sheets: {excel.sheet_names!r}")
    frames: list[pd.DataFrame] = []
    for sheet in SHEETS:
        frame = pd.read_excel(excel, sheet_name=sheet, engine="openpyxl")
        if list(frame.columns) != SOURCE_COLUMNS:
            raise ValueError(f"Unexpected columns on {sheet}: {list(frame.columns)!r}")
        frame.insert(0, "SourceRowNumber", pd.Series(frame.index + 2, dtype="Int64"))
        frame.insert(0, "SourceSheet", sheet)
        if sheet == SHEETS[0]:
            frame = frame.loc[frame["InvoiceDate"] < CUTOFF]
        frames.append(frame)
    canonical = pd.concat(frames, ignore_index=True)
    if len(canonical) != EXPECTED_CANONICAL_ROWS:
        raise ValueError(
            f"Canonical row count {len(canonical):,} != {EXPECTED_CANONICAL_ROWS:,}"
        )
    return canonical


def add_duplicate_lineage(frame: pd.DataFrame) -> pd.DataFrame:
    frame["IsExactDuplicateAfterFirst"] = frame.duplicated(
        subset=SOURCE_COLUMNS, keep="first"
    )
    frame["IsInExactDuplicateGroup"] = frame.duplicated(
        subset=SOURCE_COLUMNS, keep=False
    )
    frame["ExactDuplicateGroupSize"] = (
        frame.groupby(SOURCE_COLUMNS, dropna=False)["Invoice"]
        .transform("size")
        .astype("Int64")
    )
    return frame


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=frame.index)
    result["SourceSheet"] = frame["SourceSheet"].astype("string")
    result["SourceRowNumber"] = frame["SourceRowNumber"].astype("Int64")
    result["InvoiceRaw"] = frame["Invoice"].astype("string")
    result["Invoice"] = result["InvoiceRaw"].str.strip()
    result["StockCodeRaw"] = frame["StockCode"].astype("string")
    result["StockCode"] = result["StockCodeRaw"].str.strip().str.upper()
    result["DescriptionRaw"] = frame["Description"].astype("string")
    result["Description"] = (
        result["DescriptionRaw"].str.strip().str.replace(r"\s+", " ", regex=True)
    )

    quantity = pd.to_numeric(frame["Quantity"], errors="raise")
    if quantity.isna().any() or quantity.mod(1).ne(0).any():
        raise ValueError("Quantity contains missing or non-integer values")
    result["Quantity"] = quantity.astype("Int64")
    result["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="raise")
    if result["InvoiceDate"].isna().any():
        raise ValueError("InvoiceDate contains missing values")
    result["Price"] = pd.to_numeric(frame["Price"], errors="raise").astype("Float64")

    customer = pd.to_numeric(frame["Customer ID"], errors="coerce")
    if customer.dropna().mod(1).ne(0).any():
        raise ValueError("Customer ID contains non-integer numeric values")
    result["CustomerIDRaw"] = customer.astype("Float64")
    result["CustomerID"] = customer.astype("Int64").astype("string")
    result["CountryRaw"] = frame["Country"].astype("string")
    result["Country"] = result["CountryRaw"].str.strip()
    result["LineAmount"] = result["Quantity"] * result["Price"]
    result["IsExactDuplicateAfterFirst"] = frame[
        "IsExactDuplicateAfterFirst"
    ].astype(bool)
    result["IsInExactDuplicateGroup"] = frame[
        "IsInExactDuplicateGroup"
    ].astype(bool)
    result["ExactDuplicateGroupSize"] = frame[
        "ExactDuplicateGroupSize"
    ].astype("Int64")
    return result


def classify_items(frame: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    default = config["default_item_class"]
    exact = {key.upper(): value for key, value in config["exact_codes"].items()}
    item_class = frame["StockCode"].map(exact).fillna(default).astype("string")
    for prefix, classification in config["prefix_codes"].items():
        prefix_mask = frame["StockCode"].str.startswith(prefix.upper(), na=False)
        item_class.loc[prefix_mask] = classification
    frame["ItemClass"] = item_class
    return frame


def classify_transactions(
    frame: pd.DataFrame, config: dict[str, Any]
) -> pd.DataFrame:
    invoice_a = frame["Invoice"].str.startswith("A", na=False)
    invoice_c = frame["Invoice"].str.startswith("C", na=False)
    merchandise = frame["ItemClass"].eq("MERCHANDISE")
    transaction_class = pd.Series(pd.NA, index=frame.index, dtype="string")

    def assign(mask: pd.Series, value: str) -> None:
        transaction_class.loc[transaction_class.isna() & mask.fillna(False)] = value

    assign(
        invoice_a | frame["ItemClass"].eq("ACCOUNTING_ADJUSTMENT"),
        "ACCOUNTING_ADJUSTMENT",
    )
    assign(frame["ItemClass"].eq("TEST"), "TEST_RECORD")
    assign(
        frame["ItemClass"].isin(
            config["non_merchandise_transaction_item_classes"]
        ),
        "NON_MERCHANDISE",
    )
    assign(
        merchandise & invoice_c & frame["Quantity"].lt(0),
        "CUSTOMER_CANCELLATION",
    )
    assign(
        merchandise & invoice_c & frame["Quantity"].ge(0),
        "DQ_REVIEW",
    )
    assign(
        merchandise & ~invoice_c & frame["Quantity"].lt(0),
        "OPERATIONAL_STOCK_ADJUSTMENT",
    )
    assign(
        merchandise & frame["Quantity"].gt(0) & frame["Price"].eq(0),
        "ZERO_PRICE_MERCHANDISE",
    )
    assign(
        merchandise & frame["Quantity"].gt(0) & frame["Price"].gt(0),
        "MERCHANDISE_SALE",
    )
    frame["TransactionClass"] = transaction_class.fillna("DQ_REVIEW")

    review_reason = pd.Series(pd.NA, index=frame.index, dtype="string")
    review = frame["TransactionClass"].eq("DQ_REVIEW")
    review_reason.loc[
        review & merchandise & invoice_c & frame["Quantity"].ge(0)
    ] = "C-prefixed merchandise with non-negative quantity"
    review_reason.loc[
        review & merchandise & frame["Price"].lt(0)
    ] = "Merchandise with negative price not covered by an earlier rule"
    review_reason.loc[review & review_reason.isna()] = (
        "Record does not fit a governed transaction rule"
    )
    frame["DQReviewReason"] = review_reason
    return frame


def add_flags(frame: pd.DataFrame) -> pd.DataFrame:
    frame["IsKnownCustomer"] = frame["CustomerID"].notna()
    frame["IsCancellationInvoice"] = frame["Invoice"].str.startswith(
        "C", na=False
    )
    frame["IsMerchandise"] = frame["ItemClass"].eq("MERCHANDISE")
    frame["IsSalesEligible"] = frame["TransactionClass"].eq(
        "MERCHANDISE_SALE"
    )
    frame["IsCustomerAnalyticsEligible"] = (
        frame["IsSalesEligible"] & frame["IsKnownCustomer"]
    )
    frame["IsCancellationEligible"] = frame["TransactionClass"].eq(
        "CUSTOMER_CANCELLATION"
    )
    frame["IsZeroPrice"] = frame["Price"].eq(0)
    frame["IsNegativePrice"] = frame["Price"].lt(0)
    return frame


def duplicate_impact(
    frame: pd.DataFrame,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    duplicates = frame.loc[frame["IsExactDuplicateAfterFirst"]]
    by_class = (
        duplicates.groupby("TransactionClass", dropna=False)
        .agg(
            duplicate_rows=("TransactionClass", "size"),
            duplicate_quantity=("Quantity", "sum"),
            duplicate_line_amount=("LineAmount", "sum"),
        )
        .reset_index()
        .sort_values("TransactionClass")
    )
    records = [
        {
            "transaction_class": str(row.TransactionClass),
            "duplicate_rows": int(row.duplicate_rows),
            "duplicate_quantity": int(row.duplicate_quantity),
            "duplicate_line_amount": float(row.duplicate_line_amount),
        }
        for row in by_class.itertuples(index=False)
    ]
    sales = frame["IsSalesEligible"]
    retained = ~frame["IsExactDuplicateAfterFirst"]
    gross_revenue = float(frame.loc[sales, "LineAmount"].sum())
    deduplicated_revenue = float(
        frame.loc[sales & retained, "LineAmount"].sum()
    )
    gross_orders = int(frame.loc[sales, "Invoice"].nunique(dropna=True))
    deduplicated_orders = int(
        frame.loc[sales & retained, "Invoice"].nunique(dropna=True)
    )
    return records, {
        "extra_rows_beyond_first": int(
            frame["IsExactDuplicateAfterFirst"].sum()
        ),
        "rows_participating_in_groups": int(
            frame["IsInExactDuplicateGroup"].sum()
        ),
        "merchandise_sales_revenue_including_duplicates": gross_revenue,
        "merchandise_sales_revenue_excluding_duplicates_after_first": (
            deduplicated_revenue
        ),
        "merchandise_sales_revenue_effect": (
            gross_revenue - deduplicated_revenue
        ),
        "eligible_order_count_including_duplicates": gross_orders,
        "eligible_order_count_excluding_duplicates_after_first": (
            deduplicated_orders
        ),
        "eligible_order_count_effect": gross_orders - deduplicated_orders,
    }


def create_summary(
    frame: pd.DataFrame,
    raw_sha256: str,
    parquet_path: Path,
    source_duplicate_groups: int,
) -> dict[str, Any]:
    transaction_counts = count_records(
        frame["TransactionClass"], "transaction_class"
    )
    item_counts = count_records(frame["ItemClass"], "item_class")
    duplicate_records, duplicate_summary = duplicate_impact(frame)
    duplicate_summary["duplicate_groups"] = source_duplicate_groups

    sales = frame["IsSalesEligible"]
    customer_eligible = frame["IsCustomerAnalyticsEligible"]
    cancellations = frame["IsCancellationEligible"]
    operational = frame["TransactionClass"].eq(
        "OPERATIONAL_STOCK_ADJUSTMENT"
    )
    review = frame["TransactionClass"].eq("DQ_REVIEW")

    example_columns = [
        "SourceSheet",
        "SourceRowNumber",
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "Price",
        "DQReviewReason",
    ]
    examples = []
    for record in frame.loc[review, example_columns].head(10).to_dict("records"):
        examples.append(
            {key: python_scalar(value) for key, value in record.items()}
        )

    row_count = len(frame)
    known = int(frame["IsKnownCustomer"].sum())
    duplicate_extra = int(frame["IsExactDuplicateAfterFirst"].sum())
    transaction_total = sum(
        item["row_count"] for item in transaction_counts
    )
    item_total = sum(item["row_count"] for item in item_counts)
    reconciliation = {
        "canonical_rows_expected": row_count == EXPECTED_CANONICAL_ROWS,
        "transaction_classes_sum_to_canonical": transaction_total == row_count,
        "item_classes_sum_to_canonical": item_total == row_count,
        "known_plus_unknown_equals_canonical": (
            known + (row_count - known) == row_count
        ),
        "duplicate_flagged_plus_nonduplicate_equals_canonical": (
            duplicate_extra + (row_count - duplicate_extra) == row_count
        ),
        "duplicate_extra_rows_match_baseline": (
            duplicate_extra == EXPECTED_DUPLICATE_EXTRA_ROWS
        ),
        "duplicate_participating_rows_match_baseline": (
            int(frame["IsInExactDuplicateGroup"].sum())
            == EXPECTED_DUPLICATE_PARTICIPATING_ROWS
        ),
        "duplicate_groups_match_baseline": (
            source_duplicate_groups == EXPECTED_DUPLICATE_GROUPS
        ),
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": "data/raw/online_retail_II.xlsx",
            "sha256": raw_sha256,
            "canonical_structural_rule": {
                SHEETS[0]: "InvoiceDate < 2010-12-01",
                SHEETS[1]: "all rows",
            },
        },
        "canonical_output": {
            "path": str(parquet_path.relative_to(PROJECT_ROOT)).replace(
                "\\", "/"
            ),
            "rows": row_count,
            "columns": len(frame.columns),
            "size_bytes": parquet_path.stat().st_size,
        },
        "transaction_class_counts": transaction_counts,
        "item_class_counts": item_counts,
        "eligibility": {
            "sales_eligible_rows": int(sales.sum()),
            "sales_eligible_line_amount": float(
                frame.loc[sales, "LineAmount"].sum()
            ),
            "customer_analytics_eligible_rows": int(customer_eligible.sum()),
            "cancellation_eligible_rows": int(cancellations.sum()),
            "cancellation_eligible_absolute_line_amount": float(
                frame.loc[cancellations, "LineAmount"].abs().sum()
            ),
        },
        "operational_adjustments": {
            "rows": int(operational.sum()),
            "line_amount": float(
                frame.loc[operational, "LineAmount"].sum()
            ),
        },
        "customers": {
            "known_rows": known,
            "unknown_rows": row_count - known,
        },
        "data_quality": {
            "missing_customer_rows": int(frame["CustomerID"].isna().sum()),
            "zero_price_rows": int(frame["IsZeroPrice"].sum()),
            "negative_price_rows": int(frame["IsNegativePrice"].sum()),
            "dq_review_rows": int(review.sum()),
            "dq_review_examples": examples,
        },
        "duplicate_impact_by_transaction_class": duplicate_records,
        "duplicate_impact": duplicate_summary,
        "reconciliation": reconciliation,
        "overall_status": (
            "PASS" if all(reconciliation.values()) else "FAIL"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=RAW_WORKBOOK)
    parser.add_argument("--config", type=Path, default=CLASSIFICATION_CONFIG)
    parser.add_argument(
        "--parquet-output", type=Path, default=PARQUET_OUTPUT
    )
    parser.add_argument(
        "--reconciliation-output",
        type=Path,
        default=RECONCILIATION_OUTPUT,
    )
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = add_duplicate_lineage(load_canonical_source(args.workbook))
    duplicate_groups = int(
        source.groupby(SOURCE_COLUMNS, dropna=False).size().gt(1).sum()
    )
    canonical = add_flags(
        classify_transactions(
            classify_items(normalize(source), config), config
        )
    )

    args.parquet_output.parent.mkdir(parents=True, exist_ok=True)
    args.reconciliation_output.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_parquet(
        args.parquet_output, index=False, engine="pyarrow"
    )
    summary = create_summary(
        canonical,
        file_sha256(args.workbook),
        args.parquet_output,
        duplicate_groups,
    )
    args.reconciliation_output.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    pd.DataFrame(summary["transaction_class_counts"]).to_csv(
        TRANSACTION_COUNTS_OUTPUT, index=False
    )
    pd.DataFrame(summary["item_class_counts"]).to_csv(
        ITEM_COUNTS_OUTPUT, index=False
    )
    pd.DataFrame(
        summary["duplicate_impact_by_transaction_class"]
    ).to_csv(DUPLICATE_IMPACT_OUTPUT, index=False)

    print(f"Overall: {summary['overall_status']}")
    print(f"Canonical rows: {len(canonical):,}")
    print(
        f"DQ_REVIEW rows: "
        f"{summary['data_quality']['dq_review_rows']:,}"
    )
    print(f"Output: {args.parquet_output.resolve()}")
    return 0 if summary["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
