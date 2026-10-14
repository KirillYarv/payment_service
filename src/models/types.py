"""SQLAlchemy column types for the PostgreSQL models."""

from sqlalchemy import CHAR
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class TrimmedChar(TypeDecorator[str]):
    """Read CHAR(n) values without PostgreSQL's trailing padding."""

    impl = CHAR
    cache_ok = True

    def __init__(self, length: int) -> None:
        super().__init__(length=length)

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        """Remove padding on read, leaving NULL values unchanged."""
        return value.rstrip() if value is not None else None
