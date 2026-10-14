"""Database operations for payments and idempotency keys."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.payment import Payment


class PaymentRepository:
    """Persist payments and lock them during status updates."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, payment_id: int) -> Payment | None:
        """Find a payment by identifier."""
        return self.session.get(Payment, payment_id)

    def get_by_key(self, key: str) -> Payment | None:
        """Find the original payment for an idempotency key."""
        return self.session.scalar(select(Payment).where(Payment.idempotency_key == key))

    def create(self, payment: Payment) -> tuple[Payment, bool]:
        """Insert once, returning the existing payment on a competing key insert."""
        try:
            with self.session.begin_nested():
                self.session.add(payment)
                self.session.flush()
        except IntegrityError:
            if payment.idempotency_key is not None:
                existing = self.get_by_key(payment.idempotency_key)
                if existing is not None:
                    return existing, False
            raise
        return payment, True

    def get_for_update(self, payment_id: int) -> Payment | None:
        """Lock one payment row until the transaction completes."""
        return self.session.scalar(
            select(Payment).where(Payment.id == payment_id).with_for_update()
        )
