"""ASGI entry point for the payment API."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.api.payments import router as payments_router
from src.api.tariffs import router as tariffs_router
from src.api.webhooks import router as webhooks_router
from src.db import session_factory
from src.repositories.promocodes import PromoCodeRepository
from src.repositories.tariffs import TariffRepository


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load tariffs and promotional discounts from the existing database."""
    with session_factory() as session:
        app.state.tariff_prices = {
            tariff.id: tariff.price for tariff in TariffRepository(session).list_all()
        }
        promocodes: dict[str, int] = {}
        for promocode in PromoCodeRepository(session).list_all():
            name = promocode.name.strip().upper()
            if not 0 <= promocode.discount <= 100:
                raise ValueError(f"Invalid discount for promocode {name}")
            if name in promocodes:
                raise ValueError(f"Duplicate promocode (case-insensitive): {name}")
            promocodes[name] = promocode.discount
        app.state.promocodes = promocodes
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(tariffs_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
