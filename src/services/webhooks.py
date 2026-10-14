"""Allowed bank status transitions."""

from fastapi import HTTPException

from src.constants.payments import ALLOWED_TRANSITIONS
from src.repositories.payments import PaymentRepository
from src.schemas.payment import BankWebhook


class WebhookService:
    """Apply only permitted status transitions under a row lock."""

    def __init__(self, payments: PaymentRepository) -> None:
        self.payments = payments

    def apply(self, webhook: BankWebhook) -> None:
        """Update the payment or raise 404/409 without changing its status."""
        payment = self.payments.get_for_update(webhook.payment_id)
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        if webhook.status not in ALLOWED_TRANSITIONS[payment.status]:
            raise InvalidTransitionError()
        payment.status = webhook.status


class InvalidTransitionError(Exception):
    """Bank requested a forbidden status change."""
