from decimal import Decimal, ROUND_HALF_UP

def normalize_amount(amount, currency):
    value = Decimal(str(amount))
    if currency == "USD":
        value = value * Decimal("83")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
