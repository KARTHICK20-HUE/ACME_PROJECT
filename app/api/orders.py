from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.pagination import PageParam, PageSizeParam, paginate
from app.db import DbSession
from app.models import Order
from app.schemas import OrderOut, OrderStatus, OrderStatusUpdate, Page

router = APIRouter(prefix="/orders", tags=["orders"])

ALLOWED_TRANSITIONS = {
    "placed": {"shipped"},
    "shipped": {"delivered"},
    "delivered": {"returned"},
    "returned": {"refunded"},
    "refunded": set(),
}


def get_order_or_404(db: DbSession, order_id: str) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("", response_model=Page[OrderOut])
def list_orders(
    page: PageParam = 1,
    page_size: PageSizeParam = 20,
    db: DbSession = None,
):
    stmt = select(Order).order_by(Order.created_at.desc(), Order.id.desc())
    return paginate(db, stmt, page, page_size)


@router.get("/search", response_model=Page[OrderOut])
def search_orders(
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: PageParam = 1,
    page_size: PageSizeParam = 20,
    db: DbSession = None,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=422, detail="date_from must be on or before date_to"
        )

    stmt = select(Order)
    if status is not None:
        stmt = stmt.where(Order.status == status)
    if customer_id is not None:
        stmt = stmt.where(Order.customer_id == customer_id)
    if date_from is not None:
        stmt = stmt.where(Order.created_at >= datetime.combine(date_from, time.min))
    if date_to is not None:
        stmt = stmt.where(Order.created_at <= datetime.combine(date_to, time.max))

    stmt = stmt.order_by(Order.created_at.desc(), Order.id.desc())
    return paginate(db, stmt, page, page_size)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: DbSession = None):
    return get_order_or_404(db, order_id)


@router.patch("/{order_id}/status", response_model=OrderOut)
def change_order_status(order_id: str, update: OrderStatusUpdate, db: DbSession = None):
    order = get_order_or_404(db, order_id)
    new_status = update.status
    current_status = order.status

    allowed_next = ALLOWED_TRANSITIONS.get(current_status, set())
    if current_status == new_status or new_status not in allowed_next:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot change status from '{current_status}' to '{new_status}'",
        )

    order.status = new_status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
