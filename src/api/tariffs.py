"""Tariff route."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db import get_session
from src.repositories.tariffs import TariffRepository
from src.schemas.tariff import TariffResponse
from src.services.tariffs import TariffService

router = APIRouter()


@router.get("/tariffs", response_model=list[TariffResponse])
def list_tariffs(session: Annotated[Session, Depends(get_session)]) -> list[TariffResponse]:
    """List the three course tariffs."""
    tariffs = TariffService(TariffRepository(session)).list_tariffs()
    return [TariffResponse.model_validate(tariff) for tariff in tariffs]
