"""Promotional code stored in PostgreSQL."""

from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.types import TrimmedChar


class PromoCode(Base):
    """A case-insensitive code and its percentage discount."""

    __tablename__ = "promocodes"

    name: Mapped[str] = mapped_column(TrimmedChar(50), primary_key=True)
    discount: Mapped[int] = mapped_column(SmallInteger, nullable=False)
