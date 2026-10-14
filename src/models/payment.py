"""Payment persistence model."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, SmallInteger, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.types import TrimmedChar


class Payment(Base):
    """A payment and its optional installment schedule in kopecks."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(TrimmedChar(16), nullable=False, default="pending")
    tariff_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("tariffs.id", ondelete="RESTRICT"), nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    discount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str] = mapped_column(TrimmedChar(16), nullable=False)
    installment_months: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    schedule: Mapped[list[int] | None] = mapped_column(ARRAY(BigInteger), nullable=True)
    email: Mapped[str] = mapped_column(TrimmedChar(320), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        TrimmedChar(255), unique=True, nullable=True
    )
