"""Isolated PostgreSQL-backed HTTP client for the payment API."""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

import main
from src.db import Base, DATABASE_URL, get_session
from src.models import Payment, PromoCode, Tariff  # noqa: F401 - register tables


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    """Create and later remove a dedicated schema within the configured test DB."""
    schema = f"test_{uuid4().hex}"
    admin_engine = create_engine(DATABASE_URL)
    with admin_engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA {schema}"))

    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": f"-csearch_path={schema}"},
    )
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin_engine.dispose()


@pytest.fixture
def api(test_engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, int, Session]]:
    """Run each test in a rollback-only transaction, including HTTP requests."""
    with test_engine.connect() as connection:
        transaction = connection.begin()

        def new_session() -> Session:
            return Session(
                bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
            )

        def override_session() -> Iterator[Session]:
            with new_session() as session:
                try:
                    yield session
                    session.commit()
                except Exception:
                    session.rollback()
                    raise

        try:
            with new_session() as session:
                basic = Tariff(title="basic", price=990_000)
                standard = Tariff(title="standard", price=1_990_000)
                premium = Tariff(title="premium", price=2_990_000)
                session.add_all([basic, standard, premium, PromoCode(name="KVITTO10", discount=10)])
                session.commit()
                standard_id = standard.id

            monkeypatch.setattr(main, "session_factory", new_session)
            main.app.dependency_overrides[get_session] = override_session
            with TestClient(main.app) as client:
                with new_session() as inspection_session:
                    yield client, standard_id, inspection_session
        finally:
            main.app.dependency_overrides.pop(get_session, None)
            transaction.rollback()
