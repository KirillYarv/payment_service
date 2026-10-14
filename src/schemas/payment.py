"""Input validation and output contracts for payments."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator, field_validator

from src.constants.payments import PROMO_CODE

PaymentStatus = Literal["pending", "succeeded", "failed", "refunded"]
BankStatus = Literal["succeeded", "failed", "refunded"]
PaymentMethod = Literal["card", "sbp", "installment"]
InstallmentMonths = Literal[3, 6, 12]


class CreatePayment(BaseModel):
    """Valid data for a new payment."""

    tariff_id: str
    email: EmailStr
    method: PaymentMethod
    installment_months: InstallmentMonths | None = None
    promo_code: str | None = None

    @field_validator("promo_code")
    @classmethod
    def validate_promo_code(cls, code: str | None) -> str | None:
        """Reject unknown promotional codes using standard 422 validation."""
        if code is not None and code.upper() != PROMO_CODE:
            raise ValueError("unknown promo_code")
        return code

    @model_validator(mode="after")
    def validate_installment(self) -> "CreatePayment":
        """Require a term only when the installment method is selected."""
        if self.method == "installment" and self.installment_months is None:
            raise ValueError("installment_months is required for installment")
        if self.method != "installment" and self.installment_months is not None:
            raise ValueError("installment_months is only allowed for installment")
        return self


class PaymentResponse(BaseModel):
    """A stored payment returned by create and read operations."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: PaymentStatus
    tariff_id: str
    amount: int
    discount: int
    method: PaymentMethod
    installment_months: InstallmentMonths | None
    schedule: list[int] | None
    email: EmailStr
    created_at: datetime


class BankWebhook(BaseModel):
    """Bank notification about a payment status change."""

    payment_id: int = Field(gt=0)
    status: BankStatus


class WebhookResponse(BaseModel):
    """Successful webhook acknowledgment."""

    result: Literal["ok"] = "ok"
