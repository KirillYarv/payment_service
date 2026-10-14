"""Tariff prices and payment rules (all monetary values are kopecks)."""

from typing import Final

TARIFF_PRICES: Final[dict[str, int]] = {
    "basic": 990_000,
    "standard": 1_990_000,
    "premium": 2_990_000,
}
PROMO_CODE: Final[str] = "KVITTO10"
DISCOUNT_PERCENT: Final[int] = 10
ALLOWED_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "pending": frozenset({"succeeded", "failed"}),
    "succeeded": frozenset({"refunded"}),
    "failed": frozenset(),
    "refunded": frozenset(),
}
