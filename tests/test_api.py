"""The required API scenarios from sections 2–4 of the assignment."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.payment import Payment


def payment_payload(tariff_id: int, **overrides: object) -> dict[str, object]:
    """Build a valid card request with optional scenario-specific fields."""
    payload: dict[str, object] = {
        "tariff_id": tariff_id,
        "email": "student@example.com",
        "method": "card",
    }
    payload.update(overrides)
    return payload


def test_tariffs(api: tuple[TestClient, int, Session]) -> None:
    """All three tariffs are returned with prices in integer kopecks."""
    client, _, _ = api
    response = client.get("/tariffs")
    assert response.status_code == 200
    tariffs = response.json()
    assert {row["title"]: row["price"] for row in tariffs} == {
        "basic": 990_000,
        "standard": 1_990_000,
        "premium": 2_990_000,
    }
    assert all(isinstance(row["id"], int) for row in tariffs)


@pytest.mark.parametrize(
    ("promo_code", "expected_amount", "expected_discount"),
    [
        (None, 1_990_000, 0),
        ("KVITTO10", 1_791_000, 199_000),
        ("kvitto10", 1_791_000, 199_000),
    ],
)
def test_amount_and_promocode(
    api: tuple[TestClient, int, Session],
    promo_code: str | None,
    expected_amount: int,
    expected_discount: int,
) -> None:
    """Discount, case insensitivity and default price preserve every kopeck."""
    client, tariff_id, _ = api
    payload = payment_payload(tariff_id)
    if promo_code is not None:
        payload["promo_code"] = promo_code
    response = client.post("/payments", json=payload)
    assert response.status_code == 201
    payment = response.json()
    assert payment["status"] == "pending"
    assert payment["amount"] == expected_amount
    assert payment["discount"] == expected_discount
    assert payment["amount"] + payment["discount"] == 1_990_000
    assert payment["schedule"] is None


@pytest.mark.parametrize("months", [3, 6, 12])
def test_installment_schedule(api: tuple[TestClient, int, Session], months: int) -> None:
    """Installments sum exactly to the amount; excess goes to the first months."""
    client, tariff_id, _ = api
    response = client.post(
        "/payments",
        json=payment_payload(tariff_id, method="installment", installment_months=months),
    )
    assert response.status_code == 201
    payment = response.json()
    schedule = payment["schedule"]
    assert payment["installment_months"] == months
    assert len(schedule) == months
    assert all(isinstance(value, int) for value in schedule)
    assert sum(schedule) == payment["amount"] == 1_990_000
    assert max(schedule) - min(schedule) <= 1
    assert schedule == sorted(schedule, reverse=True)
    if months == 3:
        assert schedule == [663_334, 663_333, 663_333]


@pytest.mark.parametrize("months", [3, 6, 12])
def test_installment_schedule_with_promocode(
    api: tuple[TestClient, int, Session], months: int
) -> None:
    """Calculate installments from the discounted amount, not the tariff price."""
    client, tariff_id, _ = api
    response = client.post(
        "/payments",
        json=payment_payload(
            tariff_id,
            method="installment",
            installment_months=months,
            promo_code="kvitto10",
        ),
    )
    assert response.status_code == 201
    payment = response.json()
    assert payment["discount"] == 199_000
    assert payment["amount"] == 1_791_000
    assert payment["installment_months"] == months
    assert payment["schedule"] == [1_791_000 // months] * months
    assert sum(payment["schedule"]) == payment["amount"]


def test_idempotency_key(api: tuple[TestClient, int, Session]) -> None:
    """A repeated key returns the original payment instead of inserting another."""
    client, tariff_id, session = api
    headers = {"Idempotency-Key": "same-request"}
    payload = payment_payload(tariff_id)
    first = client.post("/payments", json=payload, headers=headers)
    second = client.post("/payments", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert session.scalar(
        select(func.count()).select_from(Payment).where(Payment.idempotency_key == "same-request")
    ) == 1


def test_forbidden_transition_does_not_change_status(
    api: tuple[TestClient, int, Session],
) -> None:
    """A pending payment cannot be refunded; the stored status stays pending."""
    client, tariff_id, _ = api
    created = client.post("/payments", json=payment_payload(tariff_id))
    assert created.status_code == 201
    payment_id = created.json()["id"]
    webhook = client.post(
        "/webhooks/bank", json={"payment_id": payment_id, "status": "refunded"}
    )
    assert webhook.status_code == 409
    assert webhook.json() == {"error": "invalid_transition"}
    retrieved = client.get(f"/payments/{payment_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["status"] == "pending"


def test_allowed_transitions(api: tuple[TestClient, int, Session]) -> None:
    """The bank can succeed and refund a payment in that order."""
    client, tariff_id, _ = api
    created = client.post("/payments", json=payment_payload(tariff_id))
    payment_id = created.json()["id"]
    for status in ("succeeded", "refunded"):
        response = client.post(
            "/webhooks/bank", json={"payment_id": payment_id, "status": status}
        )
        assert response.status_code == 200
        assert response.json() == {"result": "ok"}
        assert client.get(f"/payments/{payment_id}").json()["status"] == status


def test_missing_payment(api: tuple[TestClient, int, Session]) -> None:
    """Reading an absent payment returns 404."""
    client, _, _ = api
    response = client.get("/payments/999999999")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "changes",
    [
        {"promo_code": "UNKNOWN"},
        {"email": "invalid-email"},
        {"method": "cash"},
        {"method": "installment"},
        {"method": "installment", "installment_months": 4},
    ],
)
def test_invalid_payment_returns_422(
    api: tuple[TestClient, int, Session], changes: dict[str, object]
) -> None:
    """Invalid inputs use the standard FastAPI validation response."""
    client, tariff_id, _ = api
    response = client.post("/payments", json=payment_payload(tariff_id, **changes))
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
