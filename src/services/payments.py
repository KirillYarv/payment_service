"""Pricing, installment, and payment creation use cases."""

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

from src.constants.payments import DISCOUNT_PERCENT
from src.models.payment import Payment
from src.repositories.payments import PaymentRepository
from src.repositories.tariffs import TariffRepository
from src.schemas.payment import CreatePayment


def installment_schedule(amount: int, months: int) -> list[int]:
    """Distribute integer kopecks, placing remainders in the first months."""
    base, remainder = divmod(amount, months)
    return [base + int(index < remainder) for index in range(months)]


class PaymentService:
    """Create and retrieve payments without exposing persistence details."""

    def __init__(
        self, payments: PaymentRepository, tariffs: TariffRepository
    ) -> None:
        self.payments = payments
        self.tariffs = tariffs

    def create(self, request: CreatePayment, key: str | None) -> tuple[Payment, bool]:
        """Return (payment, created), reusing a previously used key."""
        if key is not None:
            existing = self.payments.get_by_key(key)
            if existing is not None:
                return existing, False

        tariff = self.tariffs.get(request.tariff_id)
        if tariff is None:
            raise RequestValidationError(
                [{
                    "type": "value_error",
                    "loc": ("body", "tariff_id"),
                    "msg": "Value error, unknown tariff_id",
                    "input": request.tariff_id,
                }]
            )

        discount = tariff.price * DISCOUNT_PERCENT // 100 if request.promo_code else 0
        amount = tariff.price - discount
        months = request.installment_months
        schedule = installment_schedule(amount, months) if months is not None else None
        payment = Payment(
            status="pending",
            tariff_id=tariff.id,
            amount=amount,
            discount=discount,
            method=request.method,
            installment_months=months,
            schedule=schedule,
            email=str(request.email),
            idempotency_key=key,
        )
        return self.payments.create(payment)

    def get(self, payment_id: int) -> Payment:
        """Return a payment or the required 404 error."""
        payment = self.payments.get(payment_id)
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
