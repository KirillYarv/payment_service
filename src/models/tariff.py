"""Tariff persistence model."""

from sqlalchemy import BigInteger, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.types import TrimmedChar


class Tariff(Base):
    """A course price in kopecks."""

    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(TrimmedChar(20), nullable=False, unique=True)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
