from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

OrderStatus = Literal["placed", "shipped", "delivered", "returned", "refunded"]
TicketStatus = Literal["open", "in_progress", "resolved", "closed"]
Priority = Literal["low", "medium", "high"]
Channel = Literal["email", "chat", "whatsapp", "phone"]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    city: str
    state: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: str
    customer_id: int
    product: str
    category: str
    quantity: int
    amount_inr: float
    payment_method: str
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class TicketCreate(BaseModel):
    customer_id: int
    order_id: Optional[str] = None
    subject: Annotated[str, StringConstraints(min_length=3, max_length=200)]
    message: Annotated[str, StringConstraints(min_length=5, max_length=5000)]
    channel: Channel = "email"
    priority: Priority = "medium"


class TicketOut(BaseModel):
    id: int
    customer_id: int
    order_id: Optional[str] = None
    subject: str
    message: str
    channel: Channel
    priority: Priority
    status: TicketStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus
