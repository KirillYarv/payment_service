"""Read promotional codes without modifying their database records."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.promocode import PromoCode


class PromoCodeRepository:
    """Access promotional codes stored in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[PromoCode]:
        """Read all existing promotional codes at application startup."""
        return list(self.session.scalars(select(PromoCode)))
