"""ASGI entry point for the payment API."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.api.payments import router as payments_router
from src.api.tariffs import router as tariffs_router
from src.api.webhooks import router as webhooks_router
from src.db import session_factory
from src.repositories.tariffs import TariffRepository


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load tariff prices from the database when the application starts."""
    with session_factory() as session:
        app.state.tariff_prices = {
            tariff.id: tariff.price for tariff in TariffRepository(session).list_all()
        }
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(tariffs_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
