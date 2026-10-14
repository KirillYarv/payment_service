"""Tariff persistence model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Tariff(Base):
    """A course price in kopecks."""

    __tablename__ = "tariffs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
