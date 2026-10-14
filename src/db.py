"""PostgreSQL connection configuration; schema provisioning is external."""

import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/payment"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
session_factory = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy database models."""


def get_session() -> Iterator[Session]:
    """Provide one transaction per HTTP request."""
    with session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
