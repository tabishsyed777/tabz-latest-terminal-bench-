import csv, json
from datetime import datetime, timezone
from pathlib import Path

from .normalize import normalize_amount

def read_rows(path, encoding="utf-8"):
    with open(path, newline="", encoding=encoding) as handle:
        return list(csv.DictReader(handle))

def deduplicate(rows, key="order_id", keep="last"):
    seen = {}
    for row in rows:
        seen.setdefault(row[key], row)
    return list(seen.values())

def write_rejections(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order_id", "reason"])
        writer.writeheader()
        for row, reason in rows:
            writer.writerow({"order_id": row.get("order_id", ""), "reason": reason})

def summarize(valid_rows, output_path):
    revenue = sum(normalize_amount(row["amount"], row["currency"]) for row in valid_rows)
    regions = {}
    for row in valid_rows:
        regions[row["region"]] = regions.get(row["region"], 0) + normalize_amount(row["amount"], row["currency"])
    top_region = max(regions, key=regions.get) if regions else ""
    summary = {"total_revenue": str(revenue), "valid_rows": len(valid_rows), "rejected_rows": 0, "top_region": top_region, "generated_at": datetime.now(timezone.utc).isoformat()}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
