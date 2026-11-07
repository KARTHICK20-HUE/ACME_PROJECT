from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Customer, Order, Ticket
from app.seed import load_seed


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_load_seed_populates_database():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    assert load_seed(db) is True
    assert db.query(Customer).count() == 200
    assert db.query(Order).count() == 1000
    assert db.query(Ticket).count() == 300
    assert load_seed(db) is False
    db.close()
