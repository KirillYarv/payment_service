"""Payment rules (all monetary values are kopecks)."""

from typing import Final

PROMO_CODE: Final[str] = "KVITTO10"
DISCOUNT_PERCENT: Final[int] = 10
ALLOWED_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "pending": frozenset({"succeeded", "failed"}),
    "succeeded": frozenset({"refunded"}),
    "failed": frozenset(),
    "refunded": frozenset(),
}
