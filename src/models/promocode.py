"""Promotional code stored in PostgreSQL."""

from sqlalchemy import CHAR, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class PromoCode(Base):
    """A case-insensitive code and its percentage discount."""

    __tablename__ = "promocodes"

    name: Mapped[str] = mapped_column(CHAR(50), primary_key=True)
    discount: Mapped[int] = mapped_column(SmallInteger, nullable=False)
