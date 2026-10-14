"""Database operations for course tariffs."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.constants.payments import TARIFF_PRICES
from src.models.tariff import Tariff


class TariffRepository:
    """Read tariffs and insert the fixed catalog on startup."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def seed(self) -> None:
        """Insert missing tariffs without changing existing ones."""
        for title, price in TARIFF_PRICES.items():
            statement = insert(Tariff).values(id=title, title=title, price=price)
            self.session.execute(statement.on_conflict_do_nothing(index_elements=[Tariff.id]))

    def list_all(self) -> list[Tariff]:
        """Return the available tariffs in catalog order."""
        tariffs = self.session.scalars(select(Tariff)).all()
        by_id = {tariff.id: tariff for tariff in tariffs}
        return [by_id[name] for name in TARIFF_PRICES if name in by_id]

    def get(self, tariff_id: str) -> Tariff | None:
        """Find a tariff by its stable identifier."""
        return self.session.get(Tariff, tariff_id)
