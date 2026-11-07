from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.customers import router as customers_router
from app.api.orders import router as orders_router
from app.api.tickets import router as tickets_router
from app.db import Base, SessionLocal, engine
from app.seed import load_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        load_seed(db)
    yield


app = FastAPI(title="Acme Support Copilot", version="0.1.0", lifespan=lifespan)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(tickets_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
