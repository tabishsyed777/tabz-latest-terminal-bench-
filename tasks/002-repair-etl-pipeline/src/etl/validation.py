from datetime import datetime
from decimal import Decimal, InvalidOperation

REQUIRED_COLUMNS = ["order_id", "region", "amount", "currency", "occurred_at"]
ALLOWED_CURRENCIES = {"INR", "USD"}
MIN_AMOUNT = Decimal("0")
MAX_AMOUNT = Decimal("1000000")

def validate_row(row):
    for column in REQUIRED_COLUMNS:
        if not row.get(column):
            return False, f"missing {column}"
    try:
        amount = Decimal(str(row["amount"]))
    except (InvalidOperation, ValueError):
        return False, "invalid amount"
    if amount < MIN_AMOUNT or amount > MAX_AMOUNT:
        return False, "amount outside permitted range"
    if row["currency"] not in ALLOWED_CURRENCIES:
        return False, "unsupported currency"
    try:
        datetime.fromisoformat(row["occurred_at"])
    except ValueError:
        return False, "invalid timestamp"
    return True, ""
