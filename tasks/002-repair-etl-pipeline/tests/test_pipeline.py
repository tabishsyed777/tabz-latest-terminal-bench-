import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from etl.config import load_config
from etl.normalize import normalize_amount
from etl.pipeline import deduplicate, read_rows, summarize
from etl.validation import validate_row

ROOT = Path(__file__).parents[1]


def test_config_has_conversion_and_validation_rules():
    config = load_config(ROOT / "config/pipeline.yaml")
    assert config["deduplication"]["keep"] == "last"
    assert config["conversion"]["usd_to_inr"] == "83"
    assert "GBP" not in config["validation"]["allowed_currencies"]


def test_deduplicate_keeps_last_record():
    rows = [{"id": "A", "value": 1}, {"id": "B", "value": 2}, {"id": "A", "value": 3}]
    assert deduplicate(rows, "id", "last") == [rows[1], rows[2]]
    assert deduplicate(rows, "id", "first") == [rows[0], rows[1]]


def test_invalid_rows_after_deduplication():
    config = load_config(ROOT / "config/pipeline.yaml")
    rows = deduplicate(read_rows(ROOT / "data/sales.csv"), "order_id", "last")
    invalid = [row for row in rows if not validate_row(row, config["validation"])[0]]
    assert len(invalid) == 4


def test_configured_currency_conversion():
    assert normalize_amount("300", "USD", "83") == Decimal("24900.00")


def test_summary_uses_converted_revenue_and_rejection_count(tmp_path):
    config = load_config(ROOT / "config/pipeline.yaml")
    rows = deduplicate(read_rows(ROOT / "data/sales.csv"), "order_id", "last")
    valid = [row for row in rows if validate_row(row, config["validation"])[0]]
    summary = summarize(valid, 4, tmp_path / "summary.json", config)
    assert Decimal(summary["total_revenue"]) == Decimal("75000.75")
    assert summary["valid_rows"] == 6
    assert summary["rejected_rows"] == 4
    assert summary["top_region"] == "West"
    assert summary["generated_at"].endswith("Z")
