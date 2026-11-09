import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / "output/sales_summary.json").read_text())
assert summary["valid_rows"] == 6, summary
assert summary["rejected_rows"] == 4, summary
assert summary["top_region"] == "West", summary
assert summary["total_revenue"] == "75000.75", summary
assert summary["generated_at"].endswith("Z"), summary
datetime.fromisoformat(summary["generated_at"].replace("Z", "+00:00"))

lines = (ROOT / "output/rejected.csv").read_text().strip().splitlines()
assert len(lines) == 5, lines
assert "reason" in lines[0], lines
print("Output validation passed")
