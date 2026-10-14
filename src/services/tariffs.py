"""Tariff use cases."""

from src.models.tariff import Tariff
from src.repositories.tariffs import TariffRepository


class TariffService:
    """Expose the fixed tariff catalog."""

    def __init__(self, repository: TariffRepository) -> None:
        self.repository = repository

    def list_tariffs(self) -> list[Tariff]:
        """Return seeded tariffs."""
        return self.repository.list_all()
