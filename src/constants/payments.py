"""Payment rules (all monetary values are kopecks)."""

from typing import Final

ALLOWED_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "pending": frozenset({"succeeded", "failed"}),
    "succeeded": frozenset({"refunded"}),
    "failed": frozenset(),
    "refunded": frozenset(),
}
