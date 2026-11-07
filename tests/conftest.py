import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app
from app.seed import load_seed


@pytest.fixture(scope="session")
def seed():
    with open(
        Path(__file__).resolve().parent.parent / "data" / "seed.json",
        "r",
        encoding="utf-8",
    ) as fh:
        return json.load(fh)


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with SessionLocal() as db:
        load_seed(db)

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
