#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

files = {
    "src/etl/normalize.py": '''from decimal import Decimal, ROUND_HALF_UP

def normalize_amount(amount, currency, usd_to_inr):
    value = Decimal(str(amount))
    if currency == "USD":
        value *= Decimal(str(usd_to_inr))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
''',
    "src/etl/validation.py": '''from datetime import datetime
from decimal import Decimal, InvalidOperation

def validate_row(row, config):
    for column in config["required_columns"]:
        if not row.get(column):
            return False, f"missing {column}"
    try:
        amount = Decimal(str(row["amount"]))
    except (InvalidOperation, ValueError):
        return False, "invalid amount"
    if amount < Decimal(str(config["min_amount"])) or amount > Decimal(str(config["max_amount"])):
        return False, "amount outside permitted range"
    if row["currency"] not in set(config["allowed_currencies"]):
        return False, "unsupported currency"
    try:
        datetime.fromisoformat(row["occurred_at"].replace("Z", "+00:00"))
    except ValueError:
        return False, "invalid timestamp"
    return True, ""
''',
    "src/etl/pipeline.py": '''import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .normalize import normalize_amount

def read_rows(path, encoding="utf-8"):
    with open(path, newline="", encoding=encoding) as handle:
        return list(csv.DictReader(handle))

def deduplicate(rows, key="order_id", keep="last"):
    if keep not in {"first", "last"}:
        raise ValueError("keep must be 'first' or 'last'")
    selected = {}
    for index, row in enumerate(rows):
        if keep == "last" or row.get(key) not in selected:
            selected[row[key]] = (index, row)
    return [row for _, row in sorted(selected.values(), key=lambda item: item[0])]

def write_rejections(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order_id", "reason"])
        writer.writeheader()
        for row, reason in rows:
            writer.writerow({"order_id": row.get("order_id", ""), "reason": reason})

def summarize(valid_rows, rejected_count, output_path, config):
    rate = config["conversion"]["usd_to_inr"]
    converted = [(row, normalize_amount(row["amount"], row["currency"], rate)) for row in valid_rows]
    revenue = sum((amount for _, amount in converted), start=normalize_amount(0, "INR", rate))
    regions = {}
    for row, amount in converted:
        regions[row["region"]] = regions.get(row["region"], 0) + amount
    top_region = max(regions, key=regions.get) if regions else ""
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    summary = {
        "total_revenue": f"{revenue:.2f}",
        "valid_rows": len(valid_rows),
        "rejected_rows": rejected_count,
        "top_region": top_region,
        "generated_at": generated_at,
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
''',
    "src/etl/cli.py": '''import argparse
from pathlib import Path

from .config import load_config
from .pipeline import deduplicate, read_rows, summarize, write_rejections
from .validation import validate_row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    rows = read_rows(args.input, config["input"]["encoding"])
    dedup = config["deduplication"]
    rows = deduplicate(rows, dedup["key"], dedup["keep"])
    valid, rejected = [], []
    for row in rows:
        ok, reason = validate_row(row, config["validation"])
        (valid if ok else rejected).append(row if ok else (row, reason))

    rejected_path = Path(args.output).parent / config["output"]["rejected_filename"]
    write_rejections(rejected, rejected_path)
    print(summarize(valid, len(rejected), args.output, config))

if __name__ == "__main__":
    main()
''',
}

for name, content in files.items():
    Path("/workspace", name).write_text(content, encoding="utf-8")
PY
