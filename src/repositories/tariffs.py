"""Database operations for course tariffs."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.tariff import Tariff


class TariffRepository:
    """Read course tariffs from the database."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Tariff]:
        """Return the available tariffs in a stable order."""
        return list(self.session.scalars(select(Tariff).order_by(Tariff.id)))

    def get(self, tariff_id: int) -> Tariff | None:
        """Find a tariff by its stable identifier."""
        return self.session.get(Tariff, tariff_id)
