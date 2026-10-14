"""Payment creation and retrieval routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Path, Request, Response
from sqlalchemy.orm import Session

from src.db import get_session
from src.repositories.payments import PaymentRepository
from src.repositories.tariffs import TariffRepository
from src.schemas.payment import CreatePayment, PaymentResponse
from src.services.payments import PaymentService

router = APIRouter()


@router.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(
    payload: CreatePayment,
    response: Response,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    idempotency_key: Annotated[str | None, Header(max_length=255)] = None,
) -> PaymentResponse:
    """Create a payment or return the one associated with the same key."""
    service = PaymentService(
        PaymentRepository(session), TariffRepository(session), request.app.state.promocodes
    )
    payment, created = service.create(payload, idempotency_key)
    if not created:
        response.status_code = 200
    return PaymentResponse.model_validate(payment)


@router.get("/payments/{id}", response_model=PaymentResponse)
def get_payment(
    id: Annotated[int, Path(gt=0)],
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> PaymentResponse:
    """Return one payment by its identifier."""
    service = PaymentService(
        PaymentRepository(session), TariffRepository(session), request.app.state.promocodes
    )
    return PaymentResponse.model_validate(service.get(id))
