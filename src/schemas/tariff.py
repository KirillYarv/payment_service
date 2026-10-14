"""Public tariff representation."""

from pydantic import BaseModel, ConfigDict


class TariffResponse(BaseModel):
    """A tariff returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    price: int
