"""Bank notification route."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.db import get_session
from src.repositories.payments import PaymentRepository
from src.schemas.payment import BankWebhook, WebhookResponse
from src.services.webhooks import InvalidTransitionError, WebhookService

router = APIRouter()


@router.post("/webhooks/bank", response_model=WebhookResponse)
def bank_webhook(
    request: BankWebhook, session: Annotated[Session, Depends(get_session)]
) -> WebhookResponse | JSONResponse:
    """Apply a valid transition and acknowledge the bank."""
    service = WebhookService(PaymentRepository(session))
    try:
        service.apply(request)
    except InvalidTransitionError:
        return JSONResponse(status_code=409, content={"error": "invalid_transition"})
    return WebhookResponse()
