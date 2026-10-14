"""Payment persistence model."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Payment(Base):
    """A payment and its optional installment schedule in kopecks."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    tariff_id: Mapped[str] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    installment_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    schedule: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
